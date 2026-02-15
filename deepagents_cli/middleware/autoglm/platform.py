"""Platform abstraction layer for Android and iOS device control.

This module provides a unified interface for controlling both Android and iOS devices,
abstracting platform-specific implementations behind a common Protocol.
"""

from dataclasses import dataclass
from typing import Protocol

from . import adb_controller
from .adb_controller import Screenshot
from .ios import (
    connection as ios_connection,
    device as ios_device,
    input as ios_input,
    screenshot as ios_screenshot,
)


@dataclass
class PlatformConfig:
    """Configuration for platform controllers."""

    platform: str  # "android" or "ios"

    # Android-specific
    device_id: str | None = None

    # iOS-specific
    wda_url: str = "http://localhost:8100"
    ios_device_id: str | None = None
    wda_session_id: str | None = None


class PlatformController(Protocol):
    """Protocol defining the interface for platform-specific device controllers.

    All platform controllers (Android, iOS) must implement these methods
    to provide a consistent interface for device automation.
    """

    def take_screenshot(self) -> Screenshot:
        """Capture a screenshot from the device.

        Returns:
            Screenshot object containing base64_data, width, height, and is_sensitive flag.
        """
        ...

    def tap(self, x: int, y: int) -> None:
        """Tap at the specified coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        ...

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float | None = None,
    ) -> None:
        """Swipe from start to end coordinates.

        Args:
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            end_x: Ending X coordinate.
            end_y: Ending Y coordinate.
            duration: Duration of swipe in seconds (optional).
        """
        ...

    def type_text(self, text: str) -> None:
        """Type text at the currently focused input field.

        Args:
            text: The text to type.
        """
        ...

    def launch_app(self, app_name: str) -> bool:
        """Launch an app by name.

        Args:
            app_name: The app name.

        Returns:
            True if app was launched successfully, False otherwise.
        """
        ...

    def press_home(self) -> None:
        """Press the home button."""
        ...

    def press_back(self) -> None:
        """Press the back button."""
        ...

    def get_current_app(self) -> str:
        """Get the currently active app name.

        Returns:
            The app name, or "System Home" if on home screen.
        """
        ...


class AndroidController:
    """Platform controller for Android devices using ADB."""

    def __init__(self, config: PlatformConfig):
        """Initialize Android controller.

        Args:
            config: Platform configuration.
        """
        self.config = config
        self.device_id = config.device_id

    def take_screenshot(self) -> Screenshot:
        """Capture a screenshot from the Android device."""
        return adb_controller.take_screenshot(device_id=self.device_id)

    def tap(self, x: int, y: int) -> None:
        """Tap at the specified coordinates on Android device."""
        adb_controller.tap(x, y, device_id=self.device_id)

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float | None = None,
    ) -> None:
        """Swipe on Android device."""
        # Convert duration from seconds to milliseconds for ADB
        duration_ms = int(duration * 1000) if duration is not None else None
        adb_controller.swipe(
            start_x,
            start_y,
            end_x,
            end_y,
            duration_ms=duration_ms,
            device_id=self.device_id,
        )

    def type_text(self, text: str) -> None:
        """Type text on Android device using ADB Keyboard."""
        adb_controller.type_text(text, device_id=self.device_id)

    def launch_app(self, app_name: str) -> bool:
        """Launch an app on Android device."""
        return adb_controller.launch_app(app_name, device_id=self.device_id)

    def press_home(self) -> None:
        """Press home button on Android device."""
        adb_controller.press_home(device_id=self.device_id)

    def press_back(self) -> None:
        """Press back button on Android device."""
        adb_controller.press_back(device_id=self.device_id)

    def get_current_app(self) -> str:
        """Get currently active app on Android device."""
        return adb_controller.get_current_app(device_id=self.device_id)


class IOSController:
    """Platform controller for iOS devices using WebDriverAgent."""

    def __init__(
        self, config: PlatformConfig, app_packages: dict[str, str] | None = None
    ):
        """Initialize iOS controller.

        Args:
            config: Platform configuration.
            app_packages: Dictionary mapping app names to bundle IDs.
        """
        self.config = config
        self.wda_url = config.wda_url
        self.device_id = config.ios_device_id
        self.session_id = config.wda_session_id
        self.app_packages = app_packages or {}

    def take_screenshot(self) -> Screenshot:
        """Capture a screenshot from the iOS device."""
        return ios_screenshot.get_screenshot(
            wda_url=self.wda_url,
            session_id=self.session_id,
            device_id=self.device_id,
        )

    def tap(self, x: int, y: int) -> None:
        """Tap at the specified coordinates on iOS device."""
        ios_device.tap(x, y, wda_url=self.wda_url, session_id=self.session_id)

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float | None = None,
    ) -> None:
        """Swipe on iOS device."""
        ios_device.swipe(
            start_x,
            start_y,
            end_x,
            end_y,
            duration=duration,
            wda_url=self.wda_url,
            session_id=self.session_id,
        )

    def type_text(self, text: str) -> None:
        """Type text on iOS device using WebDriverAgent."""
        ios_input.type_text(text, wda_url=self.wda_url, session_id=self.session_id)

    def launch_app(self, app_name: str) -> bool:
        """Launch an app on iOS device."""
        return ios_device.launch_app(
            app_name,
            wda_url=self.wda_url,
            session_id=self.session_id,
            app_packages=self.app_packages,
        )

    def press_home(self) -> None:
        """Press home button on iOS device."""
        ios_device.home(wda_url=self.wda_url, session_id=self.session_id)

    def press_back(self) -> None:
        """Navigate back on iOS device (swipe from left edge)."""
        ios_device.back(wda_url=self.wda_url, session_id=self.session_id)

    def get_current_app(self) -> str:
        """Get currently active app on iOS device."""
        return ios_device.get_current_app(
            wda_url=self.wda_url,
            session_id=self.session_id,
            app_packages=self.app_packages,
        )


def create_controller(
    config: PlatformConfig, app_packages: dict[str, str] | None = None
) -> PlatformController:
    """Factory function to create the appropriate platform controller.

    Args:
        config: Platform configuration.
        app_packages: Dictionary mapping app names to package/bundle IDs.

    Returns:
        Platform controller instance (AndroidController or IOSController).

    Raises:
        ValueError: If platform is unknown.
        RuntimeError: If platform-specific requirements are not met.
    """
    platform = config.platform.lower()

    if platform == "android":
        # Verify Android requirements
        if not adb_controller.check_adb_available():
            raise RuntimeError(
                "ADB is not available. Please install Android SDK Platform Tools."
            )

        devices = adb_controller.list_devices()
        if not devices:
            raise RuntimeError(
                "No Android devices connected. Please connect a device via USB or WiFi."
            )

        return AndroidController(config)

    if platform == "ios":
        # Verify iOS requirements
        if not ios_connection.check_libimobiledevice():
            raise RuntimeError(
                "libimobiledevice is not available. Install it with: brew install libimobiledevice"
            )

        devices = ios_connection.list_devices()
        if not devices:
            raise RuntimeError(
                "No iOS devices connected. Please connect a device via USB or ensure WiFi connection is configured."
            )

        # Verify WebDriverAgent is running
        if not ios_connection.is_wda_ready(config.wda_url):
            raise RuntimeError(
                f"WebDriverAgent is not running at {config.wda_url}. "
                "Please start WebDriverAgent on the iOS device."
            )

        # Auto-create WDA session if not provided
        if config.wda_session_id is None:
            wda_connection = ios_connection.XCTestConnection(wda_url=config.wda_url)
            success, session_id = wda_connection.start_wda_session()
            if success and session_id != "session_started":
                config.wda_session_id = session_id
                print(f"✅ Created WDA session: {session_id}")
            else:
                print("⚠️  Using default WDA session (no explicit session ID)")

        return IOSController(config, app_packages)

    raise ValueError(f"Unknown platform: {platform}. Must be 'android' or 'ios'.")
