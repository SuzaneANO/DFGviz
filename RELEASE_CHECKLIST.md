# Release Checklist - v1.1.0

## Pre-Release Steps

### 1. Verify All Tests Pass Locally
```bash
cd dataflow_analysis
python test_cpp_runner.py --all
```

### 2. Check Git Status
```bash
git status
```

### 3. Add All New Files
```bash
# On Windows (PowerShell)
git add test_cpp_dataflow_comprehensive.py
git add test_cpp_runner.py
git add test_cpp_files/
git add .github/workflows/tests.yml
git add .github/workflows/release.yml
git add TEST_README.md
git add TEST_SUMMARY.md
git add RELEASE_NOTES.md
git add pytest.ini
git add prepare_release.ps1
git add prepare_release.sh

# Or use the script
.\prepare_release.ps1 -Version 1.1.0
```

### 4. Commit Changes
```bash
git commit -m "Add comprehensive C++ test suite and CI/CD workflows

- Add comprehensive C++ dataflow analysis test suite
- Add test runner with multiple options  
- Add GitHub Actions workflows for testing
- Update release workflow to run tests before building
- Add test documentation and README
- Update release notes for v1.1.0"
```

### 5. Create and Push Tag
```bash
git tag -a v1.1.0 -m "Release v1.1.0: C++ Test Suite

- Comprehensive C++ test suite
- GitHub Actions CI/CD integration
- Automated testing before releases"

git push origin main  # or master
git push origin v1.1.0
```

## Automated Steps (GitHub Actions)

Once the tag is pushed, GitHub Actions will automatically:

1. ✅ Run test suite (Python and C++)
2. ✅ Build binaries for Windows, Linux, macOS
3. ✅ Create release package
4. ✅ Upload artifacts
5. ✅ Create GitHub release

## Manual Steps (if needed)

If GitHub Actions doesn't create the release automatically:

1. Go to GitHub repository
2. Click "Releases" → "Draft a new release"
3. Select tag `v1.1.0`
4. Title: "Release v1.1.0: C++ Test Suite"
5. Copy content from RELEASE_NOTES.md
6. Upload artifacts from `releases/` folder
7. Publish release

## Verification

After release:

- [ ] Check GitHub Actions ran successfully
- [ ] Verify release was created on GitHub
- [ ] Download and test release artifacts
- [ ] Update documentation if needed

## Files Changed

### New Files
- `test_cpp_dataflow_comprehensive.py` - Main test suite
- `test_cpp_runner.py` - Test runner
- `test_cpp_files/` - Test C++ files
- `.github/workflows/tests.yml` - Test workflow
- `TEST_README.md` - Test documentation
- `TEST_SUMMARY.md` - Test summary
- `prepare_release.ps1` - Release script (Windows)
- `prepare_release.sh` - Release script (Linux/macOS)

### Modified Files
- `.github/workflows/release.yml` - Added test step
- `RELEASE_NOTES.md` - Added v1.1.0 notes
- `.gitignore` - May need to allow test files

## Notes

- Test files may need to be explicitly added if they're in .gitignore
- GitHub Actions will run tests automatically on push
- Release will be created automatically when tag is pushed

