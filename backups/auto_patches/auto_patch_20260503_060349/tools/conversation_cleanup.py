#!/usr/bin/env python3
"""
Conversation log cleanup and analysis utility.

Reads exported ULTRON conversation logs (ChatGPT-style `mapping` structure),
filters noisy system/tool events, deduplicates attachment metadata, and emits
an easy-to-consume flattened view with fatigue markers and summary stats.

The original file is never modified — a cleaned JSON report is written next to
the source file (suffix `_cleaned.json`), along with an optional Markdown
summary.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


NOISE_TOOL_NAMES = {"file_search"}
NOISE_COMMANDS = {"spinner", "context_stuff"}
FATIGUE_KEYWORDS = [
    "i'm tired",
    "im tired",
    "i am tired",
    "need a break",
    "too long",
    "exhausted",
    "fatigued",
]


@dataclass
class MessageRecord:
    role: str
    text: str
    created_at: Optional[float]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_noise(self) -> bool:
        """Determine if this message should be dropped from the cleaned view."""
        if self.text.strip():
            return False

        role = self.role.lower()
        if role == "user":
            return False

        meta = self.metadata or {}
        if role == "system":
            # Empty system bootstrap messages are noise.
            return True

        if role == "tool":
            tool_name = meta.get("name") or meta.get("tool_name")
            command = meta.get("command")
            if tool_name in NOISE_TOOL_NAMES and (not command or command in NOISE_COMMANDS):
                return True
            if command in NOISE_COMMANDS:
                return True

        # Empty assistant messages without attachments are also noise.
        attachments = (meta.get("attachments") or [])
        return not attachments

    def attachments(self) -> List[Dict[str, Any]]:
        attachments = (self.metadata or {}).get("attachments") or []
        deduped: List[Dict[str, Any]] = []
        seen: set = set()

        for item in attachments:
            att_id = item.get("id") or item.get("name") or json.dumps(item, sort_keys=True)
            if att_id in seen:
                continue
            deduped.append(item)
            seen.add(att_id)
        return deduped


def load_conversations(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Unexpected root structure in {path}")
    return data


def flatten_messages(mapping: Dict[str, Any]) -> List[MessageRecord]:
    messages: List[MessageRecord] = []
    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue
        author = (msg.get("author") or {}).get("role") or "unknown"
        content = msg.get("content") or {}
        text = ""
        if content.get("content_type") == "text":
            parts = content.get("parts") or []
            text = " ".join(str(part) for part in parts if part is not None)
        elif content:
            text = f"[{content.get('content_type', 'non-text')}]"
        metadata = msg.get("metadata") or {}
        messages.append(
            MessageRecord(
                role=author,
                text=text.strip(),
                created_at=msg.get("create_time") or msg.get("update_time"),
                metadata=metadata,
            )
        )
    messages.sort(key=lambda m: (m.created_at or 0))
    return messages


def detect_fatigue(messages: Iterable[MessageRecord]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    msg_list = list(messages)
    if len(msg_list) > 350:
        reasons.append(f"{len(msg_list)} messages (>350 threshold)")

    user_texts = [m.text.lower() for m in msg_list if m.role.lower() == "user"]
    for text in user_texts[-5:]:
        for kw in FATIGUE_KEYWORDS:
            if kw in text:
                reasons.append(f"User fatigue keyword detected: {kw}")
                break

    if not reasons:
        return False, []
    return True, reasons


def conversation_topic(title: str) -> str:
    title_lower = title.lower()
    if any(word in title_lower for word in ["deploy", "deployment", "release"]):
        return "deployment"
    if any(word in title_lower for word in ["failure", "timeline", "forensic"]):
        return "incident-response"
    if any(word in title_lower for word in ["world", "creative", "story"]):
        return "creative"
    if any(word in title_lower for word in ["command", "sovereign", "control"]):
        return "control"
    if any(word in title_lower for word in ["scan", "system", "status"]):
        return "diagnostics"
    return "general"


def summarise_conversation(raw_conv: Dict[str, Any]) -> Dict[str, Any]:
    mapping = raw_conv.get("mapping") or {}
    messages = flatten_messages(mapping)
    cleaned: List[MessageRecord] = [m for m in messages if not m.is_noise()]

    total_messages = len(cleaned)
    role_counts = Counter(m.role.lower() for m in cleaned)
    fatigue_flag, fatigue_reasons = detect_fatigue(cleaned)
    attachments: List[Dict[str, Any]] = []
    attachment_names: set = set()
    for msg in cleaned:
        for att in msg.attachments():
            name = att.get("name") or att.get("id")
            if name in attachment_names:
                continue
            attachments.append(att)
            attachment_names.add(name)

    created_at = raw_conv.get("create_time")
    updated_at = raw_conv.get("update_time")

    def fmt(ts: Optional[float]) -> Optional[str]:
        if not ts:
            return None
        try:
            return datetime.fromtimestamp(ts).isoformat()
        except (OverflowError, ValueError):
            return None

    cleaned_messages = [
        {
            "role": msg.role,
            "text": msg.text,
            "created_at": fmt(msg.created_at),
            "attachments": msg.attachments(),
        }
        for msg in cleaned
    ]

    return {
        "title": raw_conv.get("title") or "Untitled Conversation",
        "topic": conversation_topic(raw_conv.get("title", "")),
        "created_at": fmt(created_at),
        "updated_at": fmt(updated_at),
        "message_count": total_messages,
        "role_counts": dict(role_counts),
        "fatigue_flag": fatigue_flag,
        "fatigue_reasons": fatigue_reasons,
        "attachments": attachments,
        "messages": cleaned_messages,
    }


def aggregate_stats(cleaned_convs: List[Dict[str, Any]]) -> Dict[str, Any]:
    message_counts = [conv["message_count"] for conv in cleaned_convs]
    fatigued = [conv for conv in cleaned_convs if conv["fatigue_flag"]]
    attachment_names: Counter = Counter()
    for conv in cleaned_convs:
        for att in conv["attachments"]:
            name = att.get("name") or att.get("id")
            if name:
                attachment_names[name] += 1

    summaries: Dict[str, Any] = {
        "conversation_count": len(cleaned_convs),
        "total_messages": sum(message_counts),
        "average_messages": statistics.mean(message_counts) if message_counts else 0,
        "median_messages": statistics.median(message_counts) if message_counts else 0,
        "fatigued_conversations": len(fatigued),
        "most_common_attachments": attachment_names.most_common(15),
        "topic_breakdown": Counter(conv["topic"] for conv in cleaned_convs),
    }
    return summaries


def write_outputs(source_path: Path, cleaned: List[Dict[str, Any]], stats: Dict[str, Any], make_markdown: bool) -> None:
    output_path = source_path.with_name(f"{source_path.stem}_cleaned.json")
    output_path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")

    if not make_markdown:
        return

    md_path = source_path.with_name(f"{source_path.stem}_cleanup_report.md")
    lines = [
        f"# Conversation Cleanup Report",
        f"*Source:* `{source_path}`",
        "",
        f"- Conversations processed: **{stats['conversation_count']}**",
        f"- Total messages (after cleanup): **{stats['total_messages']}**",
        f"- Average messages per conversation: **{stats['average_messages']:.1f}**",
        f"- Median messages per conversation: **{stats['median_messages']}**",
        f"- Conversations flagged for fatigue: **{stats['fatigued_conversations']}**",
        "",
        "## Topic Breakdown",
    ]
    for topic, count in stats["topic_breakdown"].most_common():
        lines.append(f"- {topic}: {count}")

    lines.extend(["", "## Most Frequent Attachments"])
    for name, count in stats["most_common_attachments"]:
        lines.append(f"- {name}: {count}")

    lines.append("")
    lines.append("## Flagged Conversations")
    for conv in cleaned:
        if not conv["fatigue_flag"]:
            continue
        reasons = "; ".join(conv["fatigue_reasons"]) or "Unspecified"
        lines.append(f"- **{conv['title']}** – {conv['message_count']} messages ({reasons})")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and summarise ULTRON conversation exports.")
    parser.add_argument("path", type=Path, help="Path to conversations.json")
    parser.add_argument("--markdown", action="store_true", help="Also emit a Markdown summary report")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.path.exists():
        raise FileNotFoundError(f"Conversation file not found: {args.path}")

    conversations = load_conversations(args.path)
    cleaned = [summarise_conversation(conv) for conv in conversations]
    stats = aggregate_stats(cleaned)
    write_outputs(args.path, cleaned, stats, args.markdown)
    print(f"Processed {len(cleaned)} conversations.")
    if stats["fatigued_conversations"]:
        print(f"Flagged {stats['fatigued_conversations']} conversations with fatigue indicators.")


if __name__ == "__main__":
    main()
