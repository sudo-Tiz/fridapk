#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Command Line Interface
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from utils.logger import Logger, VerbosityLevel
from utils.colors import Colors


class CLI:
    """Command Line Interface for FridAPK"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.logger = Logger()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            prog='fridapk',
            description='FridAPK - Automatically patch Android APKs with Frida Gadget',
            epilog='For detailed usage examples, visit: https://github.com/sudo-Tiz/fridapk',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Main arguments
        main_group = parser.add_argument_group('Main options')
        main_group.add_argument(
            '-a', '--apk',
            type=Path,
            help='APK file to patch',
            metavar='FILE'
        )
        
        main_group.add_argument(
            '-o', '--output',
            type=Path,
            help='Output file path for patched APK',
            metavar='FILE'
        )
        
        main_group.add_argument(
            '-v', '--verbosity',
            type=int,
            choices=[1, 2, 3],
            default=3,
            help='Verbosity level: 1=errors only, 2=+warnings, 3=all (default: 3)'
        )
        
        # Gadget options
        gadget_group = parser.add_argument_group('Frida Gadget options')
        gadget_group.add_argument(
            '-g', '--gadget',
            type=Path,
            help='Specific Frida gadget file to use',
            metavar='FILE'
        )
        
        gadget_group.add_argument(
            '--autoload-script',
            type=Path,
            help='JavaScript file to auto-load with gadget',
            metavar='FILE'
        )
        
        gadget_group.add_argument(
            '--prevent-gadget',
            action='store_true',
            help='Skip Frida gadget injection'
        )
        
        gadget_group.add_argument(
            '--update-gadgets',
            action='store_true',
            help='Download/update Frida gadgets for current Frida version'
        )
        
        # APK processing options
        processing_group = parser.add_argument_group('APK processing options')
        processing_group.add_argument(
            '-f', '--force-resources',
            action='store_true',
            help='Force extraction of resources and manifest'
        )
        
        processing_group.add_argument(
            '--use-aapt2',
            action='store_true',
            help='Use aapt2 with apktool for building'
        )
        
        processing_group.add_argument(
            '--enable-user-certs',
            action='store_true',
            help='Enable user certificate authorities in APK'
        )
        
        processing_group.add_argument(
            '-k', '--keep-keystore',
            action='store_true',
            help='Keep generated keystore for future use'
        )
        
        # Interactive options
        interactive_group = parser.add_argument_group('Interactive options')
        interactive_group.add_argument(
            '-w', '--wait',
            action='store_true',
            help='Wait for user confirmation before repackaging'
        )
        
        interactive_group.add_argument(
            '-x', '--exec-command',
            type=str,
            help='Execute shell command before repackaging',
            metavar='CMD'
        )
        
        interactive_group.add_argument(
            '--pass-temp-path',
            action='store_true',
            help='Pass temporary APK directory to --exec-command'
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse command line arguments"""
        parsed_args = self.parser.parse_args(args)
        
        # Set logger verbosity
        self.logger.set_verbosity(VerbosityLevel(parsed_args.verbosity))
        
        # Validate arguments
        self._validate_args(parsed_args)
        
        return parsed_args
    
    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate parsed arguments"""
        # If not updating gadgets, APK file is required
        if not args.update_gadgets and not args.apk:
            self.parser.error('APK file is required (use -a/--apk or --update-gadgets)')
        
        # Check if APK file exists
        if args.apk and not args.apk.exists():
            self.parser.error(f'APK file not found: {args.apk}')
        
        # Check if gadget file exists
        if args.gadget and not args.gadget.exists():
            self.parser.error(f'Gadget file not found: {args.gadget}')
        
        # Check if autoload script exists
        if args.autoload_script and not args.autoload_script.exists():
            self.parser.error(f'Autoload script not found: {args.autoload_script}')
        
        # Validate exec command options
        if args.pass_temp_path and not args.exec_command:
            self.parser.error('--pass-temp-path requires --exec-command')
    
    def print_banner(self) -> None:
        """Print application banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                          FridAPK                            ║
║              Frida Gadget injection made easy               ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.BLUE}✓{Colors.ENDC} Automatic Frida Gadget injection
{Colors.BLUE}✓{Colors.ENDC} User certificate authority support  
{Colors.BLUE}✓{Colors.ENDC} Auto-load JavaScript hooks
{Colors.BLUE}✓{Colors.ENDC} APK signing and alignment
"""
        print(banner)
    
    def handle_no_args(self) -> None:
        """Handle case when no arguments provided"""
        self.print_banner()
        print(f"\n{Colors.YELLOW}No arguments provided. Use -h/--help for usage information.{Colors.ENDC}")
        print(f"\n{Colors.BLUE}Quick start examples:{Colors.ENDC}")
        print(f"  {Colors.GREEN}fridapk -a app.apk{Colors.ENDC}                    # Patch with auto-detected gadget")
        print(f"  {Colors.GREEN}fridapk --update-gadgets{Colors.ENDC}             # Download latest gadgets")
        print(f"  {Colors.GREEN}fridapk -a app.apk --enable-user-certs{Colors.ENDC} # Enable user certificates")
        sys.exit(1)
