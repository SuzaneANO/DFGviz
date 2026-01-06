"""
Create Release Package
Compresses the binary and prepares release files for GitHub
"""
import os
import sys
import shutil
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime

def create_release():
    """Create release package - ONLY includes the executable, no other files"""
    script_dir = Path(__file__).parent
    dist_dir = script_dir / 'dist'
    releases_dir = script_dir / 'releases'
    releases_dir.mkdir(exist_ok=True)
    
    # Get version (you can modify this)
    version = "1.1.1"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Find executable - ONLY the executable will be included
    if sys.platform == 'win32':
        exe_name = 'DFGviz.exe'
        exe_path = dist_dir / exe_name
        if not exe_path.exists():
            print(f"Error: Executable not found: {exe_path}")
            return False
        
        # Create ZIP for Windows - ONLY the executable, no other files
        zip_path = releases_dir / f'DFGviz-windows-v{version}.zip'
        print(f"Creating Windows release: {zip_path}")
        print(f"  Including ONLY: {exe_name}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Only add the executable file, nothing else
            zipf.write(exe_path, arcname=exe_name)
        
        print(f"[OK] Created: {zip_path}")
        print(f"  Size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
        
    else:
        exe_name = 'DFGviz'
        exe_path = dist_dir / exe_name
        if not exe_path.exists():
            print(f"Error: Executable not found: {exe_path}")
            return False
        
        # Create tar.gz for Unix - ONLY the executable, no other files
        ext = 'tar.gz'
        archive_path = releases_dir / f'DFGviz-{sys.platform}-v{version}.{ext}'
        print(f"Creating {sys.platform} release: {archive_path}")
        print(f"  Including ONLY: {exe_name}")
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            # Only add the executable file, nothing else
            tar.add(exe_path, arcname=exe_name, recursive=False)
        
        print(f"[OK] Created: {archive_path}")
        print(f"  Size: {archive_path.stat().st_size / (1024*1024):.2f} MB")
    
    print(f"\n[OK] Release package created successfully!")
    print(f"  Location: {releases_dir}")
    print(f"  Note: Release contains ONLY the executable, no other files")
    return True

if __name__ == '__main__':
    create_release()

