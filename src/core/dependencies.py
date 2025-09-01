#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Dependencies checker
"""

import subprocess
import shutil
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from exceptions import DependencyError
from utils.logger import Logger


@dataclass
class Dependency:
    """Represents a system dependency"""
    name: str
    command: str
    check_args: List[str]
    check_output_contains: Optional[str] = None
    required: bool = True
    description: str = ""


class DependencyChecker:
    """Manages and checks system dependencies"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.dependencies = self._init_dependencies()
    
    def _init_dependencies(self) -> Dict[str, Dependency]:
        """Initialize dependency definitions"""
        return {
            'frida': Dependency(
                name='Frida',
                command='frida',
                check_args=['--version'],
                description='Frida dynamic instrumentation toolkit'
            ),
            'aapt': Dependency(
                name='AAPT',
                command='aapt',
                check_args=['version'],
                description='Android Asset Packaging Tool'
            ),
            'adb': Dependency(
                name='ADB',
                command='adb',
                check_args=['--version'],
                description='Android Debug Bridge'
            ),
            'apktool': Dependency(
                name='APKTool',
                command='apktool',
                check_args=['--version'],
                description='APK reverse engineering tool'
            ),
            'unxz': Dependency(
                name='unxz',
                command='unxz',
                check_args=['--version'],
                description='XZ decompression utility'
            ),
            'keytool': Dependency(
                name='Keytool',
                command='keytool',
                check_args=['-help'],
                check_output_contains='Key and Certificate',
                description='Java keystore management tool'
            ),
            'jarsigner': Dependency(
                name='Jarsigner',
                command='jarsigner',
                check_args=['-help'],
                description='Java JAR signing tool'
            ),
            'zipalign': Dependency(
                name='Zipalign',
                command='zipalign',
                check_args=[],
                check_output_contains='zip alignment',
                description='Android APK alignment tool'
            ),
            'apksigner': Dependency(
                name='APKSigner',
                command='apksigner',
                check_args=['--help'],
                required=False,
                description='Android APK v2 signing tool'
            ),
        }
    
    def check_dependency(self, dep_name: str) -> Tuple[bool, str]:
        """Check if a single dependency is satisfied"""
        if dep_name not in self.dependencies:
            return False, f"Unknown dependency: {dep_name}"
        
        dep = self.dependencies[dep_name]
        
        # First check if command exists in PATH
        if not shutil.which(dep.command):
            return False, f"{dep.name} not found in PATH"
        
        try:
            # Run the check command
            result = subprocess.run(
                [dep.command] + dep.check_args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # For some commands, we need to check stderr instead of stdout
            output = result.stdout + result.stderr
            
            # Check if specific output is required
            if dep.check_output_contains:
                if dep.check_output_contains.lower() not in output.lower():
                    return False, f"{dep.name} found but not working correctly"
            
            return True, f"{dep.name} is available"
            
        except subprocess.TimeoutExpired:
            return False, f"{dep.name} check timed out"
        except subprocess.SubprocessError as e:
            return False, f"{dep.name} check failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error checking {dep.name}: {str(e)}"
    
    def check_all_dependencies(self, required_only: bool = False) -> Dict[str, Tuple[bool, str]]:
        """Check all dependencies"""
        results = {}
        
        self.logger.info('Checking dependencies...')
        
        for dep_name, dep in self.dependencies.items():
            if required_only and not dep.required:
                continue
            
            is_satisfied, message = self.check_dependency(dep_name)
            results[dep_name] = (is_satisfied, message)
            
            if is_satisfied:
                self.logger.debug(f"✓ {dep.name}: {message}")
            else:
                self.logger.warning(f"✗ {dep.name}: {message}")
        
        return results
    
    def ensure_dependencies(self, required_deps: List[str] = None) -> bool:
        """Ensure required dependencies are satisfied"""
        if required_deps is None:
            required_deps = [name for name, dep in self.dependencies.items() if dep.required]
        
        results = {}
        for dep_name in required_deps:
            if dep_name in self.dependencies:
                results[dep_name] = self.check_dependency(dep_name)
        
        failed_deps = [name for name, (satisfied, _) in results.items() if not satisfied]
        
        if failed_deps:
            error_msg = f"Missing required dependencies: {', '.join(failed_deps)}"
            self.logger.error(error_msg)
            self._print_installation_help(failed_deps)
            raise DependencyError(error_msg)
        
        return True
    
    def _print_installation_help(self, failed_deps: List[str]) -> None:
        """Print installation help for failed dependencies"""
        self.logger.info("Installation help:")
        
        help_text = {
            'frida': 'pip3 install frida frida-tools',
            'apktool': 'Download from https://ibotpeaches.github.io/Apktool/install/',
            'aapt': 'Install Android SDK Build Tools',
            'adb': 'Install Android SDK Platform Tools',
            'zipalign': 'Install Android SDK Build Tools',
            'unxz': 'apt-get install xz-utils (Ubuntu/Debian) or brew install xz (macOS)',
            'keytool': 'Install Java JDK',
            'jarsigner': 'Install Java JDK',
        }
        
        for dep in failed_deps:
            if dep in help_text:
                self.logger.info(f"  {dep}: {help_text[dep]}")
