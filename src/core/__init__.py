# FridAPK Core functionality

from .dependencies import DependencyChecker
from .gadgets import GadgetManager
from .apk_processor import APKProcessor

__all__ = ['DependencyChecker', 'GadgetManager', 'APKProcessor']
