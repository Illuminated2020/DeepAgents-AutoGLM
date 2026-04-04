"""Unit tests for AutoGLM middleware integration."""

from __future__ import annotations

import asyncio
import base64
import importlib
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest

deepagents_sandbox = importlib.import_module("deepagents.backends.sandbox")
if not hasattr(deepagents_sandbox, "SandboxProvider"):
    deepagents_sandbox.SandboxProvider = object

package = types.ModuleType("deepagents_cli")
package.__path__ = [str(Path(__file__).resolve().parents[2] / "deepagents_cli")]
sys.modules.setdefault("deepagents_cli", package)

from deepagents_cli.middleware.autoglm import adb_controller
from deepagents_cli.middleware.autoglm.ios import connection as ios_connection
from deepagents_cli.middleware import autoglm_middleware
from deepagents_cli.middleware.autoglm_middleware import (
    AutoGLMConfig,
    AutoGLMMiddleware,
)


class _FakeAndroidController:
    def __init__(self) -> None:
        self.device_id: str | None = None


class _FakeIOSController:
    def __init__(self) -> None:
        self.device_id: str | None = None


def test_before_agent_syncs_auto_selected_android_device_to_controller(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-selected Android device ID should also update the controller."""
    controller = _FakeAndroidController()
    middleware = AutoGLMMiddleware(AutoGLMConfig(vision_model=object(), platform="android"))

    monkeypatch.setattr(autoglm_middleware.signal, "signal", lambda *_args, **_kwargs: Mock())
    monkeypatch.setattr(
        autoglm_middleware,
        "create_controller",
        lambda *_args, **_kwargs: controller,
    )
    monkeypatch.setattr(
        autoglm_middleware.adb_controller,
        "list_devices",
        lambda: [
            adb_controller.DeviceInfo(
                device_id="android-serial-1",
                status="device",
                connection_type=adb_controller.ConnectionType.USB,
                model="Pixel",
            )
        ],
    )
    monkeypatch.setattr(autoglm_middleware.adb_controller, "check_adb_keyboard", lambda _device_id: True)

    request = Mock()
    result = middleware.before_agent(request)

    assert result is request
    assert middleware.config.device_id == "android-serial-1"
    assert controller.device_id == "android-serial-1"


def test_before_agent_syncs_auto_selected_ios_device_to_controller(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-selected iOS device ID should also update the controller."""
    controller = _FakeIOSController()
    middleware = AutoGLMMiddleware(AutoGLMConfig(vision_model=object(), platform="ios"))

    monkeypatch.setattr(autoglm_middleware.signal, "signal", lambda *_args, **_kwargs: Mock())
    monkeypatch.setattr(
        autoglm_middleware,
        "create_controller",
        lambda *_args, **_kwargs: controller,
    )
    monkeypatch.setattr(
        ios_connection,
        "list_devices",
        lambda: [
            ios_connection.DeviceInfo(
                device_id="00008030-TESTUDID",
                status="connected",
                connection_type=ios_connection.ConnectionType.USB,
                device_name="iPhone",
            )
        ],
    )

    request = Mock()
    result = middleware.before_agent(request)

    assert result is request
    assert middleware.config.ios_device_id == "00008030-TESTUDID"
    assert controller.device_id == "00008030-TESTUDID"


def test_phone_screenshot_tool_handles_screenshot_object(tmp_path: Path) -> None:
    """The screenshot tool should read fields from the Screenshot object."""
    middleware = AutoGLMMiddleware(
        AutoGLMConfig(
            vision_model=object(),
            expose_low_level_tools=True,
            screenshot_dir=str(tmp_path),
        )
    )
    middleware.controller = Mock()
    middleware.controller.take_screenshot.return_value = adb_controller.Screenshot(
        base64_data=base64.b64encode(b"fake-image").decode("ascii"),
        width=1080,
        height=1920,
    )
    runtime = Mock(tool_call_id="call-1")
    tool = next(tool for tool in middleware.tools if tool.name == "phone_screenshot")

    result = tool.func(runtime=runtime)

    assert result.status == "success"
    assert "Size: 1080x1920" in result.content
    assert len(list(tmp_path.glob("manual_*.png"))) == 1


def test_phone_task_waits_for_lock_without_blocking_event_loop() -> None:
    """Waiting for an existing phone task should not freeze the event loop."""

    async def runner() -> None:
        middleware = AutoGLMMiddleware(AutoGLMConfig(vision_model=object(), max_steps=0))
        middleware._task_lock = asyncio.Lock()
        await middleware._task_lock.acquire()
        tick_count = 0

        async def ticker() -> None:
            nonlocal tick_count
            for _ in range(10):
                await asyncio.sleep(0.01)
                tick_count += 1

        task = asyncio.create_task(
            middleware._execute_phone_task_async("noop", "call-2")
        )
        ticker_task = asyncio.create_task(ticker())
        await asyncio.sleep(0.05)

        assert not task.done()
        assert tick_count > 0

        middleware._task_lock.release()
        await task
        await ticker_task

    asyncio.run(runner())


def test_phone_task_cancellation_does_not_release_foreign_lock() -> None:
    """Cancelling a waiting task must not release a lock held by another task."""

    async def runner() -> None:
        middleware = AutoGLMMiddleware(AutoGLMConfig(vision_model=object(), max_steps=0))
        middleware._task_lock = asyncio.Lock()
        await middleware._task_lock.acquire()

        task = asyncio.create_task(
            middleware._execute_phone_task_async("noop", "call-3")
        )
        await asyncio.sleep(0.05)

        task.cancel()
        await asyncio.sleep(0.05)

        assert middleware._task_lock.locked()

        middleware._task_lock.release()

        with pytest.raises(asyncio.CancelledError):
            await task

        assert not middleware._task_lock.locked()

    asyncio.run(runner())
