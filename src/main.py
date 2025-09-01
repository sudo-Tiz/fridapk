#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK v2.0 - Main application
"""

import signal
import sys
import subprocess
import shutil
from pathlib import Path

from cli import CLI
from config import Config
from core.dependencies import DependencyChecker
from core.gadgets import GadgetManager
from core.apk_processor import APKProcessor
from exceptions import APKPatcherError
from utils.logger import Logger, VerbosityLevel


class FridAPK:
    """Main FridAPK application"""
    
    def __init__(self):
        self.cli = CLI()
        self.logger = Logger()
        self.config = Config()
        self.dep_checker = DependencyChecker(self.logger)
        self.gadget_manager = GadgetManager(self.logger, self.config)
        self.apk_processor = APKProcessor(self.logger, self.config)
    
    def run(self, args=None):
        """Run the application"""
        try:
            # Setup signal handler
            signal.signal(signal.SIGINT, self._signal_handler)
            
            # Parse arguments
            if not args and len(sys.argv) == 1:
                self.cli.handle_no_args()
                return 1
            
            parsed_args = self.cli.parse_args(args)
            
            # Update logger verbosity
            self.logger.set_verbosity(VerbosityLevel(parsed_args.verbosity))
            
            # Handle gadget updates
            if parsed_args.update_gadgets:
                return self._handle_update_gadgets()
            
            # Check dependencies
            required_deps = ['frida', 'aapt', 'adb', 'apktool']
            if not parsed_args.prevent_gadget:
                required_deps.append('unxz')
            
            self.dep_checker.ensure_dependencies(required_deps)
            
            # Process APK
            return self._process_apk(parsed_args)
            
        except KeyboardInterrupt:
            self.logger.warning("Operation cancelled by user")
            return 1
        except APKPatcherError as e:
            self.logger.error(str(e))
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if parsed_args and parsed_args.verbosity >= 3:
                import traceback
                self.logger.debug(traceback.format_exc())
            return 1
    
    def _handle_update_gadgets(self) -> int:
        """Handle gadget updates"""
        try:
            if self.gadget_manager.update_gadgets():
                self.logger.success("Gadgets updated successfully")
                return 0
            else:
                return 1
        except Exception as e:
            self.logger.error(f"Failed to update gadgets: {e}")
            return 1
    
    def _process_apk(self, args) -> int:
        """Process APK with given arguments"""
        apk_path = Path(args.apk)
        
        # Create temp directory
        temp_dir = self.apk_processor.create_temp_folder(apk_path)
        
        try:
            # Determine if we need to extract resources
            needs_resources = (
                args.force_resources or 
                args.enable_user_certs or
                (not args.prevent_gadget and not self.apk_processor.has_permission(apk_path, 'android.permission.INTERNET'))
            )
            
            # Extract APK
            self.apk_processor.extract_apk(apk_path, temp_dir, needs_resources)
            
            # Add Internet permission if needed
            if not args.prevent_gadget and not self.apk_processor.has_permission(apk_path, 'android.permission.INTERNET'):
                self._inject_internet_permission(temp_dir)
            
            # Enable user certificates if requested
            if args.enable_user_certs:
                self._enable_user_certificates(temp_dir)
            
            # Inject Frida gadget if not prevented
            if not args.prevent_gadget:
                success = self._inject_frida_gadget(args, apk_path, temp_dir)
                if not success:
                    return 1
            
            # Execute custom command if provided
            if args.exec_command:
                if not self._execute_custom_command(args, temp_dir):
                    return 1
            
            # Wait for user confirmation if requested
            if args.wait:
                self.logger.info('Waiting for your confirmation to repackage...')
                if not self.logger.confirm('Ready to repackage?'):
                    self.logger.info('Operation cancelled')
                    return 1
            
            # Determine output path
            output_path = args.output or apk_path.with_stem(f"{apk_path.stem}_patched")
            
            # Repackage APK
            final_apk = self.apk_processor.repackage_apk(temp_dir, output_path, args.use_aapt2)
            
            # Sign and align
            self.apk_processor.sign_and_align_apk(final_apk, args.keep_keystore)
            
            # Success
            self.logger.success(f'Patched APK created: {final_apk}')
            self.logger.success(f'Temporary files at: {temp_dir}')
            
            return 0
            
        except Exception as e:
            self.logger.error(f"APK processing failed: {e}")
            return 1
    
    def _inject_internet_permission(self, temp_dir: Path) -> None:
        """Inject INTERNET permission into AndroidManifest.xml"""
        manifest_path = temp_dir / 'AndroidManifest.xml'
        
        if not manifest_path.exists():
            raise APKPatcherError("AndroidManifest.xml not found")
        
        self.logger.info("Injecting INTERNET permission...")
        
        # Read manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find manifest tag
        manifest_start = content.find('<manifest ')
        if manifest_start == -1:
            raise APKPatcherError("Invalid AndroidManifest.xml format")
        
        manifest_end = content.find('>', manifest_start)
        if manifest_end == -1:
            raise APKPatcherError("Invalid AndroidManifest.xml format")
        
        # Insert permission
        permission_tag = '    <uses-permission android:name="android.permission.INTERNET"/>'
        new_content = (
            content[:manifest_end + 1] + '\n' +
            permission_tag + '\n' +
            content[manifest_end + 1:]
        )
        
        # Write back
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        self.logger.success("INTERNET permission added")
    
    def _enable_user_certificates(self, temp_dir: Path) -> None:
        """Enable user certificate authorities"""
        self.logger.info("Enabling user certificate authorities...")
        
        # Create network security config
        self._create_network_security_config(temp_dir)
        
        # Update manifest
        self._inject_network_security_config(temp_dir)
        
        self.logger.success("User certificates enabled")
    
    def _create_network_security_config(self, temp_dir: Path) -> None:
        """Create network security configuration file"""
        xml_dir = temp_dir / 'res' / 'xml'
        xml_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = xml_dir / 'network_security_config.xml'
        
        if config_path.exists():
            self.logger.warning("network_security_config.xml already exists!")
            with open(config_path, 'r') as f:
                self.logger.info(f"Original content:\n{f.read()}")
            
            if not self.logger.confirm("Replace existing file?"):
                return
        
        config_content = '''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
'''
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        self.logger.info("Network security config created")
    
    def _inject_network_security_config(self, temp_dir: Path) -> None:
        """Inject network security config reference into manifest"""
        manifest_path = temp_dir / 'AndroidManifest.xml'
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Find application tag
        app_start = content.find('<application ')
        if app_start == -1:
            raise APKPatcherError("No <application> tag found in manifest")
        
        app_end = content.find('>', app_start)
        if app_end == -1:
            raise APKPatcherError("Invalid <application> tag in manifest")
        
        # Check if already has network security config
        if 'networkSecurityConfig' in content[app_start:app_end]:
            self.logger.warning("Application already has networkSecurityConfig")
            return
        
        # Insert attribute
        new_content = (
            content[:app_end] +
            ' android:networkSecurityConfig="@xml/network_security_config"' +
            content[app_end:]
        )
        
        with open(manifest_path, 'w') as f:
            f.write(new_content)
        
        self.logger.info("Network security config reference added to manifest")
    
    def _inject_frida_gadget(self, args, apk_path: Path, temp_dir: Path) -> bool:
        """Inject Frida gadget into APK"""
        try:
            # Get gadget to use
            if args.gadget:
                gadget_path = args.gadget
                self.logger.info(f"Using specified gadget: {gadget_path}")
            else:
                gadget_path = self.gadget_manager.get_recommended_gadget()
                if not gadget_path:
                    self.logger.error("Could not find appropriate Frida gadget")
                    return False
            
            # Get main activity
            main_activity = self.apk_processor.get_main_activity(apk_path)
            if not main_activity:
                return False
            
            # Find smali file
            smali_path = self._find_smali_file(temp_dir, main_activity)
            if not smali_path:
                return False
            
            # Inject loader code
            self._inject_frida_loader(smali_path)
            
            # Copy gadget files
            self._copy_gadget_files(temp_dir, gadget_path, args.autoload_script)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Gadget injection failed: {e}")
            return False
    
    def _find_smali_file(self, temp_dir: Path, activity_class: str) -> Path:
        """Find smali file for given activity class"""
        smali_path = activity_class.replace('.', '/') + '.smali'
        
        # Search in smali directories
        for smali_dir in temp_dir.glob('smali*'):
            candidate = smali_dir / smali_path
            if candidate.exists():
                self.logger.info(f"Found smali file: {candidate}")
                return candidate
        
        self.logger.error(f"Could not find smali file for {activity_class}")
        return None
    
    def _inject_frida_loader(self, smali_path: Path) -> None:
        """Inject Frida loader code into smali file"""
        with open(smali_path, 'r') as f:
            content = f.read()
        
        if 'frida-gadget' in content:
            self.logger.info("Frida loader already present, skipping injection")
            return
        
        # Find injection point
        direct_methods_start = content.find('# direct methods')
        if direct_methods_start == -1:
            raise APKPatcherError("Could not find direct methods section")
        
        # Look for existing class constructor
        clinit_start = content.find('.method static constructor <clinit>()V', direct_methods_start)
        
        if clinit_start == -1:
            # No existing constructor, create one
            injection_code = '''
.method static constructor <clinit>()V
    .locals 1

    .prologue
    const-string v0, "frida-gadget"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method
'''
            # Insert after direct methods comment
            direct_methods_end = content.find('\n', direct_methods_start)
            new_content = (
                content[:direct_methods_end + 1] +
                injection_code +
                content[direct_methods_end + 1:]
            )
        else:
            # Existing constructor, inject into it
            prologue_pos = content.find('.prologue', clinit_start)
            if prologue_pos == -1:
                raise APKPatcherError("Could not find .prologue in class constructor")
            
            prologue_end = content.find('\n', prologue_pos) + 1
            
            injection_code = '''    const-string v0, "frida-gadget"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

'''
            
            new_content = (
                content[:prologue_end] +
                injection_code +
                content[prologue_end:]
            )
        
        with open(smali_path, 'w') as f:
            f.write(new_content)
        
        self.logger.success("Frida loader injected into smali file")
    
    def _copy_gadget_files(self, temp_dir: Path, gadget_path: Path, autoload_script: Path = None) -> None:
        """Copy Frida gadget and related files to APK"""
        # Determine architecture and create lib directories
        arch = self._get_arch_from_gadget(gadget_path.name)
        lib_dirs = self._create_lib_directories(temp_dir, arch)
        
        for lib_dir in lib_dirs:
            # Copy gadget
            target_gadget = lib_dir / 'libfrida-gadget.so'
            shutil.copy2(gadget_path, target_gadget)
            self.logger.info(f"Copied gadget to {target_gadget}")
            
            # Copy autoload script if provided
            if autoload_script:
                target_script = lib_dir / 'libhook.js.so'
                shutil.copy2(autoload_script, target_script)
                self.logger.info(f"Copied autoload script to {target_script}")
                
                # Create config file for autoload
                config_content = '''
{
    "interaction": {
        "type": "script",
        "address": "127.0.0.1",
        "port": 27042,
        "path": "./libhook.js.so"
    }
}
'''
                target_config = lib_dir / 'libfrida-gadget.config.so'
                with open(target_config, 'w') as f:
                    f.write(config_content.strip())
                self.logger.info(f"Created config file at {target_config}")
    
    def _get_arch_from_gadget(self, filename: str) -> str:
        """Determine architecture from gadget filename"""
        filename = filename.lower()
        
        if 'arm64' in filename:
            return 'arm64'
        elif 'arm' in filename:
            return 'arm'
        elif 'x86_64' in filename:
            return 'x86_64'
        elif 'i386' in filename or 'x86' in filename:
            return 'x86'
        
        return 'arm'  # default fallback
    
    def _create_lib_directories(self, temp_dir: Path, arch: str) -> list:
        """Create lib directories for the given architecture"""
        lib_base = temp_dir / 'lib'
        lib_base.mkdir(exist_ok=True)
        
        arch_mapping = {
            'arm': ['armeabi', 'armeabi-v7a'],
            'arm64': ['arm64-v8a'],
            'x86': ['x86'],
            'x86_64': ['x86_64']
        }
        
        dirs = []
        for dir_name in arch_mapping.get(arch, ['armeabi-v7a']):
            lib_dir = lib_base / dir_name
            lib_dir.mkdir(exist_ok=True)
            dirs.append(lib_dir)
            self.logger.info(f"Created lib directory: {lib_dir}")
        
        return dirs
    
    def _execute_custom_command(self, args, temp_dir: Path) -> bool:
        """Execute custom command before repackaging"""
        command = args.exec_command
        
        if args.pass_temp_path:
            if 'TMP_PATH_HERE' in command:
                command = command.replace('TMP_PATH_HERE', str(temp_dir))
            else:
                command = f"{command} {temp_dir}"
        
        self.logger.warning(f"About to execute: {command}")
        if not self.logger.critical_confirm("Execute this command?"):
            return False
        
        try:
            self.logger.info(f"Executing: {command}")
            result = subprocess.run(command, shell=True, cwd=temp_dir)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return False
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        self.logger.warning("\nOperation cancelled by user")
        sys.exit(1)


def main():
    """Main entry point"""
    patcher = FridAPK()
    return patcher.run()


if __name__ == '__main__':
    sys.exit(main())
