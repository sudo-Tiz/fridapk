#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Logger utility module
Provides consistent logging functionality
"""

import sys
from enum import IntEnum
from .colors import Colors


class VerbosityLevel(IntEnum):
    """Verbosity levels for logging"""
    LOW = 1     # only 'error' and 'done' messages
    MID = 2     # 'adding' messages too
    HIGH = 3    # all messages


class Logger:
    """Logger class for consistent output formatting"""
    
    def __init__(self, verbosity: VerbosityLevel = VerbosityLevel.HIGH):
        self.verbosity = verbosity
    
    def set_verbosity(self, verbosity: VerbosityLevel) -> None:
        """Set verbosity level"""
        self.verbosity = verbosity
    
    def info(self, msg: str) -> None:
        """Print info message"""
        if self.verbosity >= VerbosityLevel.HIGH:
            sys.stdout.write(f'{Colors.BLUE}[*] {msg}\n{Colors.ENDC}')
    
    def success(self, msg: str) -> None:
        """Print success message"""
        if self.verbosity >= VerbosityLevel.LOW:
            sys.stdout.write(f'{Colors.GREEN}[+] {msg}\n{Colors.ENDC}')
    
    def warning(self, msg: str) -> None:
        """Print warning message"""
        if self.verbosity >= VerbosityLevel.LOW:
            sys.stdout.write(f'{Colors.RED}[-] {msg}\n{Colors.ENDC}')
    
    def error(self, msg: str) -> None:
        """Print error message"""
        sys.stderr.write(f'{Colors.RED}[!] ERROR: {msg}\n{Colors.ENDC}')
    
    def debug(self, msg: str) -> None:
        """Print debug message"""
        if self.verbosity >= VerbosityLevel.HIGH:
            sys.stdout.write(f'{Colors.CYAN}[DEBUG] {msg}\n{Colors.ENDC}')
    
    def confirm(self, msg: str) -> bool:
        """Ask for user confirmation"""
        answer = input(f'{Colors.YELLOW}[?] {msg} (y/N): {Colors.ENDC}')
        return answer.lower() in ('y', 'yes')
    
    def critical_confirm(self, msg: str) -> bool:
        """Ask for critical confirmation"""
        answer = input(f'{Colors.RED}[!] {msg} (y/N) {Colors.ENDC}')
        return answer.lower() in ('y', 'yes')
