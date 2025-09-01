#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Configuration and constants
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List


class Architecture:
    """Supported architectures"""
    ARM = 'arm'
    ARM64 = 'arm64'
    X86 = 'x86'
    X64 = 'x64'


class FileNames:
    """Default file names"""
    DEFAULT_GADGET = 'libfrida-gadget.so'
    DEFAULT_CONFIG = 'libfrida-gadget.config.so'
    DEFAULT_HOOKFILE = 'libhook.js.so'
    KEYSTORE = 'fridapkkeystore'
    NETWORK_SECURITY_CONFIG = 'network_security_config.xml'


class Permissions:
    """Android permissions"""
    INTERNET = 'android.permission.INTERNET'


class URLs:
    """API URLs"""
    FRIDA_RELEASES = 'https://api.github.com/repos/frida/frida/releases'


@dataclass
class Config:
    """APK Patcher configuration"""
    
    # Paths
    gadgets_dir: Path = Path(__file__).parent.parent.parent / 'gadgets'
    temp_dir: Path = Path('/tmp/apkptmp')
    
    # Dependencies
    required_tools: List[str] = None
    
    # Architecture mapping
    arch_mapping: Dict[str, str] = None
    
    # Lib directories for each architecture
    lib_dirs: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.required_tools is None:
            self.required_tools = [
                'frida', 'aapt', 'adb', 'apktool', 'unxz',
                'keytool', 'jarsigner', 'zipalign', 'apksigner'
            ]
        
        if self.arch_mapping is None:
            self.arch_mapping = {
                'armeabi': Architecture.ARM,
                'armeabi-v7a': Architecture.ARM,
                'arm64-v8a': Architecture.ARM64,
                'x86': Architecture.X86,
                'x86_64': Architecture.X64,
            }
        
        if self.lib_dirs is None:
            self.lib_dirs = {
                Architecture.ARM: ['armeabi', 'armeabi-v7a'],
                Architecture.ARM64: ['arm64-v8a'],
                Architecture.X86: ['x86'],
                Architecture.X64: ['x86_64'],
            }
        
        # Create directories
        self.gadgets_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
