# Packaging and Deployment

## Overview

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [just](https://github.com/casey/just) for task automation. The packaging is handled by [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci/) tool, which performs a `git archive` operation based on the `CHANGELOG.md`.

## Prerequisites

Ensure you have the required tools installed:

- **uv**: For Python dependency management
- **just**: For task automation
- **Git**: For version control and tagging

## Development Setup

Set up the development environment using the justfile:

```bash
# Bootstrap complete development environment
just bootstrap-dev

# Or run individual steps:
just create-venv          # Create virtual environment with uv
just dev-link            # Create symbolic links for development
just trans-compile       # Compile translations
```

## Packaging

### Install Dependencies

The CI dependencies are managed through uv and defined in `pyproject.toml`:

```bash
# Sync CI dependencies
uv sync --group ci
```

### Create Package

Use the justfile task to package a version:

```bash
# Package a specific version
just package 1.3.1

# The package task automatically:
# - Syncs CI dependencies
# - Copies required files (LICENSE, CHANGELOG.md, CREDITS.md)
# - Runs qgis-plugin-ci package
# - Restores development links
```

### Manual Packaging

If you need to run qgis-plugin-ci directly:

```bash
# Package latest version from CHANGELOG.md
uv run qgis-plugin-ci package latest

# Package specific version
uv run qgis-plugin-ci package 1.3.1
```

## Release Process

The release process is automated through GitHub Actions and follows a standard git workflow: **1 released version = 1 git tag**.

### Release Steps

For a tag `X.y.z` (must be SemVer compliant):

1. **Update CHANGELOG.md**: Add the new version entry. You can write it manually or use GitHub's auto-generated release notes:
   1. Go to [project's releases](https://github.com/fpennica/dip-strike-tools/releases) and click on `Draft a new release`
   1. In `Choose a tag`, enter the new tag
   1. Click on `Generate release notes`
   1. Copy/paste the generated text from `## What's changed` until the line before `**Full changelog**:...` in the CHANGELOG.md, replacing `What's changed` with the tag and publication date.

2. **Update metadata.txt** (optional): Change the version number in `dip_strike_tools/metadata.txt`. It's recommended to use the next version number with `-DEV` suffix (e.g. `1.4.0-DEV` when `X.y.z` is `1.3.0`) to avoid confusion during development.

3. **Create and push the git tag**:
   ```bash
   # Create annotated tag
   git tag -a X.y.z {git commit hash} -m "Release version X.y.z"

   # Push tag to main branch
   git push origin X.y.z
   # or push all tags at once
   git push --tags
   ```

4. **Automated CI/CD**: The GitHub Actions workflow will automatically:
   - Compile translations
   - Package the plugin
   - Create a GitHub release
   - Publish to the [official QGIS plugins repository](https://plugins.qgis.org/)

### Testing Release Process

Use the justfile to test the release process without publishing:

```bash
# Test release process locally
just release-test X.y.z
```

This runs the packaging steps without GitHub token and OSGEO authentication.

### Troubleshooting Failed Releases

If the CI/CD pipeline fails or you need to recreate a release:

```bash
# Delete the problematic tag locally and remotely
git tag -d X.y.z
git push origin :refs/tags/X.y.z

# Fix the issue, create a new tag, and push again
git tag -a X.y.z {corrected commit hash} -m "Release version X.y.z"
git push origin X.y.z
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **Linter**: Code quality checks with ruff
- **Tester**: Run tests with pytest-qgis  
- **Documentation**: Build and deploy documentation
- **Package & Release**: Automated packaging and publishing on tag push

### Workflow Files

- `.github/workflows/linter.yml`: Code linting
- `.github/workflows/tester.yml`: Test execution
- `.github/workflows/documentation.yml`: Documentation building
- `.github/workflows/package_and_release.yml`: Release automation
