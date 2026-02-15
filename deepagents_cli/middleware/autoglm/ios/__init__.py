"""iOS device control module for AutoGLM middleware.

This module provides iOS device control capabilities through WebDriverAgent
and libimobiledevice.
"""

from .connection import (
    XCTestConnection,
    check_libimobiledevice,
    is_wda_ready,
    list_devices,
)
from .device import (
    back,
    double_tap,
    get_current_app,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
)
from .input import clear_text, type_text
from .screenshot import get_screenshot

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
