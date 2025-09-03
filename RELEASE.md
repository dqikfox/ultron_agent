# Release Management Guide

This document describes the automated release process for ULTRON Agent.

## Overview

ULTRON Agent uses semantic versioning and automated release workflows to publish packages to PyPI and Docker Hub.

## Version Management

### Semantic Versioning

The project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality in a backwards compatible manner
- **PATCH** version: Backwards compatible bug fixes

### Version Files

- `ultron_agent/__version__.py` - Centralized version management
- `pyproject.toml` - Uses dynamic versioning from `__version__.py`
- `package.json` - JavaScript package version (kept in sync manually)

## Release Process

### Automated Release (Recommended)

1. **Check current version:**
   ```bash
   python version_manager.py show
   ```

2. **Dry run release:**
   ```bash
   python release_manager.py --dry-run patch  # or minor/major
   ```

3. **Execute release:**
   ```bash
   python release_manager.py patch  # or minor/major
   ```

This will:
- Validate git status and run tests
- Bump version in code
- Update changelog
- Commit changes
- Create and push version tag
- Trigger automated publishing workflows

### Manual Version Management

```bash
# Show current version
python version_manager.py show

# Bump version
python version_manager.py bump patch
python version_manager.py bump minor  
python version_manager.py bump major

# Set specific version
python version_manager.py set 3.1.0
```

### NPM Scripts

Convenient NPM scripts are available:

```bash
# Check version
npm run version

# Release commands
npm run release:patch
npm run release:minor
npm run release:major
npm run release:dry-run
```

## Automated Publishing

When a version tag (e.g., `v3.0.1`) is pushed, GitHub Actions automatically:

### PyPI Publishing
- Validates version consistency
- Runs tests and quality checks
- Builds Python package
- Publishes to PyPI

### Docker Hub Publishing
- Builds multi-platform Docker images
- Tags with semantic version
- Publishes to Docker Hub

### GitHub Release
- Generates changelog from commits
- Creates GitHub Release with artifacts
- Attaches built packages

## Configuration

### Required Secrets

Configure these secrets in GitHub repository settings:

- `PYPI_API_TOKEN` - PyPI API token for publishing
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token

### Environment Setup

For PyPI publishing environment:
1. Go to Repository Settings > Environments
2. Create environment named "release"
3. Add required reviewers if needed
4. Configure protection rules

## Docker Usage

After release, the Docker image is available:

```bash
# Pull latest version
docker pull dqikfox/ultron-agent:latest

# Pull specific version
docker pull dqikfox/ultron-agent:3.0.1

# Run container
docker run -p 8000:8000 dqikfox/ultron-agent:latest
```

## PyPI Installation

After release, the package is available on PyPI:

```bash
# Install latest version
pip install ultron-agent

# Install specific version
pip install ultron-agent==3.0.1

# Install with extras
pip install ultron-agent[gui,ml]
```

## Troubleshooting

### Release Validation Failures

If release validation fails:

1. Check git repository is clean
2. Ensure on main branch
3. Run tests manually: `python release_manager.py --skip-tests patch`

### Version Consistency Issues

If version tag doesn't match code:

1. Update version: `python version_manager.py set X.Y.Z`
2. Commit changes: `git commit -am "Fix version to X.Y.Z"`
3. Re-tag: `git tag -f vX.Y.Z && git push origin vX.Y.Z --force`

### Failed Publishing

- Check GitHub Actions logs for specific error messages
- Verify secrets are configured correctly
- Ensure PyPI and Docker Hub credentials are valid

## Best Practices

1. **Always test releases with dry-run first**
2. **Keep changelog updated with meaningful entries**
3. **Use conventional commit messages for better changelog generation**
4. **Test the release locally before publishing**
5. **Monitor the automated workflows after tagging**

## Manual Release Steps (Emergency)

If automated release fails, manual steps:

1. **Build package:**
   ```bash
   python -m build
   ```

2. **Publish to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

3. **Build Docker image:**
   ```bash
   docker build -t ultron-agent:X.Y.Z .
   docker tag ultron-agent:X.Y.Z dqikfox/ultron-agent:X.Y.Z
   docker push dqikfox/ultron-agent:X.Y.Z
   ```

4. **Create GitHub release manually through web interface**

## Support

For release-related issues:
- Check [GitHub Actions](https://github.com/dqikfox/ultron_agent/actions)
- Review [Issues](https://github.com/dqikfox/ultron_agent/issues)
- Contact maintainers