#!/usr/bin/env python3
"""
DEEPINTEL VIDEO SUITE - Quick Build
Build EXE immediately without stress tests
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_basic_tests():
    """Run basic tests"""
    print("RUNNING BASIC TESTS...")
    
    test_commands = [
        [sys.executable, "-c", "import main; print('Main module OK')"],
        [sys.executable, "-c", "import download_manager; print('Download manager OK')"],
        [sys.executable, "-c", "import error_handler; print('Error handler OK')"]
    ]
    
    for cmd in test_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"  PASS - {cmd[2]}")
            else:
                print(f"  FAIL - {cmd[2]}")
                return False
        except Exception as e:
            print(f"  FAIL - {cmd[2]} - {e}")
            return False
    
    print("ALL TESTS PASSED")
    return True

def build_executable():
    """Build the executable"""
    print("\nBUILDING EXECUTABLE...")
    
    # Clean previous builds
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Use full path to PyInstaller
    pyinstaller_path = r"C:\Users\sttpi\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe"
    
    build_cmd = [
        pyinstaller_path,
        '--name=DeepIntel_Video_Suite',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        'main.py'
    ]
    
    try:
        print("Starting PyInstaller...")
        result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("BUILD SUCCESSFUL")
            return True
        else:
            print(f"BUILD FAILED: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("BUILD TIMEOUT")
        return False
    except Exception as e:
        print(f"BUILD ERROR: {e}")
        return False

def verify_and_package():
    """Verify and create distribution"""
    print("\nVERIFYING AND PACKAGING...")
    
    exe_path = Path('dist') / 'DeepIntel_Video_Suite.exe'
    
    if not exe_path.exists():
        print("ERROR: Executable not found")
        return None
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"Executable size: {size_mb:.1f} MB")
    
    # Create distribution
    dist_dir = Path('Distribution')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy executable
    shutil.copy2(exe_path, dist_dir / 'DeepIntel_Video_Suite.exe')
    
    # Create README
    readme_content = '''DEEPINTEL VIDEO SUITE
Professional Video Downloader & Converter

INSTALLATION:
1. Run DeepIntel_Video_Suite.exe
2. No installation required
3. Start downloading videos!

SUPPORT: support@deepintel.com
LICENSE: Commercial - $19-49
'''
    
    with open(dist_dir / 'README.txt', 'w') as f:
        f.write(readme_content)
    
    print("Distribution package created")
    return exe_path

def main():
    """Main build process"""
    print("DEEPINTEL VIDEO SUITE - QUICK BUILD")
    print("=" * 50)
    
    # Step 1: Basic tests
    if not run_basic_tests():
        print("\nTESTS FAILED")
        return
    
    # Step 2: Build
    if not build_executable():
        print("\nBUILD FAILED")
        return
    
    # Step 3: Verify
    exe_path = verify_and_package()
    
    if exe_path:
        print("\n" + "=" * 50)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Executable: {exe_path}")
        print("Distribution folder: Distribution/")
        print("\nREADY FOR COMMERCIAL RELEASE!")
    else:
        print("\nBUILD FAILED")

if __name__ == "__main__":
    main()