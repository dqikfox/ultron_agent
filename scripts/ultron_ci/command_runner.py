from __future__ import annotations
import os
import sys
import re
import json
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

import yaml

# Project guardrails & logging
from utils.model_awareness import check_file_context, should_modify_file
from utils.ultron_logger import (
    log_info, log_error, log_ai_decision, log_file_operation
)

ULTRON_BOT = "ultron_ci"
REPO_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = REPO_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

COMMENT_BODY: Optional[str] = None

def _read_github_comment() -> str:
    """Load the triggering comment or empty string for workflow_dispatch."""
    evt_path = os.getenv("GH_EVENT_PATH") or os.getenv("GITHUB_EVENT_PATH")
    if not evt_path or not Path(evt_path).exists():
        return ""
    with open(evt_path, "r", encoding="utf-8") as f:
        evt = json.load(f)
    # issue_comment or pull_request_review_comment
    body = (
        evt.get("comment", {}).get("body") or
        evt.get("inputs", {}).get("body", "")
    )
    return body or ""


def _extract_yaml_block(body: str) -> Optional[str]:
    m = re.search(r"(?s)/ultron\s+\w+\s+```(?:yaml|yml)\s+(.*?)\s+```", body)
    if m:
        return m.group(1).strip()
    # also support inline compact YAML after the command
    m2 = re.search(r"(?s)/ultron\s+\w+\s+(.*)", body)
    return m2.group(1).strip() if m2 else None

def _git(*args: str) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
    return res.stdout.strip()


def _commit_and_create_pr(branch_name: str, title: str, body: str) -> str:
    _git("checkout", "-B", branch_name)
    _git("add", "-A")
    _git("commit", "-m", title, "--no-verify")
    _git("push", "--set-upstream", "origin", branch_name, "--force")
    pr_url = _git("ls-remote", "--get-url")
    # not ideal; below, use gh cli if available
    try:
        # Prefer gh if present for nice UX
        subprocess.run(
            ["gh", "pr", "create", "--fill", "--title", title, "--body", body],
            cwd=REPO_ROOT,
            check=True
        )
        pr_link = subprocess.run(
            ["gh", "pr", "view", "--json", "url", "-q", ".url"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        return pr_link.stdout.strip() or "PR created."
    except Exception:
        return "PR created (gh not available). Please check repository PRs."


def _replace_with_context(file_path: Path, before: str, after: str) -> Tuple[bool, str]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    if before not in text:
        return False, "context_not_found"
    new_text = text.replace(before, after, 1)
    file_path.write_text(new_text, encoding="utf-8")
    return True, "ok"

def _apply_command(cmd: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Supported commands:
      type: replace_with_context | replace_regex
      file: path
      before/after (for replace_with_context)
      pattern/replacement (for replace_regex)
    """
    file_path = REPO_ROOT / cmd["file"]
    if not file_path.exists():
        return False, f"file_not_found: {file_path}"

    # Guardrails: context + policy check
    ctx = check_file_context(str(file_path))
    proceed, reason, _ = should_modify_file(
        str(file_path),
        cmd.get("type", "edit"),
        "ultron_ci"
    )

    log_ai_decision(
        ULTRON_BOT,
        f"considering modification to {file_path}",
        ai_model="ultron_ci",
        confidence_score=0.9
    )

    if not proceed:
        log_ai_decision(
            ULTRON_BOT,
            f"blocked: {reason}",
            ai_model="ultron_ci",
            confidence_score=0.99
        )
        return False, f"blocked_by_model_awareness: {reason}"

    try:
        if cmd["type"] == "replace_with_context":
            ok, msg = _replace_with_context(
                file_path,
                cmd["before"],
                cmd["after"]
            )
        elif cmd["type"] == "replace_regex":
            import re as _re
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            new_text, n = _re.subn(
                cmd["pattern"],
                cmd["replacement"],
                text,
                count=1,
                flags=_re.DOTALL
            )
            if n == 0:
                return False, "pattern_not_found"
            file_path.write_text(new_text, encoding="utf-8")
            ok, msg = True, "ok"
        else:
            return False, f"unsupported_type: {cmd['type']}"

        if ok:
            log_file_operation(
                ULTRON_BOT,
                f"modified {file_path}",
                str(file_path),
                action="edit"
            )
            return True, "ok"
        return False, msg
    except Exception as e:
        log_error(ULTRON_BOT, f"apply_command_failed: {e}")
        return False, f"exception: {e}"


def _run_tests_if_requested(req: Dict[str, Any]) -> Tuple[bool, str]:
    if not req.get("tests", False):
        return True, "skipped"
    try:
        res = subprocess.run(["pytest", "-q"], cwd=REPO_ROOT, text=True, capture_output=True)
        passed = (res.returncode == 0)
        if passed:
            log_info(ULTRON_BOT, "tests_passed")
            return True, res.stdout[-2000:]
        else:
            log_error(ULTRON_BOT, f"tests_failed:\n{res.stdout}\n{res.stderr}")
            return False, (res.stdout + "\n" + res.stderr)[-4000:]
    except Exception as e:
        log_error(ULTRON_BOT, f"pytest_exception: {e}")
        return False, f"pytest_exception: {e}"

def main() -> None:
    body = _read_github_comment()
    if not body and os.getenv("GH_EVENT_NAME") != "workflow_dispatch":
        print("::set-output name=comment::No /ultron command found.")
        return

    # Determine command kind
    m = re.match(r"(?s).*/ultron\s+(\w+)\s*", body or "")
    kind = m.group(1) if m else os.getenv("KIND", "edit")

    yaml_block = _extract_yaml_block(body) or ""
    try:
        req = yaml.safe_load(yaml_block) if yaml_block else {}
        if not isinstance(req, dict):
            req = {}
    except Exception as e:
        req = {}
        log_error(ULTRON_BOT, f"yaml_parse_error: {e}")

    # Normalize command to list (allow batch)
    changes = req.get("changes") or ([{
        "type": req.get("change", {}).get("type", "replace_with_context"),
        "file": req.get("file"),
        "before": req.get("change", {}).get("before"),
        "after": req.get("change", {}).get("after"),
        "pattern": req.get("change", {}).get("pattern"),
        "replacement": req.get("change", {}).get("replacement"),
    }])

    results = []
    for change in changes:
        if not change.get("file"):
            results.append({"ok": False, "reason": "missing_file"})
            continue
        ok, msg = _apply_command(change)
        results.append({"ok": ok, "reason": msg, "file": change["file"]})

    tests_ok, tests_msg = _run_tests_if_requested(req)

    # Prepare branch & PR if any change succeeded
    if any(r["ok"] for r in results):
        branch = f"ultron/ci/{os.getenv('GH_SHA','manual')[:7]}"
        title = req.get("intent", "Ultron CI: edit")
        pr_url = _commit_and_create_pr(branch, title, "Automated edit via /ultron command.")
        feedback = f"✅ Changes applied.\nPR: {pr_url}\nTests: {'PASS' if tests_ok else 'FAIL'}"
    else:
        feedback = "❌ No changes applied.\nReasons:\n" + "\n".join([f"- {r.get('file')}: {r['reason']}" for r in results])

    # Surface short feedback to the workflow step
    safe = feedback.replace("\n", "  \n")
    print(f"::set-output name=comment::{safe}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(ULTRON_BOT, f"fatal_error: {e}")
        print(f"::set-output name=comment::Ultron CI fatal error: {e}")
        sys.exit(1)