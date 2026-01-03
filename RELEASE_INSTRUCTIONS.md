# Release Instructions - v1.1.0

## Quick Release (Windows PowerShell)

Run the automated script:
```powershell
.\prepare_release.ps1 -Version 1.1.0
```

## Manual Release Steps

### Step 1: Add All Files
```powershell
git add test_cpp_dataflow_comprehensive.py
git add test_cpp_runner.py
git add test_cpp_files/
git add .github/workflows/tests.yml
git add .github/workflows/release.yml
git add TEST_README.md
git add TEST_SUMMARY.md
git add RELEASE_NOTES.md
git add pytest.ini
git add .gitignore
git add prepare_release.ps1
git add prepare_release.sh
```

### Step 2: Commit
```powershell
git commit -m "Add comprehensive C++ test suite and CI/CD workflows

- Add comprehensive C++ dataflow analysis test suite
- Add test runner with multiple options
- Add GitHub Actions workflows for testing
- Update release workflow to run tests before building
- Add test documentation and README
- Update release notes for v1.1.0"
```

### Step 3: Create Tag
```powershell
git tag -a v1.1.0 -m "Release v1.1.0: C++ Test Suite

- Comprehensive C++ test suite
- GitHub Actions CI/CD integration
- Automated testing before releases"
```

### Step 4: Push Everything
```powershell
git push origin main
git push origin v1.1.0
```

## What Happens Next

1. GitHub Actions will automatically:
   - Run test suite (Python and C++)
   - Build binaries for Windows, Linux, macOS
   - Create release package
   - Upload artifacts
   - Create GitHub release

2. Monitor progress at:
   - Actions tab: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
   - Releases: `https://github.com/YOUR_USERNAME/YOUR_REPO/releases`

## Files Added/Modified

### New Files
- ✅ `test_cpp_dataflow_comprehensive.py` - Comprehensive test suite
- ✅ `test_cpp_runner.py` - Test runner
- ✅ `test_cpp_files/` - Test C++ files directory
- ✅ `.github/workflows/tests.yml` - CI/CD test workflow
- ✅ `TEST_README.md` - Test documentation
- ✅ `TEST_SUMMARY.md` - Test summary
- ✅ `pytest.ini` - Pytest configuration
- ✅ `prepare_release.ps1` - Release script (Windows)
- ✅ `prepare_release.sh` - Release script (Linux/macOS)
- ✅ `RELEASE_CHECKLIST.md` - Release checklist
- ✅ `RELEASE_INSTRUCTIONS.md` - This file

### Modified Files
- ✅ `.github/workflows/release.yml` - Added test step
- ✅ `RELEASE_NOTES.md` - Added v1.1.0 notes
- ✅ `.gitignore` - Updated to allow test files

## Verification

After pushing, verify:
- [ ] GitHub Actions workflow runs successfully
- [ ] Tests pass (may skip C++ tests if Clang not available)
- [ ] Release is created automatically
- [ ] Artifacts are uploaded

## Troubleshooting

### If tests fail
- C++ tests may be skipped if Clang is not available (this is OK)
- Python tests should always pass
- Check GitHub Actions logs for details

### If release doesn't create automatically
- Manually create release on GitHub
- Select tag `v1.1.0`
- Copy content from `RELEASE_NOTES.md`
- Upload artifacts from `releases/` folder

### If git push fails
- Check you have write access to repository
- Verify you're on the correct branch (main/master)
- Check remote is set: `git remote -v`

