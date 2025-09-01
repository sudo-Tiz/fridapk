#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FridAPK - Custom exceptions
"""


class APKPatcherError(Exception):
    """Base exception for FridAPK"""
    pass


class DependencyError(APKPatcherError):
    """Raised when a required dependency is missing"""
    pass


class APKError(APKPatcherError):
    """Raised when APK processing fails"""
    pass


class GadgetError(APKPatcherError):
    """Raised when Frida gadget operations fail"""
    pass


class ExtractionError(APKError):
    """Raised when APK extraction fails"""
    pass


class RepackageError(APKError):
    """Raised when APK repackaging fails"""
    pass


class SigningError(APKError):
    """Raised when APK signing fails"""
    pass
