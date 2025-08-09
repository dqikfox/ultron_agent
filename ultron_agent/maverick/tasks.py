from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol, Any


@dataclass
class Suggestion:
    id: str
    title: str
    description: str
    severity: str = "info"  # info | low | medium | high | critical
    file: Optional[str] = None
    line: Optional[int] = None
    action: Optional[str] = None  # textual proposed action
    metadata: Optional[dict] = None


class Task(Protocol):
    name: str
    def run(self, repo_root: Path) -> List[Suggestion]: ...
    def apply(self, repo_root: Path, suggestion: Suggestion) -> bool: ...


class TodoFinderTask:
    name = "todo_finder"

    TODO_PATTERN = re.compile(r"#\s*TODO\b", re.IGNORECASE)

    def run(self, repo_root: Path) -> List[Suggestion]:
        suggestions: List[Suggestion] = []
        for root, _, files in os.walk(repo_root):
            for f in files:
                if not f.endswith((".py", ".md", ".txt")):
                    continue
                path = Path(root) / f
                try:
                    with path.open("r", encoding="utf-8", errors="ignore") as fh:
                        for idx, line in enumerate(fh, start=1):
                            if self.TODO_PATTERN.search(line):
                                suggestions.append(
                                    Suggestion(
                                        id=f"todo:{path}:{idx}",
                                        title="Address TODO comment",
                                        description=f"Found TODO in {path} at line {idx}. Consider resolving or tracking as an issue.",
                                        severity="low",
                                        file=str(path),
                                        line=idx,
                                        action="Create a tracking issue or resolve the TODO.",
                                        metadata={"task": self.name},
                                    )
                                )
                except Exception:
                    # ignore unreadable files
                    pass
        return suggestions

    def apply(self, repo_root: Path, suggestion: Suggestion) -> bool:
        # Non-destructive: we don't auto-edit TODOs
        return False


class ImagePathValidatorTask:
    name = "image_path_validator"

    def run(self, repo_root: Path) -> List[Suggestion]:
        suggestions: List[Suggestion] = []
        # Heuristic: check for gui files referencing images under resources/images
        candidates = list(repo_root.glob("**/*.py"))
        for py in candidates:
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "resources/images/" not in text:
                continue

            for m in re.finditer(r'["\'](resources/images/[^"\']+)["\']', text):
                rel = m.group(1)
                abspath = repo_root / rel
                if not abspath.exists():
                    suggestions.append(
                        Suggestion(
                            id=f"missing_image:{py}:{rel}",
                            title="Missing GUI image resource",
                            description=f"{py.name} references '{rel}' but it does not exist. Add the asset or update the path.",
                            severity="medium",
                            file=str(py),
                            action="Add the missing asset under resources/images or update the code path.",
                            metadata={"path": rel, "task": self.name},
                        )
                    )
        return suggestions

    def apply(self, repo_root: Path, suggestion: Suggestion) -> bool:
        # Could auto-create placeholder images in the future
        return False


class RequirementsAuditTask:
    name = "requirements_audit"

    def run(self, repo_root: Path) -> List[Suggestion]:
        suggestions: List[Suggestion] = []
        req = repo_root / "requirements.txt"
        if not req.exists():
            return suggestions

        try:
            lines = [l.strip() for l in req.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        except Exception:
            lines = []

        if not lines:
            return suggestions

        suggestions.append(
            Suggestion(
                id="deps:outdated_check",
                title="Check for outdated dependencies",
                description="Run 'pip list --outdated' and update pinned versions where safe. Consider using pip-tools.",
                severity="low",
                file=str(req),
                action="Evaluate updates with 'pip list --outdated' and update requirements.",
                metadata={"task": self.name, "packages": lines},
            )
        )
        return suggestions

    def apply(self, repo_root: Path, suggestion: Suggestion) -> bool:
        # Non-destructive placeholder for now
        return False


class BanditSecurityTask:
    name = "bandit_security_scan"

    def run(self, repo_root: Path) -> List[Suggestion]:
        # Lightweight placeholder: suggest adding Bandit if missing
        py_files = list(repo_root.glob("**/*.py"))
        if not py_files:
            return []
        cfg = repo_root / "pyproject.toml"
        bandit_mentioned = False
        if cfg.exists():
            try:
                text = cfg.read_text(encoding="utf-8", errors="ignore")
                bandit_mentioned = "bandit" in text
            except Exception:
                pass
        if not bandit_mentioned:
            return [
                Suggestion(
                    id="security:add_bandit",
                    title="Add security scanning (Bandit)",
                    description="Integrate Bandit to scan for common Python security issues. Add to CI.",
                    severity="medium",
                    action="Add Bandit, run 'bandit -r .' and triage findings.",
                    metadata={"task": self.name},
                )
            ]
        return []

    def apply(self, repo_root: Path, suggestion: Suggestion) -> bool:
        return False


DEFAULT_TASKS: List[Task] = [
    TodoFinderTask(),
    ImagePathValidatorTask(),
    RequirementsAuditTask(),
    BanditSecurityTask(),
]