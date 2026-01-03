#!/bin/bash
# Script to prepare and push a new release

set -e

VERSION=${1:-"1.1.0"}
TAG="v${VERSION}"

echo "=========================================="
echo "Preparing Release ${TAG}"
echo "=========================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Warning: You have uncommitted changes"
    echo "Do you want to continue? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Aborted"
        exit 1
    fi
fi

# Add all new files
echo "Adding new files..."
git add test_cpp_dataflow_comprehensive.py
git add test_cpp_runner.py
git add test_cpp_files/
git add .github/workflows/tests.yml
git add .github/workflows/release.yml
git add TEST_README.md
git add TEST_SUMMARY.md
git add RELEASE_NOTES.md
git add pytest.ini

# Commit changes
echo "Committing changes..."
git commit -m "Add comprehensive C++ test suite and CI/CD workflows

- Add comprehensive C++ dataflow analysis test suite
- Add test runner with multiple options
- Add GitHub Actions workflows for testing
- Update release workflow to run tests before building
- Add test documentation and README
- Update release notes for v1.1.0"

# Create and push tag
echo "Creating tag ${TAG}..."
git tag -a "${TAG}" -m "Release ${TAG}: C++ Test Suite

- Comprehensive C++ test suite
- GitHub Actions CI/CD integration
- Automated testing before releases"

echo "Pushing changes..."
git push origin main || git push origin master

echo "Pushing tag..."
git push origin "${TAG}"

echo ""
echo "=========================================="
echo "Release ${TAG} prepared and pushed!"
echo "=========================================="
echo ""
echo "GitHub Actions will now:"
echo "1. Run tests automatically"
echo "2. Build binaries for all platforms"
echo "3. Create release with artifacts"
echo ""
echo "Check the Actions tab in GitHub to monitor progress:"
echo "https://github.com/YOUR_USERNAME/YOUR_REPO/actions"

