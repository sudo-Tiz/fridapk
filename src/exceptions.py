#!/usr/bin/env python3
"""
FridAPK - Custom exception classes
"""


class FridAPKError(Exception):
    """Base exception for FridAPK errors"""

    pass


class DependencyError(FridAPKError):
    """Raised when required dependencies are missing"""

    pass


class APKError(FridAPKError):
    """Raised when APK operation fails"""

    pass


class GadgetError(FridAPKError):
    """Raised when Frida Gadget operation fails"""

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
