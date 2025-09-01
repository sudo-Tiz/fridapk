#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for FridAPK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="fridapk",
    version="1.0.0",
    author="sudo-Tiz",
    description="Automatically patch Android APKs with Frida Gadget",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sudo-Tiz/fridapk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "frida>=16.0.0",
        "frida-tools>=12.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fridapk=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
