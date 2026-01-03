# Installing Clang/LLVM on Windows

## Quick Fix for Your Current Issue

The error you're seeing is because Chocolatey needs administrator privileges. Here are your options:

## Option 1: Run PowerShell as Administrator (Easiest)

1. **Close your current PowerShell window**
2. **Right-click on PowerShell** in Start Menu
3. **Select "Run as Administrator"**
4. **Run the installation command:**
   ```powershell
   choco install llvm -y
   ```
5. **After installation, set the environment variable:**
   ```powershell
   setx LIBCLANG_PATH "C:\Program Files\LLVM\bin\libclang.dll"
   ```
6. **Restart your terminal** (close and reopen PowerShell)

## Option 2: Manual Installation (No Admin Required)

If you don't want to use admin privileges:

1. **Download LLVM:**
   - Go to: https://github.com/llvm/llvm-project/releases
   - Download the latest Windows installer (e.g., `LLVM-XX.X.X-win64.exe`)

2. **Install to a user directory:**
   - Choose a location like `C:\Users\YourName\llvm` or `C:\llvm`
   - Make sure to check "Add LLVM to system PATH" during installation

3. **Set environment variable:**
   ```powershell
   setx LIBCLANG_PATH "C:\llvm\bin\libclang.dll"
   ```
   (Replace `C:\llvm` with your actual installation path)

4. **Restart your terminal**

## Option 3: Using winget (Windows 11/10)

If you have Windows 11 or Windows 10 with App Installer:

```powershell
winget install LLVM.LLVM
setx LIBCLANG_PATH "C:\Program Files\LLVM\bin\libclang.dll"
```

## Verify Installation

After installation, verify it works:

```powershell
# Check if libclang.dll exists
Test-Path "C:\Program Files\LLVM\bin\libclang.dll"

# Test Python bindings
python -c "from clang.cindex import Index; print('Clang OK!')"
```

## Troubleshooting

### If you get "Access Denied" errors:

1. **Check for lock files:**
   ```powershell
   # Remove any stale lock files (if they exist)
   Remove-Item "C:\ProgramData\chocolatey\lib\f6441487c4a652f0c98facae5fef474fa47c5c94" -ErrorAction SilentlyContinue
   ```

2. **Try manual installation instead** (Option 2 above)

### If LIBCLANG_PATH doesn't work:

1. **Check the actual path:**
   ```powershell
   Get-ChildItem "C:\Program Files\LLVM\bin\libclang.dll" -ErrorAction SilentlyContinue
   ```

2. **Set it for current session (temporary):**
   ```powershell
   $env:LIBCLANG_PATH = "C:\Program Files\LLVM\bin\libclang.dll"
   ```

3. **Or set it permanently via System Properties:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Add new System Variable: `LIBCLANG_PATH` = `C:\Program Files\LLVM\bin\libclang.dll`

## After Installation

Once Clang is installed, install the Python bindings:

```powershell
pip install clang
```

Then test the C++ analyzer:

```powershell
cd dataflow_analysis
python clang_complete_dataflow.py --file test_example.cpp
```


