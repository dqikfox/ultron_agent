#!/usr/bin/env python3
"""
ULTRON Agent - Suggestion Viewer
================================
Interactive viewer for improvement suggestions with filtering and prioritization.

Usage:
    python view_suggestions.py                    # View all suggestions
    python view_suggestions.py --priority high    # Filter by priority
    python view_suggestions.py --category performance  # Filter by category
    python view_suggestions.py --top 10           # Show top 10 only
    python view_suggestions.py --export report.md # Export to markdown
"""

import json
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent
SUGGESTIONS_FILE = PROJECT_ROOT / "metrics" / "suggestions.json"


def load_suggestions() -> List[Dict[str, Any]]:
    """Load suggestions from JSON file"""
    if not SUGGESTIONS_FILE.exists():
        print(f"❌ No suggestions file found at: {SUGGESTIONS_FILE}")
        print("   Run: python self_improvement.py --scan")
        return []

    with open(SUGGESTIONS_FILE, 'r') as f:
        return json.load(f)


def filter_suggestions(suggestions: List[Dict], priority: str = None, category: str = None) -> List[Dict]:
    """Filter suggestions by priority and/or category"""
    filtered = suggestions

    if priority:
        filtered = [s for s in filtered if s.get('priority', '').lower() == priority.lower()]

    if category:
        filtered = [s for s in filtered if s.get('category', '').lower() == category.lower()]

    return filtered


def get_statistics(suggestions: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics about suggestions"""
    priorities = Counter(s.get('priority', 'unknown') for s in suggestions)
    categories = Counter(s.get('category', 'unknown') for s in suggestions)

    return {
        'total': len(suggestions),
        'by_priority': dict(priorities),
        'by_category': dict(categories),
        'avg_confidence': sum(s.get('confidence', 0) for s in suggestions) / len(suggestions) if suggestions else 0
    }


def format_suggestion(s: Dict, index: int = None) -> str:
    """Format a single suggestion for display"""
    priority_colors = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }

    icon = priority_colors.get(s.get('priority', '').lower(), '⚪')
    num = f"{index}. " if index else ""

    output = f"\n{num}{icon} [{s.get('priority', 'UNKNOWN').upper()}] {s.get('module', 'Unknown Module')}\n"
    output += f"   Category: {s.get('category', 'unknown')}\n"
    output += f"   Issue: {s.get('description', 'No description')}\n"
    output += f"   Impact: {s.get('estimated_impact', 'Unknown')}\n"
    output += f"   Action: {s.get('suggested_action', 'No action specified')}\n"
    output += f"   Confidence: {s.get('confidence', 0):.0%}\n"

    return output


def display_suggestions(suggestions: List[Dict], top: int = None):
    """Display suggestions in a formatted manner"""
    if not suggestions:
        print("\n✅ No suggestions found! System is in excellent condition.\n")
        return

    stats = get_statistics(suggestions)

    print("\n" + "="*70)
    print("🤖 ULTRON AGENT - IMPROVEMENT SUGGESTIONS")
    print("="*70)

    print(f"\n📊 STATISTICS:")
    print(f"   Total Suggestions: {stats['total']}")
    print(f"   By Priority:")
    for priority in ['critical', 'high', 'medium', 'low']:
        count = stats['by_priority'].get(priority, 0)
        if count > 0:
            print(f"      {priority.capitalize()}: {count}")

    print(f"\n   By Category:")
    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
        print(f"      {category.capitalize()}: {count}")

    print(f"\n   Average Confidence: {stats['avg_confidence']:.0%}")

    print("\n" + "-"*70)

    # Sort by priority and confidence
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_suggestions = sorted(
        suggestions,
        key=lambda s: (priority_order.get(s.get('priority', 'low').lower(), 4), -s.get('confidence', 0))
    )

    # Limit to top N if specified
    if top:
        sorted_suggestions = sorted_suggestions[:top]
        print(f"\n📋 TOP {top} SUGGESTIONS:\n")
    else:
        print(f"\n📋 ALL SUGGESTIONS ({len(sorted_suggestions)}):\n")

    for i, suggestion in enumerate(sorted_suggestions, 1):
        print(format_suggestion(suggestion, i))

    print("="*70 + "\n")


def export_to_markdown(suggestions: List[Dict], output_file: str):
    """Export suggestions to a markdown file"""
    stats = get_statistics(suggestions)

    with open(output_file, 'w') as f:
        f.write("# ULTRON Agent - Improvement Suggestions\n\n")
        f.write(f"*Generated: {Path(SUGGESTIONS_FILE).stat().st_mtime}*\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total Suggestions**: {stats['total']}\n")
        f.write(f"- **Average Confidence**: {stats['avg_confidence']:.0%}\n\n")

        f.write("### By Priority\n\n")
        for priority in ['critical', 'high', 'medium', 'low']:
            count = stats['by_priority'].get(priority, 0)
            if count > 0:
                f.write(f"- **{priority.capitalize()}**: {count}\n")

        f.write("\n### By Category\n\n")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{category.capitalize()}**: {count}\n")

        f.write("\n---\n\n")

        # Group by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: (priority_order.get(s.get('priority', 'low').lower(), 4), -s.get('confidence', 0))
        )

        current_priority = None
        for suggestion in sorted_suggestions:
            priority = suggestion.get('priority', 'unknown').capitalize()

            if priority != current_priority:
                f.write(f"\n## {priority} Priority\n\n")
                current_priority = priority

            f.write(f"### {suggestion.get('module', 'Unknown Module')}\n\n")
            f.write(f"**Category**: {suggestion.get('category', 'unknown')}\n\n")
            f.write(f"**Issue**: {suggestion.get('description', 'No description')}\n\n")
            f.write(f"**Impact**: {suggestion.get('estimated_impact', 'Unknown')}\n\n")
            f.write(f"**Suggested Action**: {suggestion.get('suggested_action', 'No action')}\n\n")
            f.write(f"**Confidence**: {suggestion.get('confidence', 0):.0%}\n\n")
            f.write("---\n\n")

    print(f"✅ Exported {len(suggestions)} suggestions to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="View and analyze ULTRON Agent improvement suggestions"
    )
    parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'],
                       help='Filter by priority level')
    parser.add_argument('--category', choices=['performance', 'feature', 'usability', 'reliability', 'documentation'],
                       help='Filter by category')
    parser.add_argument('--top', type=int, metavar='N',
                       help='Show only top N suggestions')
    parser.add_argument('--export', metavar='FILE',
                       help='Export to markdown file')
    parser.add_argument('--stats-only', action='store_true',
                       help='Show only statistics')

    args = parser.parse_args()

    # Load suggestions
    suggestions = load_suggestions()
    if not suggestions:
        return

    # Apply filters
    filtered = filter_suggestions(suggestions, args.priority, args.category)

    if not filtered:
        print(f"\n❌ No suggestions found matching filters:")
        if args.priority:
            print(f"   Priority: {args.priority}")
        if args.category:
            print(f"   Category: {args.category}")
        print()
        return

    # Export if requested
    if args.export:
        export_to_markdown(filtered, args.export)
        return

    # Show stats only
    if args.stats_only:
        stats = get_statistics(filtered)
        print(f"\n📊 STATISTICS:")
        print(f"   Total: {stats['total']}")
        print(f"   By Priority: {stats['by_priority']}")
        print(f"   By Category: {stats['by_category']}")
        print(f"   Avg Confidence: {stats['avg_confidence']:.0%}\n")
        return

    # Display suggestions
    display_suggestions(filtered, args.top)


if __name__ == "__main__":
    main()
