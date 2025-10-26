#!/usr/bin/env python3
"""
ULTRON Agent - Automated Improvement Implementation
===================================================
Automatically implement improvement suggestions with AI assistance.

Usage:
    python auto_improve.py --show                    # Show all suggestions
    python auto_improve.py --implement-all           # Implement ALL suggestions
    python auto_improve.py --implement-priority high # Implement by priority
    python auto_improve.py --implement-category reliability  # By category
    python auto_improve.py --implement-top 10        # Top 10 only
    python auto_improve.py --dry-run                 # Preview changes without applying
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter

PROJECT_ROOT = Path(__file__).parent
SUGGESTIONS_FILE = PROJECT_ROOT / "metrics" / "suggestions.json"
BACKUP_DIR = PROJECT_ROOT / "backups" / "auto_improve"


class AutoImprover:
    """Automated improvement implementation engine"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.changes_made = []
        self.errors = []

    def load_suggestions(self) -> List[Dict[str, Any]]:
        """Load all suggestions"""
        if not SUGGESTIONS_FILE.exists():
            print(f"❌ No suggestions file found. Run: python self_improvement.py --scan")
            return []

        with open(SUGGESTIONS_FILE, 'r') as f:
            return json.load(f)

    def show_all_suggestions(self, suggestions: List[Dict]):
        """Display all suggestions in organized format"""
        if not suggestions:
            print("\n✅ No suggestions found!\n")
            return

        stats = self._get_stats(suggestions)

        print("\n" + "="*80)
        print("🤖 ULTRON AGENT - ALL IMPROVEMENT SUGGESTIONS")
        print("="*80)

        print(f"\n📊 OVERVIEW:")
        print(f"   Total Suggestions: {stats['total']}")
        print(f"   High Priority: {stats['high']}")
        print(f"   Medium Priority: {stats['medium']}")
        print(f"   Low Priority: {stats['low']}")
        print(f"   Average Confidence: {stats['avg_confidence']:.0%}")

        print(f"\n📁 BY CATEGORY:")
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat.capitalize()}: {count}")

        # Group by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_sugs = sorted(
            suggestions,
            key=lambda s: (priority_order.get(s.get('priority', 'low').lower(), 4), -s.get('confidence', 0))
        )

        current_priority = None
        for i, sug in enumerate(sorted_sugs, 1):
            priority = sug.get('priority', 'unknown').upper()

            if priority != current_priority:
                print(f"\n{'='*80}")
                print(f"🎯 {priority} PRIORITY")
                print(f"{'='*80}\n")
                current_priority = priority

            icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(priority, '⚪')

            print(f"{i}. {icon} {sug.get('module', 'Unknown')}")
            print(f"   Category: {sug.get('category', 'unknown')}")
            print(f"   Issue: {sug.get('description', 'No description')}")
            print(f"   Impact: {sug.get('estimated_impact', 'Unknown')}")
            print(f"   Action: {sug.get('suggested_action', 'No action')}")
            print(f"   Confidence: {sug.get('confidence', 0):.0%}")
            print()

        print("="*80 + "\n")

    def _get_stats(self, suggestions: List[Dict]) -> Dict:
        """Get statistics about suggestions"""
        priorities = Counter(s.get('priority', 'unknown').lower() for s in suggestions)
        categories = Counter(s.get('category', 'unknown') for s in suggestions)

        return {
            'total': len(suggestions),
            'high': priorities.get('high', 0),
            'medium': priorities.get('medium', 0),
            'low': priorities.get('low', 0),
            'by_category': dict(categories),
            'avg_confidence': sum(s.get('confidence', 0) for s in suggestions) / len(suggestions) if suggestions else 0
        }

    def implement_suggestions(self, suggestions: List[Dict]) -> Dict[str, Any]:
        """Implement all provided suggestions"""
        print(f"\n🚀 {'DRY RUN - ' if self.dry_run else ''}Implementing {len(suggestions)} suggestions...\n")

        stats = {
            'total': len(suggestions),
            'implemented': 0,
            'skipped': 0,
            'failed': 0
        }

        # Group by category for efficient processing
        by_category = {}
        for sug in suggestions:
            cat = sug.get('category', 'unknown')
            by_category.setdefault(cat, []).append(sug)

        # Implement by category
        for category, cat_suggestions in by_category.items():
            print(f"📦 Processing {category.upper()} suggestions ({len(cat_suggestions)})...")

            if category == 'reliability':
                result = self._implement_reliability(cat_suggestions)
            elif category == 'performance':
                result = self._implement_performance(cat_suggestions)
            elif category == 'usability':
                result = self._implement_usability(cat_suggestions)
            elif category == 'documentation':
                result = self._implement_documentation(cat_suggestions)
            else:
                result = {'implemented': 0, 'skipped': len(cat_suggestions), 'failed': 0}

            stats['implemented'] += result['implemented']
            stats['skipped'] += result['skipped']
            stats['failed'] += result['failed']

        return stats

    def _implement_reliability(self, suggestions: List[Dict]) -> Dict[str, int]:
        """Implement reliability improvements (error handling, tests)"""
        stats = {'implemented': 0, 'skipped': 0, 'failed': 0}

        for sug in suggestions:
            module = sug.get('module', '')
            description = sug.get('description', '')

            # Handle test coverage issues
            if 'test coverage' in description.lower():
                print(f"   📝 Test coverage: Creating test structure...")
                if self._create_test_structure():
                    stats['implemented'] += 1
                    self.changes_made.append(f"Created test structure for improved coverage")
                else:
                    stats['skipped'] += 1
                continue

            # Handle error handling
            if 'error handling' in description.lower() and module.endswith('.py'):
                file_path = PROJECT_ROOT / module
                if file_path.exists():
                    print(f"   🔧 {module}: Adding error handling...")
                    if self._add_error_handling(file_path):
                        stats['implemented'] += 1
                        self.changes_made.append(f"Added error handling to {module}")
                    else:
                        stats['failed'] += 1
                else:
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1

        return stats

    def _implement_performance(self, suggestions: List[Dict]) -> Dict[str, int]:
        """Implement performance improvements (modularization, optimization)"""
        stats = {'implemented': 0, 'skipped': 0, 'failed': 0}

        for sug in suggestions:
            module = sug.get('module', '')
            description = sug.get('description', '')

            # Handle large files
            if 'large file' in description.lower() and module.endswith('.py'):
                file_path = PROJECT_ROOT / module
                if file_path.exists() and self._is_deprecated_file(module):
                    print(f"   🗑️  {module}: Deprecated/backup file - documenting for cleanup...")
                    stats['implemented'] += 1
                    self.changes_made.append(f"Flagged {module} for cleanup (deprecated)")
                else:
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1

        return stats

    def _implement_usability(self, suggestions: List[Dict]) -> Dict[str, int]:
        """Implement usability improvements (documentation, comments)"""
        stats = {'implemented': 0, 'skipped': 0, 'failed': 0}

        for sug in suggestions:
            module = sug.get('module', '')
            description = sug.get('description', '')

            # Handle missing docstrings
            if 'docstring' in description.lower() and module.endswith('.py'):
                file_path = PROJECT_ROOT / module
                if file_path.exists():
                    print(f"   📚 {module}: Adding docstrings...")
                    if self._add_docstrings(file_path):
                        stats['implemented'] += 1
                        self.changes_made.append(f"Added docstrings to {module}")
                    else:
                        stats['failed'] += 1
                else:
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1

        return stats

    def _implement_documentation(self, suggestions: List[Dict]) -> Dict[str, int]:
        """Implement documentation improvements"""
        stats = {'implemented': 0, 'skipped': 0, 'failed': 0}

        for sug in suggestions:
            # Most documentation suggestions need manual review
            stats['skipped'] += 1

        return stats

    def _create_test_structure(self) -> bool:
        """Create basic test structure"""
        if self.dry_run:
            print(f"      [DRY RUN] Would create test structure")
            return True

        try:
            tests_dir = PROJECT_ROOT / "tests"
            tests_dir.mkdir(exist_ok=True)

            # Create test template
            test_template = tests_dir / "test_template.py"
            if not test_template.exists():
                test_template.write_text("""\"\"\"
Test Template for ULTRON Agent
==============================
Copy this template to create new test files.

Usage:
    pytest tests/test_mymodule.py
\"\"\"

import pytest
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestExample:
    \"\"\"Example test class\"\"\"

    def test_example(self):
        \"\"\"Example test case\"\"\"
        assert True

    def test_import(self):
        \"\"\"Test that module can be imported\"\"\"
        # TODO: Import your module here
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
""")

            # Create README for tests
            test_readme = tests_dir / "README.md"
            if not test_readme.exists():
                test_readme.write_text("""# ULTRON Agent Tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_brain.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run verbose
pytest -v
```

## Test Structure

- `test_template.py` - Template for new tests
- `test_*.py` - Individual test modules
- `conftest.py` - Shared fixtures (in project root)

## Writing Tests

1. Copy `test_template.py` to `test_yourmodule.py`
2. Import module to test
3. Write test cases using pytest
4. Run tests to verify

## Coverage Goals

- Core modules: >80% coverage
- Tools: >60% coverage
- GUI: >40% coverage
""")

            return True
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            self.errors.append(f"Test structure creation: {e}")
            return False

    def _add_error_handling(self, file_path: Path) -> bool:
        """Add basic error handling to a Python file"""
        if self.dry_run:
            print(f"      [DRY RUN] Would add error handling to {file_path.name}")
            return True

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Skip if file is too small or already has good error handling
            if len(content) < 100 or content.count('try:') > 3:
                return False

            # Backup original
            backup_path = self.backup_dir / file_path.name
            backup_path.write_text(content, encoding='utf-8')

            # Add error handling wrapper to main execution
            if '__name__ == "__main__"' in content and 'try:' not in content.split('__name__ == "__main__"')[1]:
                content = content.replace(
                    'if __name__ == "__main__":',
                    'if __name__ == "__main__":\n    try:'
                )
                # Add except at the end
                content += '\n    except Exception as e:\n        print(f"Error: {e}")\n        sys.exit(1)\n'

                file_path.write_text(content, encoding='utf-8')
                return True

            return False
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            self.errors.append(f"Error handling for {file_path}: {e}")
            return False

    def _add_docstrings(self, file_path: Path) -> bool:
        """Add basic docstrings to a Python file"""
        if self.dry_run:
            print(f"      [DRY RUN] Would add docstrings to {file_path.name}")
            return True

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Check if file already has module docstring
            if content.strip().startswith('"""') or content.strip().startswith("'''"):
                return False

            # Backup original
            backup_path = self.backup_dir / file_path.name
            backup_path.write_text(content, encoding='utf-8')

            # Add module docstring
            module_name = file_path.stem.replace('_', ' ').title()
            docstring = f'"""\n{module_name}\n{"="*len(module_name)}\nULTRON Agent module for {module_name.lower()} functionality.\n"""\n\n'

            # Insert after shebang and encoding declarations
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('#!') or 'coding' in line or 'encoding' in line:
                    insert_pos = i + 1
                else:
                    break

            lines.insert(insert_pos, docstring.strip())
            new_content = '\n'.join(lines)

            file_path.write_text(new_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            self.errors.append(f"Docstring for {file_path}: {e}")
            return False

    def _is_deprecated_file(self, module: str) -> bool:
        """Check if file is deprecated or backup"""
        deprecated_indicators = [
            '.git-rewrite', 'backup', 'old', '_deprecated',
            'archive', 'unused', 'legacy', 'gui_compact', 'gui_clean'
        ]
        return any(ind in module.lower() for ind in deprecated_indicators)

    def generate_report(self, stats: Dict[str, int]):
        """Generate implementation report"""
        print("\n" + "="*80)
        print("📊 IMPLEMENTATION REPORT")
        print("="*80)

        print(f"\n✅ Successfully Implemented: {stats['implemented']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"📊 Total Processed: {stats['total']}")

        if stats['implemented'] > 0:
            success_rate = (stats['implemented'] / stats['total']) * 100
            print(f"🎯 Success Rate: {success_rate:.1f}%")

        if self.changes_made:
            print(f"\n📝 CHANGES MADE:")
            for change in self.changes_made:
                print(f"   ✓ {change}")

        if self.errors:
            print(f"\n⚠️  ERRORS:")
            for error in self.errors:
                print(f"   ✗ {error}")

        print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Automatically implement improvement suggestions"
    )
    parser.add_argument('--show', action='store_true',
                       help='Show all suggestions without implementing')
    parser.add_argument('--implement-all', action='store_true',
                       help='Implement ALL suggestions')
    parser.add_argument('--implement-priority', choices=['critical', 'high', 'medium', 'low'],
                       help='Implement suggestions by priority')
    parser.add_argument('--implement-category', choices=['performance', 'reliability', 'usability', 'documentation'],
                       help='Implement suggestions by category')
    parser.add_argument('--implement-top', type=int, metavar='N',
                       help='Implement top N suggestions')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without applying them')

    args = parser.parse_args()

    improver = AutoImprover(dry_run=args.dry_run)
    suggestions = improver.load_suggestions()

    if not suggestions:
        return

    # Show all suggestions
    if args.show:
        improver.show_all_suggestions(suggestions)
        return

    # Filter suggestions based on arguments
    to_implement = suggestions

    if args.implement_priority:
        to_implement = [s for s in suggestions if s.get('priority', '').lower() == args.implement_priority.lower()]
        print(f"🎯 Filtering to {args.implement_priority.upper()} priority: {len(to_implement)} suggestions")

    if args.implement_category:
        to_implement = [s for s in to_implement if s.get('category', '').lower() == args.implement_category.lower()]
        print(f"📦 Filtering to {args.implement_category.upper()} category: {len(to_implement)} suggestions")

    if args.implement_top:
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        to_implement = sorted(
            to_implement,
            key=lambda s: (priority_order.get(s.get('priority', 'low').lower(), 4), -s.get('confidence', 0))
        )[:args.implement_top]
        print(f"🔝 Limiting to top {args.implement_top} suggestions")

    # Show what will be implemented
    if not args.show and (args.implement_all or args.implement_priority or args.implement_category or args.implement_top):
        print(f"\n📋 SUGGESTIONS TO IMPLEMENT: {len(to_implement)}")

        if not args.dry_run:
            response = input("\n⚠️  This will modify your code. Continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Cancelled.")
                return

        # Implement suggestions
        stats = improver.implement_suggestions(to_implement)
        improver.generate_report(stats)
    else:
        print("\n❌ No action specified. Use --show, --implement-all, or filter options.")
        print("   Run with --help for usage information.")


if __name__ == "__main__":
    main()
