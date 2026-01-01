# Publishing Guide - Scalpel Dataflow Analyzer

This guide walks you through publishing Scalpel Dataflow Analyzer as a GitHub release.

## Prerequisites

1. **GitHub Account** - You need a GitHub account
2. **Git Installed** - Git must be installed on your system
3. **Python Environment** - For building binaries (if needed)

## Step-by-Step Publishing Process

### Step 1: Prepare Your Repository

1. **Create a new GitHub repository**
   ```bash
   # On GitHub, create a new repository named "DFGviz"
   # Make it public or private as needed
   ```

2. **Initialize local repository** (if not already done)
   ```bash
   cd dataflow_analysis
   git init
   git add .
   git commit -m "Initial commit: Scalpel Dataflow Analyzer v1.0.0"
   ```

3. **Connect to remote repository**
   ```bash
   git remote add origin https://github.com/SuzaneANO/DFGviz.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Update Placeholders

Before publishing, update these placeholders in `README.md`:

- `SuzaneANO` → Your GitHub username
- `YOUR_VIDEO_ID` → Your YouTube demo video ID
- `your-email@example.com` → Your contact email
- Add actual screenshots to `docs/screenshots/` directory
- Add logo to `docs/logo.png`
- Add demo video thumbnail to `docs/demo_video_thumbnail.png`

### Step 3: Build Release Binaries

1. **Build binaries for all platforms** (if you have access to them):
   ```bash
   # On Windows
   python build_binary.py
   
   # On Linux (if available)
   python build_binary.py
   
   # On macOS (if available)
   python build_binary.py
   ```

2. **Create release packages**:
   ```bash
   python create_release.py
   ```
   
   This will create compressed archives in the `releases/` directory:
   - `ScalpelDataflowAnalyzer-windows-v1.0.0.zip`
   - `ScalpelDataflowAnalyzer-linux-v1.0.0.tar.gz` (if built on Linux)
   - `ScalpelDataflowAnalyzer-macos-v1.0.0.tar.gz` (if built on macOS)

### Step 4: Create Documentation Structure

Create the following directory structure:

```
dataflow_analysis/
├── docs/
│   ├── screenshots/
│   │   ├── main_gui.png
│   │   ├── dataflow_graph.png
│   │   ├── function_analysis.png
│   │   └── git_history.png
│   ├── logo.png
│   ├── demo_video_thumbnail.png
│   ├── USER_GUIDE.md
│   ├── API.md
│   └── TROUBLESHOOTING.md
├── releases/
└── ...
```

### Step 5: Create GitHub Release

1. **Go to your repository on GitHub**
   - Navigate to: `https://github.com/SuzaneANO/DFGviz`

2. **Click "Releases"** (on the right sidebar)
   - Or go directly to: `https://github.com/SuzaneANO/DFGviz/releases`

3. **Click "Draft a new release"**

4. **Fill in release details**:
   - **Tag version**: `v1.0.0` (or your version)
   - **Release title**: `Scalpel Dataflow Analyzer v1.0.0`
   - **Description**: Copy from `RELEASE_NOTES.md` (create this file) or use:
     ```markdown
     ## 🎉 First Release!
     
     ### Features
     - Interactive GUI for dataflow analysis
     - Git history analysis
     - Function-level analysis
     - Interactive D3.js visualizations
     - Standalone binary (no installation required)
     
     ### Downloads
     - **Windows**: Download `ScalpelDataflowAnalyzer-windows-v1.0.0.zip`
     - **Linux**: Download `ScalpelDataflowAnalyzer-linux-v1.0.0.tar.gz`
     - **macOS**: Download `ScalpelDataflowAnalyzer-macos-v1.0.0.tar.gz`
     
     ### Installation
     1. Download the archive for your platform
     2. Extract the archive
     3. Run `ScalpelDataflowAnalyzer.exe` (Windows) or `ScalpelDataflowAnalyzer` (Linux/macOS)
     
     ### Trial Period
     This release includes a 30-day trial period. After the trial expires, please purchase a license.
     ```

5. **Attach release files**:
   - Drag and drop the compressed binaries from `releases/` directory
   - Or click "Attach binaries" and select files

6. **Check "Set as the latest release"** (if this is your latest version)

7. **Click "Publish release"**

### Step 6: Update Repository Settings

1. **Add repository topics** (on GitHub repository page):
   - Click the gear icon next to "About"
   - Add topics: `python`, `dataflow-analysis`, `scalpel`, `static-analysis`, `visualization`, `git-analysis`

2. **Add repository description**:
   ```
   Professional Python dataflow analysis tool with interactive visualizations. Analyze code dataflow across git history with Scalpel CFG.
   ```

3. **Add website** (if you have one):
   ```
   https://github.com/SuzaneANO/DFGviz
   ```

### Step 7: Create Additional Files

Create these files to improve your repository:

1. **LICENSE** (if not exists):
   ```bash
   # Create MIT License file
   # You can use: https://choosealicense.com/licenses/mit/
   ```

2. **CONTRIBUTING.md**:
   ```markdown
   # Contributing to Scalpel Dataflow Analyzer
   
   Thank you for your interest in contributing!
   
   ## How to Contribute
   
   1. Fork the repository
   2. Create a feature branch
   3. Make your changes
   4. Submit a pull request
   
   ## Development Setup
   
   See README.md for setup instructions.
   ```

3. **.gitignore** (if not exists):
   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg
   
   # PyInstaller
   *.spec
   build/
   dist/
   
   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo
   *~
   
   # OS
   .DS_Store
   Thumbs.db
   
   # Releases (optional - you might want to track these)
   # releases/
   ```

### Step 8: Finalize and Share

1. **Test the release**:
   - Download your own release
   - Test on a clean system
   - Verify all features work

2. **Share your release**:
   - Share the release link on social media
   - Post on relevant forums/communities
   - Update your project website (if any)

3. **Monitor feedback**:
   - Watch for issues on GitHub
   - Respond to user questions
   - Collect feedback for future releases

## Release Checklist

Before publishing, ensure:

- [ ] All placeholders in README.md are replaced
- [ ] Screenshots are added to `docs/screenshots/`
- [ ] Logo is added to `docs/logo.png`
- [ ] Demo video thumbnail is added
- [ ] LICENSE file exists
- [ ] .gitignore is configured
- [ ] Binaries are built and tested
- [ ] Release packages are created
- [ ] Release notes are written
- [ ] Repository description and topics are set
- [ ] Code is committed and pushed to GitHub

## Post-Release Tasks

After publishing:

1. **Monitor downloads** - Check release statistics
2. **Respond to issues** - Address user feedback
3. **Update documentation** - Based on user questions
4. **Plan next release** - Based on feedback and roadmap

## Troubleshooting

### Binary too large
- Use UPX compression (already enabled in pyinstaller.spec)
- Consider splitting into installer + data files
- Use compression in release archives

### Users report missing DLLs
- Ensure Python DLL is included (already fixed)
- Test on clean Windows system
- Consider using `--onedir` instead of `--onefile` if issues persist

### Trial period not working
- Check `usage_limiter.py` is included in binary
- Verify installation info file is created correctly
- Test on fresh installation

## Additional Resources

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)
- [Creating Releases Best Practices](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

---

**Good luck with your release! 🚀**

