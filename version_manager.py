#!/usr/bin/env python3
"""
Version Management Utility for ULTRON Agent

This script provides utilities for managing semantic versions:
- Bump version numbers (major, minor, patch)
- Display current version information
- Validate version format
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple


def get_version_file_path() -> Path:
    """Get the path to the version file."""
    return Path(__file__).parent / "ultron_agent" / "__version__.py"


def read_version() -> str:
    """Read current version from __version__.py file."""
    version_file = get_version_file_path()
    if not version_file.exists():
        raise FileNotFoundError(f"Version file not found: {version_file}")
    
    content = version_file.read_text(encoding="utf-8")
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    
    if not version_match:
        raise ValueError("Could not find version in __version__.py")
    
    return version_match.group(1)


def write_version(new_version: str) -> None:
    """Write new version to __version__.py file."""
    version_file = get_version_file_path()
    content = version_file.read_text(encoding="utf-8")
    
    # Replace version string
    new_content = re.sub(
        r'^(__version__\s*=\s*["\'])([^"\']+)(["\'])',
        rf'\g<1>{new_version}\g<3>',
        content,
        flags=re.MULTILINE
    )
    
    # Update version_info tuple
    version_parts = new_version.split('.')
    if len(version_parts) == 3:
        new_content = re.sub(
            r'^(__version_info__\s*=\s*tuple\(map\(int,\s*__version__\.split\(["\'][.]["\']\)\))',
            rf'__version_info__ = {tuple(map(int, version_parts))}',
            new_content,
            flags=re.MULTILINE
        )
    
    version_file.write_text(new_content, encoding="utf-8")
    print(f"✅ Version updated to {new_version}")


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string into major, minor, patch components."""
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValueError(f"Invalid semantic version format: {version}")
    
    parts = version.split('.')
    return int(parts[0]), int(parts[1]), int(parts[2])


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version components into semantic version string."""
    return f"{major}.{minor}.{patch}"


def bump_version(version_type: str) -> str:
    """Bump version by specified type (major, minor, patch)."""
    current_version = read_version()
    major, minor, patch = parse_version(current_version)
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid version type: {version_type}")
    
    new_version = format_version(major, minor, patch)
    write_version(new_version)
    return new_version


def show_version() -> None:
    """Display current version information."""
    try:
        current_version = read_version()
        major, minor, patch = parse_version(current_version)
        
        print(f"Current Version: {current_version}")
        print(f"  Major: {major}")
        print(f"  Minor: {minor}")
        print(f"  Patch: {patch}")
        
        # Import and show full version info if possible
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from ultron_agent.__version__ import get_version_info
            
            info = get_version_info()
            print(f"  Full Version: {info['full_version']}")
            if info.get('build_commit'):
                print(f"  Build Commit: {info['build_commit']}")
            if info.get('build_branch'):
                print(f"  Build Branch: {info['build_branch']}")
        except ImportError:
            pass
            
    except Exception as e:
        print(f"❌ Error reading version: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ULTRON Agent Version Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python version_manager.py show              # Show current version
  python version_manager.py bump patch        # Bump patch version
  python version_manager.py bump minor        # Bump minor version  
  python version_manager.py bump major        # Bump major version
  python version_manager.py set 3.1.0         # Set specific version
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    subparsers.add_parser('show', help='Show current version information')
    
    # Bump command
    bump_parser = subparsers.add_parser('bump', help='Bump version')
    bump_parser.add_argument(
        'type', 
        choices=['major', 'minor', 'patch'],
        help='Version component to bump'
    )
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set specific version')
    set_parser.add_argument('version', help='Version to set (e.g., 3.1.0)')
    
    args = parser.parse_args()
    
    if args.command == 'show':
        show_version()
    elif args.command == 'bump':
        try:
            old_version = read_version()
            new_version = bump_version(args.type)
            print(f"🚀 Bumped {args.type} version: {old_version} → {new_version}")
        except Exception as e:
            print(f"❌ Error bumping version: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == 'set':
        try:
            # Validate format
            parse_version(args.version)
            old_version = read_version()
            write_version(args.version)
            print(f"🎯 Version set: {old_version} → {args.version}")
        except Exception as e:
            print(f"❌ Error setting version: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()