#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Colors utility module
Provides color constants for terminal output
"""

class Colors:
    """Terminal color constants"""
    
    # Basic colors
    BLUE = '\033[94m'
    RED = '\033[91m'
    RED_BG = '\033[101m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Reset
    ENDC = '\033[0m'
    
    # Semantic colors
    HEADER = MAGENTA
    OKBLUE = BLUE
    OKGREEN = GREEN
    WARNING = YELLOW
    FAIL = RED
