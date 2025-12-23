"""iOS device control module for AutoGLM middleware.

This module provides iOS device control capabilities through WebDriverAgent
and libimobiledevice.
"""

from .connection import XCTestConnection, list_devices, check_libimobiledevice, is_wda_ready
from .device import (
    tap,
    double_tap,
    long_press,
    swipe,
    home,
    back,
    launch_app,
    get_current_app,
)
from .screenshot import get_screenshot
from .input import type_text, clear_text

__all__ = [
    # Connection
    "XCTestConnection",
    "list_devices",
    "check_libimobiledevice",
    "is_wda_ready",
    # Device control
    "tap",
    "double_tap",
    "long_press",
    "swipe",
    "home",
    "back",
    "launch_app",
    "get_current_app",
    # Screenshot
    "get_screenshot",
    # Input
    "type_text",
    "clear_text",
]
