"""
ULTRON Agent Version Management

This module provides centralized version information for the ULTRON Agent project.
Follows semantic versioning: MAJOR.MINOR.PATCH

Version Components:
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality additions  
- PATCH: Backwards-compatible bug fixes
"""

# Main version information
__version__ = "3.0.0"
__version_info__ = tuple(map(int, __version__.split(".")))

# Additional version metadata
VERSION_MAJOR = __version_info__[0]
VERSION_MINOR = __version_info__[1] 
VERSION_PATCH = __version_info__[2]

# Build metadata (populated by CI/CD)
BUILD_DATE = None
BUILD_COMMIT = None
BUILD_BRANCH = None

def get_version(include_build_info: bool = False) -> str:
    """
    Get the version string, optionally including build information.
    
    Args:
        include_build_info: Whether to include build metadata in version string
        
    Returns:
        Version string in semantic version format
    """
    version = __version__
    
    if include_build_info and any([BUILD_DATE, BUILD_COMMIT, BUILD_BRANCH]):
        build_info = []
        if BUILD_COMMIT:
            build_info.append(f"commit.{BUILD_COMMIT[:8]}")
        if BUILD_BRANCH and BUILD_BRANCH != "main":
            build_info.append(f"branch.{BUILD_BRANCH}")
        if BUILD_DATE:
            build_info.append(f"built.{BUILD_DATE}")
            
        if build_info:
            version += f"+{'.'.join(build_info)}"
    
    return version

def get_version_info() -> dict:
    """
    Get comprehensive version information as a dictionary.
    
    Returns:
        Dictionary containing all version metadata
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR, 
        "patch": VERSION_PATCH,
        "build_date": BUILD_DATE,
        "build_commit": BUILD_COMMIT,
        "build_branch": BUILD_BRANCH,
        "full_version": get_version(include_build_info=True)
    }

# For backward compatibility
version = __version__