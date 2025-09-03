#!/usr/bin/env python3
"""
Release Management Script for ULTRON Agent

This script automates the release process including:
- Version validation and bumping
- Git tagging and pushing
- Release notes generation
- Pre-release checks
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Import local version utilities
from version_manager import read_version, bump_version, parse_version


def run_command(cmd: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"📝 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
    if capture_output and result.stdout:
        print(result.stdout.strip())
    return result


def check_git_status() -> bool:
    """Check if git repository is clean."""
    try:
        result = run_command(['git', 'status', '--porcelain'])
        if result.stdout.strip():
            print("❌ Git repository is not clean. Please commit or stash changes:")
            print(result.stdout)
            return False
        
        print("✅ Git repository is clean")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to check git status")
        return False


def check_on_main_branch() -> bool:
    """Check if currently on main branch."""
    try:
        result = run_command(['git', 'branch', '--show-current'])
        current_branch = result.stdout.strip()
        
        if current_branch != 'main':
            print(f"❌ Not on main branch. Current branch: {current_branch}")
            print("Please switch to main branch before releasing")
            return False
        
        print(f"✅ On main branch: {current_branch}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to check current branch")
        return False


def run_tests() -> bool:
    """Run basic validation tests."""
    print("🧪 Running validation tests...")
    
    try:
        # Test version module
        result = run_command([
            'python', '-c',
            'from version_manager import read_version, parse_version; '
            'v = read_version(); '
            'parse_version(v); '
            'print(f"✅ Version validation passed: {v}")'
        ])
        
        # Test package import (basic)
        result = run_command([
            'python', '-c', 
            'exec(open("ultron_agent/__version__.py").read()); '
            'print(f"✅ Package version import: {__version__}")'
        ])
        
        print("✅ All validation tests passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False


def get_changelog_entry(version: str) -> str:
    """Get changelog entry for the version."""
    changelog_path = Path("Changelog.md")
    
    if not changelog_path.exists():
        return f"Release {version}"
    
    content = changelog_path.read_text(encoding="utf-8")
    
    # Look for unreleased section
    if "## [Unreleased]" in content:
        lines = content.split('\n')
        changelog_lines = []
        in_unreleased = False
        
        for line in lines:
            if line.startswith("## [Unreleased]"):
                in_unreleased = True
                continue
            elif line.startswith("## [") and in_unreleased:
                break
            elif in_unreleased and line.strip():
                changelog_lines.append(line)
        
        if changelog_lines:
            return '\n'.join(changelog_lines).strip()
    
    return f"Release {version}\n\nSee Changelog.md for details."


def update_changelog(version: str) -> None:
    """Update changelog with release information."""
    changelog_path = Path("Changelog.md")
    
    if not changelog_path.exists():
        print("⚠️ Changelog.md not found, skipping update")
        return
    
    content = changelog_path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Replace [Unreleased] with version and date
    updated_content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n### Added\n### Changed\n### Fixed\n\n## [{version}] - {today}"
    )
    
    changelog_path.write_text(updated_content, encoding="utf-8")
    print(f"✅ Updated Changelog.md for version {version}")


def create_git_tag(version: str, message: str) -> bool:
    """Create and push git tag."""
    tag_name = f"v{version}"
    
    try:
        # Create annotated tag
        run_command(['git', 'tag', '-a', tag_name, '-m', message])
        print(f"✅ Created tag: {tag_name}")
        
        # Push tag
        run_command(['git', 'push', 'origin', tag_name])
        print(f"✅ Pushed tag: {tag_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create/push tag: {e}")
        return False


def dry_run_release(version_type: str) -> None:
    """Perform a dry run of the release process."""
    print("🔍 DRY RUN: Release process simulation")
    print("=" * 50)
    
    current_version = read_version()
    print(f"Current version: {current_version}")
    
    # Simulate version bump
    major, minor, patch = parse_version(current_version)
    if version_type == "major":
        new_version = f"{major + 1}.0.0"
    elif version_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif version_type == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        new_version = version_type
    
    print(f"New version would be: {new_version}")
    print(f"Git tag would be: v{new_version}")
    
    changelog_entry = get_changelog_entry(new_version)
    print(f"\nChangelog entry:\n{changelog_entry}")
    
    print("\n🔍 Steps that would be performed:")
    print("1. ✅ Check git status and branch")
    print("2. ✅ Run validation tests")
    print("3. ✅ Bump version in code")
    print("4. ✅ Update changelog")
    print("5. ✅ Commit version changes")
    print("6. ✅ Create and push git tag")
    print("7. ✅ GitHub Actions will handle PyPI and Docker publishing")
    
    print("\n⚠️ This was a DRY RUN - no changes were made")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ULTRON Agent Release Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python release_manager.py patch         # Release patch version
  python release_manager.py minor         # Release minor version
  python release_manager.py major         # Release major version
  python release_manager.py 3.1.0         # Release specific version
  python release_manager.py --dry-run patch # Simulate release process
"""
    )
    
    parser.add_argument(
        'version',
        help='Version to release (major/minor/patch) or specific version'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate the release process without making changes'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip validation tests'
    )
    
    args = parser.parse_args()
    
    # Dry run mode
    if args.dry_run:
        dry_run_release(args.version)
        return
    
    print("🚀 Starting ULTRON Agent release process...")
    print("=" * 50)
    
    # Pre-release checks
    if not check_git_status():
        sys.exit(1)
    
    if not check_on_main_branch():
        sys.exit(1)
    
    if not args.skip_tests and not run_tests():
        sys.exit(1)
    
    # Determine new version
    current_version = read_version()
    print(f"Current version: {current_version}")
    
    if args.version in ['major', 'minor', 'patch']:
        new_version = bump_version(args.version)
    else:
        # Validate custom version
        try:
            parse_version(args.version)
            new_version = args.version
            # Update version file manually
            from version_manager import write_version
            write_version(new_version)
        except ValueError as e:
            print(f"❌ Invalid version format: {e}")
            sys.exit(1)
    
    print(f"New version: {new_version}")
    
    # Update changelog
    update_changelog(new_version)
    
    # Commit changes
    try:
        run_command(['git', 'add', 'ultron_agent/__version__.py', 'Changelog.md'])
        run_command(['git', 'commit', '-m', f'Bump version to {new_version}'])
        run_command(['git', 'push', 'origin', 'main'])
        print("✅ Committed and pushed version changes")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit changes: {e}")
        sys.exit(1)
    
    # Create release tag
    changelog_entry = get_changelog_entry(new_version)
    tag_message = f"Release {new_version}\n\n{changelog_entry}"
    
    if not create_git_tag(new_version, tag_message):
        sys.exit(1)
    
    print("=" * 50)
    print(f"🎉 Release {new_version} initiated successfully!")
    print(f"📦 Tag v{new_version} has been pushed")
    print("🔄 GitHub Actions will now handle:")
    print("  • PyPI package publishing")
    print("  • Docker image building and publishing")
    print("  • GitHub Release creation")
    print("\n👀 Monitor the release progress at:")
    print("  https://github.com/dqikfox/ultron_agent/actions")


if __name__ == '__main__':
    main()