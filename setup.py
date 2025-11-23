#!/usr/bin/env python3
"""
Video Downloader - Instalator
Automatyczne pobieranie i konwersja wideo z monitorowaniem czatów
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="video-downloader",
    version="1.0.0",
    author="Video Downloader Team",
    description="Zaawansowany system pobierania i konwersji wideo z monitorowaniem czatów",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/video-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyperclip>=1.9.0",
        "requests>=2.32.0",
        "schedule>=1.2.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "video-downloader=main:main",
            "vd-diagnostics=system_diagnostics:main",
            "vd-test=comprehensive_test:run_comprehensive_tests",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
