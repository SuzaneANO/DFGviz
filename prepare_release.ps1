# PowerShell script to prepare and push a new release

param(
    [string]$Version = "1.1.0"
)

$Tag = "v$Version"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Preparing Release $Tag" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if we're in a git repository
try {
    $null = git rev-parse --git-dir 2>$null
} catch {
    Write-Host "Error: Not in a git repository" -ForegroundColor Red
    exit 1
}

# Check if there are uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "Warning: You have uncommitted changes" -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue? (y/n)"
    if ($response -ne "y") {
        Write-Host "Aborted" -ForegroundColor Red
        exit 1
    }
}

# Add all new files
Write-Host "Adding new files..." -ForegroundColor Green
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
Write-Host "Committing changes..." -ForegroundColor Green
$commitMessage = @"
Add comprehensive C++ test suite and CI/CD workflows

- Add comprehensive C++ dataflow analysis test suite
- Add test runner with multiple options
- Add GitHub Actions workflows for testing
- Update release workflow to run tests before building
- Add test documentation and README
- Update release notes for v1.1.0
"@

git commit -m $commitMessage

# Create and push tag
Write-Host "Creating tag $Tag..." -ForegroundColor Green
$tagMessage = @"
Release $Tag : C++ Test Suite

- Comprehensive C++ test suite
- GitHub Actions CI/CD integration
- Automated testing before releases
"@

git tag -a $Tag -m $tagMessage

Write-Host "Pushing changes..." -ForegroundColor Green
git push origin main 2>$null
if ($LASTEXITCODE -ne 0) {
    git push origin master
}

Write-Host "Pushing tag..." -ForegroundColor Green
git push origin $Tag

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Release $Tag prepared and pushed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GitHub Actions will now:" -ForegroundColor Yellow
Write-Host "1. Run tests automatically"
Write-Host "2. Build binaries for all platforms"
Write-Host "3. Create release with artifacts"
Write-Host ""
Write-Host "Check the Actions tab in GitHub to monitor progress"

