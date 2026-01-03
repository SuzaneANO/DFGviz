# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Find Python DLL for Windows
binaries_list = []
if sys.platform == "win32":
    python_exe = sys.executable
    python_dir = os.path.dirname(python_exe)
    
    # Try to find python313.dll or python3.dll
    for dll_name in ['python313.dll', 'python3.dll', 'python.dll']:
        dll_path = os.path.join(python_dir, dll_name)
        if os.path.exists(dll_path):
            binaries_list.append((dll_path, '.'))
            break
    
    # Also check DLLs subdirectory
    if not binaries_list:
        dlls_dir = os.path.join(os.path.dirname(python_dir), 'DLLs')
        if os.path.exists(dlls_dir):
            for dll_name in ['python313.dll', 'python3.dll', 'python.dll']:
                dll_path = os.path.join(dlls_dir, dll_name)
                if os.path.exists(dll_path):
                    binaries_list.append((dll_path, '.'))
                    break

a = Analysis(
    ['git_history_dataflow_analyzer.py'],
    pathex=[],
    binaries=binaries_list,
    datas=[
        ('generate_interactive_dataflow.py', '.'),
        ('scalpel_complete_dataflow.py', '.'),
        ('clang_complete_dataflow.py', '.'),
        ('cmake_parser.py', '.'),
        ('usage_limiter.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'scalpel',
        'scalpel.cfg',
        'scalpel.core.mnode',
        'scalpel.ssa',
        'clang',
        'clang.cindex',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DFGviz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
