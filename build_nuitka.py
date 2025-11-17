#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuitka Build Script for Bencmark

This script compiles the Benchmark application into a standalone executable using Nuitka.
It handles all necessary dependencies, data files, and platform-specific configurations.

Usage:
    python build_nuitka.py [--clean] [--onefile] [--windows-disable-console] [--include-qt-plugins]

Options:
    --clean                Clean build directory before building
    --onefile              Create a single executable file
    --windows-disable-console  Disable console window (Windows only)
    --include-qt-plugins   Include additional Qt plugins (may increase size)
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from script.version import __version__

# Get version from version.py
from script.version import __version__

# Project information
APP_NAME = "PyBench"
VERSION = __version__
AUTHOR = "Nsfr750"

# Build configuration
BUILD_DIR = Path("build")
DIST_DIR = Path("dist")
LANG_DIR = "lang"
DOCS_DIR = "docs"

# Get version from version.py and ensure it's in Windows version format (X.Y.Z.W)
try:
    version = {}
    with open("script/version.py", "r") as f:
        exec(f.read(), version)
    # Convert version to Windows format (X.Y.Z.W)
    version_parts = version["__version__"].replace('-', '.').split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    VERSION = '.'.join(version_parts[:4])  # Take first 4 parts
except Exception as e:
    print(f"Error reading version from script/version.py: {e}")
    VERSION = "1.3.0.0"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME} with Nuitka")
    parser.add_argument("--clean", action="store_true", help="Clean build directory before building")
    parser.add_argument("--windows-disable-console", action="store_true", 
                        help="Disable console window (Windows only)")
    parser.add_argument("--onefile", action="store_true", 
                        help="Create a single executable file")
    return parser.parse_args()

def clean_build():
    """Clean build and dist directories."""
    print("Cleaning build directories...")
    for dir_name in ['build', 'dist', f'{APP_NAME}.spec']:
        if os.path.exists(dir_name):
            try:
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                else:
                    os.remove(dir_name)
                print(f"Removed {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {e}")

def get_nuitka_command(args):
    """Build the Nuitka command based on arguments."""
    # Ensure required directories exist
    os.makedirs('lang', exist_ok=True)
    os.makedirs('assets', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    # Base command with minimal required options
    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",
        "--onefile",
        f"--jobs={os.cpu_count() or 1}",
        "--windows-console-mode=disable",
        f"--output-dir={DIST_DIR}",
        f"--output-filename={APP_NAME}-{VERSION}",
        "--file-description=A Benchmark Tool",
        "--windows-icon-from-ico=assets/icon.ico",
        "--windows-company-name=Tuxxle",
        f"--windows-product-name={APP_NAME}",
        f"--windows-file-version={VERSION}",
        f"--windows-product-version={VERSION}",
        "--windows-uac-admin",
        "--copyright=© 2025 Nsfr750 - All Rights Reserved",
        "--enable-plugin=pyside6",
        # Include data files
        "--include-package-data=script",
        # Include assets
        "--include-data-dir=assets=assets",
        # Include config
        "--include-data-files=./config/config.json=./config/config.json",
        # Include packages
        "--include-package=send2trash",
        "--include-package=psutil",
        "--include-package=tqdm",
        # Other options
        "--assume-yes-for-downloads",
        "--follow-imports",
        "--follow-import-to=script",
        "--show-progress",
        "main.py"
    ]
    
    # Filter out any empty strings from the command
    return [x for x in cmd if x]

def build():
    """Build the application with Nuitka."""
    args = parse_arguments()
    
    # Set default for onefile if not provided
    if not hasattr(args, 'onefile'):
        args.onefile = True  # Default to onefile for easier distribution
    
    if args.clean:
        clean_build()
    
    # Create necessary directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    # Build the command
    cmd = get_nuitka_command(args)
    
    print("Running command:", " ".join(cmd))
    
    # Run the command
    try:
        subprocess.check_call(cmd)
        print("\nBuild completed successfully!")
        
        if args.onefile:
            # Check if the build was successful
            exe_name = f"{APP_NAME}-{VERSION}.exe"
            built_exe = DIST_DIR / f"{APP_NAME}-{VERSION}.exe"
            
            if built_exe.exists():
                print(f"[SUCCESS] Build completed! Executable: {built_exe}")
                return True
            else:
                print("[ERROR] Build failed - output executable not found!")
                if (BUILD_DIR / f"{APP_NAME}.build").exists():
                    print("[INFO] Build directory exists, but no executable was created.")
                return False
        
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
