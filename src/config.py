#!/usr/bin/env python3
"""
FridAPK - Configuration settings
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


class Architecture:
    """Supported architectures"""

    ARM = "arm"
    ARM64 = "arm64"
    X86 = "x86"
    X64 = "x64"


class FileNames:
    """Default file names"""

    DEFAULT_GADGET = "libfrida-gadget.so"
    DEFAULT_CONFIG = "libfrida-gadget.config.so"
    DEFAULT_HOOKFILE = "libhook.js.so"
    KEYSTORE = "fridapkkeystore"
    NETWORK_SECURITY_CONFIG = "network_security_config.xml"


class Permissions:
    """Android permissions"""

    INTERNET = "android.permission.INTERNET"


class URLs:
    """API URLs"""

    FRIDA_RELEASES = "https://api.github.com/repos/frida/frida/releases"


@dataclass
class Config:
    """APK Patcher configuration"""

    # Paths - will be set in __post_init__
    gadgets_dir: Path = None
    temp_dir: Path = None

    # Dependencies
    required_tools: List[str] = None

    # Architecture mapping
    arch_mapping: Dict[str, str] = None

    # Lib directories for each architecture
    lib_dirs: Dict[str, List[str]] = None

    def __post_init__(self):
        # Set paths using environment variables with fallbacks
        if self.gadgets_dir is None:
            env_path = os.getenv("FRIDAPK_GADGETS_DIR")
            if env_path:
                self.gadgets_dir = Path(env_path)
            else:
                self.gadgets_dir = Path("/fridapk/gadgets")

        if self.temp_dir is None:
            env_path = os.getenv("FRIDAPK_TEMP_DIR")
            if env_path:
                self.temp_dir = Path(env_path)
            else:
                self.temp_dir = Path("/tmp/fridapk")
        if self.required_tools is None:
            self.required_tools = [
                "frida",
                "aapt",
                "adb",
                "apktool",
                "unxz",
                "keytool",
                "jarsigner",
                "zipalign",
                "apksigner",
            ]

        if self.arch_mapping is None:
            self.arch_mapping = {
                "armeabi": Architecture.ARM,
                "armeabi-v7a": Architecture.ARM,
                "arm64-v8a": Architecture.ARM64,
                "x86": Architecture.X86,
                "x86_64": Architecture.X64,
            }

        if self.lib_dirs is None:
            self.lib_dirs = {
                Architecture.ARM: ["armeabi", "armeabi-v7a"],
                Architecture.ARM64: ["arm64-v8a"],
                Architecture.X86: ["x86"],
                Architecture.X64: ["x86_64"],
            }

        # Create temp directory only (gadgets_dir already exists)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
