#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, find_namespace_packages
from pathlib import Path
import sys
import os

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from script/version.py
version = {}
version_file = this_directory / "script" / "version.py"
with version_file.open("r", encoding="utf-8") as f:
    exec(f.read(), version)

# Get the version
version_str = version.get('__version__', '0.0.1')

# Define base requirements
install_requires = [
    'PySide6>=6.5.0,<7.0.0',
    'wand>=0.6.10,<0.7.0',
    'pywin32>=306,<308; platform_system == "Windows"',
    'psutil>=5.9.5,<6.0.0',
    'py-cpuinfo>=9.0.0,<10.0.0',
    'wmi>=1.5.1,<2.0.0; platform_system == "Windows"',
    'numpy>=2.0.2,<3.0.0',
    'pandas>=2.0.0,<3.0.0',
    'matplotlib>=3.7.0,<4.0.0',
    'requests>=2.31.0,<3.0.0',
    'python-dateutil>=2.8.2,<3.0.0',
]

# Development dependencies
extras_require = {
    'dev': [
        'pytest>=7.0.0,<8.0.0',
        'pytest-cov>=4.0.0,<5.0.0',
        'black>=23.0.0,<24.0.0',
        'flake8>=6.0.0,<7.0.0',
        'mypy>=1.0.0,<2.0.0',
        'isort>=5.12.0,<6.0.0',
    ],
}

# Entry points
entry_points = {
    'console_scripts': [
        'pybench=main:main',
    ],
    'gui_scripts': [
        'pybench-gui=main:main',
    ],
}

# Get all package data files
def get_package_data():
    package_data = {
        '': ['*.md', '*.txt', '*.json'],
        'assets': ['*'],
        'lang': ['*.json'],
    }
    
    # Add all files in the script directory
    for root, _, files in os.walk('script'):
        if '__pycache__' in root or '.pytest_cache' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.ui', '.qss', '.png', '.ico', '.icns')):
                rel_path = os.path.relpath(root, 'script')
                if rel_path == '.':
                    rel_path = ''
                if rel_path not in package_data:
                    package_data[rel_path] = ['*']
    
    return package_data

setup(
    name="nsfr750-pybench",
    version=version_str,
    author="Nsfr750",
    author_email="nsfr750@yandex.com",
    description="A comprehensive benchmarking tool with a modern GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750/benchmark",
    packages=find_namespace_packages(include=['script*', 'test*']),
    package_dir={'': '.'},
    package_data=get_package_data(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Benchmark",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires='>=3.8',
    license="GPLv3",
    keywords="benchmark system performance monitoring",
    project_urls={
        'Bug Reports': 'https://github.com/Nsfr750/benchmark/issues',
        'Source': 'https://github.com/Nsfr750/benchmark',
        'Documentation': 'https://github.com/Nsfr750/benchmark/wiki',
    },
    options={
        'build_exe': {
            'packages': ['PySide6', 'wand', 'numpy', 'pandas', 'matplotlib'],
            'include_files': [
                'assets/',
                'lang/',
                'LICENSE',
                'README.md',
                'CHANGELOG.md',
            ],
            'excludes': ['tkinter'],
        },
    },
)

# Windows-specific configurations (only if cx_Freeze is available)
try:
    if sys.platform == 'win32':
        from cx_Freeze import setup as cx_setup, Executable
        
        base = 'Win32GUI'
        
        executables = [
            Executable(
                'main.py',
                base=base,
                target_name='PyBench.exe',
                icon='assets/icon.ico',
                shortcut_name="PyBench",
                shortcut_dir="DesktopFolder"
            )
        ]
        
        # Only run cx_Freeze setup if this is a build command
        if 'build' in sys.argv or 'bdist_msi' in sys.argv:
            cx_setup(
                name="PyBench",
                version=version.get('__version__', '1.3.0.0'),
                description="A comprehensive benchmarking tool",
                executables=executables,
                options={
                    'build_exe': {
                        'packages': ['PySide6', 'wand', 'numpy', 'pandas', 'matplotlib'],
                        'include_files': [
                            'assets/',
                            'lang/',
                            'LICENSE',
                            'README.md',
                            'CHANGELOG.md',
                        ],
                        'excludes': ['tkinter'],
                    },
                    'bdist_msi': {
                        'upgrade_code': '{6F8D2D9F-1234-5678-9ABC-DEF012345678}',
                        'add_to_path': False,
                        'initial_target_dir': r'[ProgramFilesFolder]\\\\PyBench',
                        'install_icon': 'assets/icon.ico',
                    },
                },
            )
except ImportError:
    # cx_Freeze is not installed, skip Windows-specific setup
    if 'build' in sys.argv or 'bdist_msi' in sys.argv:
        print("Warning: cx_Freeze is not installed. Windows executable cannot be built.")
        print("Install it with: pip install cx_Freeze")
