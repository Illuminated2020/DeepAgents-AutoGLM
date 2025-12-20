"""ADB device controller for Android automation.

Ported from: Open-AutoGLM/phone_agent/adb/
- connection.py (device connection management)
- device.py (device control operations)
- screenshot.py (screenshot capture)
- input.py (text input via ADB Keyboard)

This module provides comprehensive ADB control capabilities including:
- Device connection management (USB/WiFi/Remote)
- Screen capture and image processing
- Touch interactions (tap, swipe, long press)
- Text input via ADB Keyboard
- System key events (back, home)
- App launching and management
"""

import base64
import os
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from io import BytesIO

from PIL import Image


# Constants and defaults
DEFAULT_TAP_DELAY = 0.5
DEFAULT_SWIPE_DELAY = 0.5
DEFAULT_BACK_DELAY = 0.5
DEFAULT_HOME_DELAY = 0.5
DEFAULT_LAUNCH_DELAY = 2.0
DEFAULT_LONG_PRESS_DURATION = 3000
DEFAULT_DOUBLE_TAP_INTERVAL = 0.2


class ConnectionType(Enum):
    """Type of ADB connection."""

    USB = "usb"
    WIFI = "wifi"
    REMOTE = "remote"


@dataclass
class DeviceInfo:
    """Information about a connected device."""

    device_id: str
    status: str
    connection_type: ConnectionType
    model: str | None = None


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int
    is_sensitive: bool = False


# Device Connection Management


