# FridAPK Core functionality

from .apk_processor import APKProcessor
from .dependencies import DependencyChecker
from .gadgets import GadgetManager

__all__ = ["DependencyChecker", "GadgetManager", "APKProcessor"]