def check_adb_available() -> bool:
    """Check if ADB tool is available on the system.

    Returns:
        True if adb command is available, False otherwise.
    """
    try:
        result = subprocess.run(
            ["adb", "version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_devices() -> list[DeviceInfo]:
    """List all connected Android devices.

    Returns:
        List of DeviceInfo objects for each connected device.
    """
    try:
        result = subprocess.run(
            ["adb", "devices", "-l"], capture_output=True, text=True, timeout=5
        )

        devices = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 2:
                device_id = parts[0]
                status = parts[1]

                # Determine connection type
                if ":" in device_id:
                    conn_type = ConnectionType.REMOTE
                elif "emulator" in device_id:
                    conn_type = ConnectionType.USB
                else:
                    conn_type = ConnectionType.USB

                # Parse model if available
                model = None
                for part in parts[2:]:
                    if part.startswith("model:"):
                        model = part.split(":", 1)[1]
                        break

                devices.append(
                    DeviceInfo(
                        device_id=device_id,
                        status=status,
                        connection_type=conn_type,
                        model=model,
                    )
                )

        return devices

    except Exception as e:
        print(f"Error listing devices: {e}")
        return []


def connect_device(address: str, timeout: int = 10) -> tuple[bool, str]:
    """Connect to a remote device via TCP/IP.

    Args:
        address: Device address (e.g., "192.168.1.100:5555").
        timeout: Connection timeout in seconds.

    Returns:
        Tuple of (success, message).
    """
    if ":" not in address:
        address = f"{address}:5555"

    try:
        result = subprocess.run(
            ["adb", "connect", address],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout + result.stderr

        if "connected" in output.lower():
            return True, f"Connected to {address}"
        elif "already connected" in output.lower():
            return True, f"Already connected to {address}"
        else:
            return False, output.strip()

    except subprocess.TimeoutExpired:
        return False, f"Connection timeout after {timeout}s"
    except Exception as e:
        return False, f"Connection error: {e}"


def disconnect_device(address: str | None = None) -> tuple[bool, str]:
    """Disconnect from a remote device.

    Args:
        address: Device address. If None, disconnects all.

    Returns:
        Tuple of (success, message).
    """
    try:
        cmd = ["adb", "disconnect"]
        if address:
            cmd.append(address)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr
        return True, output.strip() or "Disconnected"

    except Exception as e:
        return False, f"Disconnect error: {e}"


def check_adb_keyboard(device_id: str | None = None) -> bool:
    """Check if ADB Keyboard is installed and enabled on the device.

    Args:
        device_id: Optional device ID.

    Returns:
        True if ADB Keyboard is available, False otherwise.
    """
    adb_prefix = _get_adb_prefix(device_id)

    try:
        # Check if ADB Keyboard package is installed
        result = subprocess.run(
            adb_prefix + ["shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if "com.android.adbkeyboard" not in result.stdout:
            return False

        # Check if ADB Keyboard is enabled
        result = subprocess.run(
            adb_prefix + ["shell", "ime", "list", "-s"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return "com.android.adbkeyboard/.AdbIME" in result.stdout

    except Exception:
        return False


# Screenshot Capture


def take_screenshot(device_id: str | None = None, timeout: int = 10) -> Screenshot:
    """Capture a screenshot from the Android device.

    Args:
        device_id: Optional device ID.
        timeout: Timeout in seconds.

    Returns:
        Screenshot object containing base64 data and dimensions.
        Returns black fallback image if capture fails.
    """
    temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4()}.png")
    adb_prefix = _get_adb_prefix(device_id)

    try:
        # Execute screenshot command
        result = subprocess.run(
            adb_prefix + ["shell", "screencap", "-p", "/sdcard/tmp.png"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Check for sensitive screen (screenshot blocked)
        output = result.stdout + result.stderr
        if "Status: -1" in output or "Failed" in output:
            return _create_fallback_screenshot(is_sensitive=True)

        # Pull screenshot to local temp path
        subprocess.run(
            adb_prefix + ["pull", "/sdcard/tmp.png", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if not os.path.exists(temp_path):
            return _create_fallback_screenshot(is_sensitive=False)

        # Read and encode image
        img = Image.open(temp_path)
        width, height = img.size

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Cleanup
        os.remove(temp_path)

        return Screenshot(
            base64_data=base64_data, width=width, height=height, is_sensitive=False
        )

    except Exception as e:
        print(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False)


def _create_fallback_screenshot(is_sensitive: bool) -> Screenshot:
    """Create a black fallback image when screenshot fails."""
    default_width, default_height = 1080, 2400

    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive,
    )


# Touch Interactions


def tap(x: int, y: int, device_id: str | None = None, delay: float | None = None) -> None:
    """Tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional device ID.
        delay: Delay in seconds after tap.
    """
    if delay is None:
        delay = DEFAULT_TAP_DELAY

    adb_prefix = _get_adb_prefix(device_id)
    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(delay)


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """Double tap at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        device_id: Optional device ID.
        delay: Delay in seconds after double tap.
    """
    if delay is None:
        delay = DEFAULT_TAP_DELAY

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(DEFAULT_DOUBLE_TAP_INTERVAL)
    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = DEFAULT_LONG_PRESS_DURATION,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Long press at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration of press in milliseconds.
        device_id: Optional device ID.
        delay: Delay in seconds after long press.
    """
    if delay is None:
        delay = DEFAULT_TAP_DELAY

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix
        + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True,
    )
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Swipe from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of swipe in milliseconds (auto-calculated if None).
        device_id: Optional device ID.
        delay: Delay in seconds after swipe.
    """
    if delay is None:
        delay = DEFAULT_SWIPE_DELAY

    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        # Calculate duration based on distance
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))  # Clamp between 1000-2000ms

    subprocess.run(
        adb_prefix
        + [
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration_ms),
        ],
        capture_output=True,
    )
    time.sleep(delay)


# System Keys


def press_back(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the back button.

    Args:
        device_id: Optional device ID.
        delay: Delay in seconds after pressing back.
    """
    if delay is None:
        delay = DEFAULT_BACK_DELAY

    adb_prefix = _get_adb_prefix(device_id)
    subprocess.run(adb_prefix + ["shell", "input", "keyevent", "4"], capture_output=True)
    time.sleep(delay)


def press_home(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the home button.

    Args:
        device_id: Optional device ID.
        delay: Delay in seconds after pressing home.
    """
    if delay is None:
        delay = DEFAULT_HOME_DELAY

    adb_prefix = _get_adb_prefix(device_id)
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True
    )
    time.sleep(delay)


# Text Input


def type_text(text: str, device_id: str | None = None, verbose: bool = False) -> None:
    """Type text using ADB Keyboard.

    Args:
        text: The text to type.
        device_id: Optional device ID.
        verbose: Enable detailed logging for debugging (default: False).

    Note:
        Requires ADB Keyboard to be installed and enabled.

        For long text (>500 chars), automatically splits into chunks to avoid
        Android Binder transaction size limits (1MB shared buffer).

        Safe chunk size: ~500 chars (after base64 encoding ~667 bytes + overhead).

    References:
        - Android Binder buffer: 1MB shared across all process transactions
        - Recommended Intent data size: a few KB to avoid TransactionTooLargeException
        - Base64 encoding overhead: ~33% size increase

    Raises:
        RuntimeError: If text input fails after retries.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Maximum safe characters per chunk to avoid Binder transaction limits
    # Conservative value to ensure reliability across different devices
    MAX_CHUNK_SIZE = 500

    # Increased delay for better reliability with long text
    CHUNK_DELAY = 0.3  # 300ms between chunks (doubled from 150ms)

    # Short text: use original single-broadcast approach
    if len(text) <= MAX_CHUNK_SIZE:
        if verbose:
            print(f"[type_text] Sending short text ({len(text)} chars)")
        encoded_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        result = subprocess.run(
            adb_prefix
            + [
                "shell",
                "am",
                "broadcast",
                "-a",
                "ADB_INPUT_B64",
                "--es",
                "msg",
                encoded_text,
            ],
            capture_output=True,
            text=True,
        )
        if verbose and result.returncode != 0:
            print(f"[type_text] Warning: broadcast failed with return code {result.returncode}")
            print(f"[type_text] stderr: {result.stderr}")
    else:
        # Long text: split into chunks and send sequentially
        total_chunks = (len(text) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE
        if verbose:
            print(f"[type_text] Sending long text ({len(text)} chars) in {total_chunks} chunks")

        failed_chunks = []
        for i in range(0, len(text), MAX_CHUNK_SIZE):
            chunk_num = i // MAX_CHUNK_SIZE + 1
            chunk = text[i : i + MAX_CHUNK_SIZE]
            encoded_chunk = base64.b64encode(chunk.encode("utf-8")).decode("utf-8")

            if verbose:
                chunk_preview = chunk[:50] + "..." if len(chunk) > 50 else chunk
                print(f"[type_text] Sending chunk {chunk_num}/{total_chunks} ({len(chunk)} chars): {chunk_preview}")

            result = subprocess.run(
                adb_prefix
                + [
                    "shell",
                    "am",
                    "broadcast",
                    "-a",
                    "ADB_INPUT_B64",
                    "--es",
                    "msg",
                    encoded_chunk,
                ],
                capture_output=True,
                text=True,
                timeout=5,  # Add timeout to avoid hanging
            )

            # Check if broadcast succeeded
            if result.returncode != 0:
                error_msg = f"Chunk {chunk_num}/{total_chunks} failed"
                failed_chunks.append(chunk_num)
                if verbose:
                    print(f"[type_text] ERROR: {error_msg}")
                    print(f"[type_text] Return code: {result.returncode}")
                    print(f"[type_text] stderr: {result.stderr}")

            # Delay between chunks to ensure proper delivery
            # Increased delay for better reliability
            if i + MAX_CHUNK_SIZE < len(text):  # Not the last chunk
                time.sleep(CHUNK_DELAY)

        if failed_chunks:
            error_msg = f"Failed to send chunks: {failed_chunks}. Text may be incomplete."
            if verbose:
                print(f"[type_text] CRITICAL ERROR: {error_msg}")
            # Don't raise exception, just warn (to match original behavior)
            print(f"Warning: {error_msg}")
        elif verbose:
            print(f"[type_text] Successfully sent all {total_chunks} chunks")


def clear_text(device_id: str | None = None) -> None:
    """Clear text in the currently focused input field.

    Args:
        device_id: Optional device ID.
    """
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "am", "broadcast", "-a", "ADB_CLEAR_TEXT"],
        capture_output=True,
        text=True,
    )


def set_adb_keyboard(device_id: str | None = None) -> str:
    """Switch to ADB Keyboard and return original IME.

    Args:
        device_id: Optional device ID.

    Returns:
        The original keyboard IME identifier for later restoration.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Get current IME
    result = subprocess.run(
        adb_prefix + ["shell", "settings", "get", "secure", "default_input_method"],
        capture_output=True,
        text=True,
    )
    current_ime = (result.stdout + result.stderr).strip()

    # Switch to ADB Keyboard if not already set
    if "com.android.adbkeyboard/.AdbIME" not in current_ime:
        subprocess.run(
            adb_prefix + ["shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"],
            capture_output=True,
            text=True,
        )

    # Warm up the keyboard
    type_text("", device_id)

    return current_ime


def restore_keyboard(ime: str, device_id: str | None = None) -> None:
    """Restore the original keyboard IME.

    Args:
        ime: The IME identifier to restore.
        device_id: Optional device ID.
    """
    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "ime", "set", ime], capture_output=True, text=True
    )


# App Management


def launch_app(
    app_name: str, device_id: str | None = None, delay: float | None = None
) -> bool:
    """Launch an app by name.

    Args:
        app_name: The app name (e.g., "微信", "Chrome", "Settings") or package name.
        device_id: Optional device ID.
        delay: Delay in seconds after launching.

    Returns:
        True if launch command succeeded, False otherwise.
    """
    if delay is None:
        delay = DEFAULT_LAUNCH_DELAY

    # Import apps module for name to package conversion
    from deepagents_cli.middleware.autoglm import apps

    # Try to find package name from app name
    package_name = apps.find_package_name(app_name)
    if not package_name:
        # Assume app_name is already a package name
        package_name = app_name

    adb_prefix = _get_adb_prefix(device_id)

    try:
        result = subprocess.run(
            adb_prefix
            + [
                "shell",
                "monkey",
                "-p",
                package_name,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ],
            capture_output=True,
            timeout=10,
        )

        time.sleep(delay)
        return result.returncode == 0

    except Exception:
        return False


def get_current_app(device_id: str | None = None) -> str:
    """Get the app name of the currently focused app.

    Args:
        device_id: Optional device ID.

    Returns:
        The app name (user-friendly) of the current app, or "System Home" if not found.
        Examples: "微信", "Chrome", "System Home"
    """
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"], capture_output=True, text=True
    )
    output = result.stdout

    # Import apps module for package name lookup
    from deepagents_cli.middleware.autoglm import apps

    # Parse window focus info
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            # Extract package name from line like "Window{...com.example.app/...}"
            parts = line.split()
            for part in parts:
                if "/" in part and "}" in part:
                    # Extract package from pattern like "com.example.app/.MainActivity}"
                    package = part.split("/")[0].split("{")[-1]

                    # Convert package name to user-friendly app name
                    app_name = apps.get_app_name(package)
                    if app_name:
                        return app_name  # Return "微信" instead of "com.tencent.mm"

                    # If package not found in mapping, return package name as fallback
                    return package

    return "System Home"


# Helper Functions


def _get_adb_prefix(device_id: str | None) -> list[str]:
    """Get ADB command prefix with optional device specifier.

    Args:
        device_id: Optional device ID.

    Returns:
        List of command components.
    """
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


# Compatibility alias for original function name
detect_and_set_adb_keyboard = set_adb_keyboard
