"""AutoGLM Middleware for Android GUI automation.

This middleware integrates Open-AutoGLM's phone agent capabilities into deepagents-cli,
providing Android device control through vision-language models and ADB.

Source: Adapted from Open-AutoGLM project
Original: https://github.com/zai-org/Open-AutoGLM

Features:
- High-level phone_task tool for autonomous task execution
- Optional low-level tools for direct ADB control (tap, swipe, type, etc.)
- Vision-language model integration for GUI understanding
- Human-in-the-loop for sensitive operations
- Multi-device support
"""

from __future__ import annotations

import asyncio
import base64
import os
import signal
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain.agents.middleware.types import AgentMiddleware, AgentState, ModelRequest
from langchain.tools import ToolRuntime, tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

from deepagents_cli.middleware.autoglm import action_parser, adb_controller, apps, prompts


@dataclass
class AutoGLMConfig:
    """Configuration for AutoGLM middleware."""

    # Vision model settings
    vision_model: BaseChatModel | None = None
    """Vision-language model for GUI understanding. Must support multimodal input."""

    # Device settings
    device_id: str | None = None
    """ADB device ID. If None, will use the first available device."""

    # Language settings
    lang: str = "zh"
    """Language for system prompts: 'zh' for Chinese, 'en' for English."""

    # Task execution settings
    max_steps: int = 100
    """Maximum number of steps for phone tasks."""

    screenshot_dir: str | None = None
    """Directory for saving screenshots. If None, uses temporary directory."""

    # Tool exposure settings
    expose_low_level_tools: bool = False
    """Whether to expose low-level ADB tools (tap, swipe, etc.) to the main agent."""

    # Debug settings
    verbose: bool = False
    """Enable verbose logging for debugging."""


class AutoGLMMiddleware(AgentMiddleware[AgentState, Any]):
    """Middleware providing Android GUI automation capabilities.

    This middleware adds phone automation tools to the agent, enabling control of
    Android devices through ADB and vision-language models.

    The middleware provides:
    1. phone_task: High-level tool for autonomous task execution
    2. Optional low-level tools for direct control (if expose_low_level_tools=True)

    Example:
        ```python
        from langchain_openai import ChatOpenAI
        from deepagents_cli.middleware.autoglm_middleware import AutoGLMMiddleware, AutoGLMConfig

        # Create vision model
        vision_model = ChatOpenAI(
            base_url="http://localhost:8000/v1",
            model="autoglm-phone-9b",
            api_key="EMPTY",
        )

        # Create middleware
        config = AutoGLMConfig(
            vision_model=vision_model,
            device_id=None,  # Use first available device
            lang="zh",  # Chinese prompts
            max_steps=50,
            expose_low_level_tools=True,  # Expose direct ADB tools
        )
        middleware = AutoGLMMiddleware(config)

        # Use in agent
        agent = create_deep_agent(
            model=main_model,
            middleware=[middleware],
        )
        ```
    """

    def __init__(self, config: AutoGLMConfig) -> None:
        """Initialize AutoGLM middleware.

        Args:
            config: AutoGLM configuration.

        Raises:
            ValueError: If vision_model is not provided in config.
        """
        super().__init__()
        self.config = config

        if config.vision_model is None:
            msg = "vision_model must be provided in AutoGLMConfig"
            raise ValueError(msg)

        # Setup screenshot directory
        if config.screenshot_dir:
            self.screenshot_dir = Path(config.screenshot_dir)
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Use temporary directory
            self.screenshot_dir = Path(tempfile.mkdtemp(prefix="autoglm_screenshots_"))

        # Get system prompt based on language
        if config.lang == "en":
            self.system_prompt = prompts.get_phone_agent_prompt_en()
        else:
            self.system_prompt = prompts.get_phone_agent_prompt_zh()

        # Interrupt handling
        self._interrupt_flag = threading.Event()
        self._original_ime = None  # Track original keyboard for cleanup

        # Build tool list
        self.tools = []
        self._define_tools()

    def before_agent(self, request: ModelRequest) -> ModelRequest | Command:
        """Perform system checks before agent starts.

        Checks:
        1. ADB is available on the system
        2. At least one device is connected
        3. ADB Keyboard is installed (if using Type actions)

        Args:
            request: The initial model request.

        Returns:
            The original request if all checks pass, or Command to fail gracefully.

        Raises:
            RuntimeError: If ADB is not available or no devices are connected.
        """
        # Setup signal handler for Ctrl+C
        self._setup_signal_handler()

        # Check ADB availability
        if not adb_controller.check_adb_available():
            msg = (
                "ADB (Android Debug Bridge) is not available. "
                "Please install ADB and ensure it's in your system PATH."
            )
            raise RuntimeError(msg)

        # Check device connection
        devices = adb_controller.list_devices()
        if not devices:
            msg = (
                "No Android devices connected. "
                "Please connect a device via USB or WiFi and ensure USB debugging is enabled."
            )
            raise RuntimeError(msg)

        # Set device ID if not specified
        if self.config.device_id is None:
            self.config.device_id = devices[0].device_id
            if self.config.verbose:
                print(f"Using device: {self.config.device_id} ({devices[0].model})")

        # Check ADB Keyboard (warn only, don't fail)
        if not adb_controller.check_adb_keyboard(self.config.device_id):
            print(
                "Warning: ADB Keyboard not found. Text input (Type action) will not work. "
                "Install from: https://github.com/senzhk/ADBKeyBoard"
            )

        return request

    def _setup_signal_handler(self) -> None:
        """Setup signal handler for graceful interruption.

        This allows the phone_task to be interrupted with Ctrl+C and clean up properly.
        """

        def signal_handler(signum: int, frame: Any) -> None:
            """Handle interrupt signal by setting the interrupt flag and raising KeyboardInterrupt.

            IMPORTANT: We must raise KeyboardInterrupt to propagate the interrupt to the
            main agent loop. Otherwise, the interrupt is "swallowed" and the agent continues running.
            """
            # signum and frame are required by signal.signal but not used
            _ = (signum, frame)

            # Provide immediate feedback to user
            print("\n" + "="*60)
            print("⚠️  INTERRUPT SIGNAL RECEIVED (Ctrl+C)")
            print("="*60)
            print("Cancelling task... Please wait for current operation to complete.")
            print("(This may take a few seconds if waiting for model response)")
            print("="*60 + "\n")

            # Set the interrupt flag for phone_task internal checking
            self._interrupt_flag.set()

            # CRITICAL: Raise KeyboardInterrupt to propagate to main agent loop
            # Without this, the interrupt is caught but not propagated, and the agent continues
            raise KeyboardInterrupt()

        # Register signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)

    def _define_tools(self) -> None:
        """Define tools that will be added to the agent."""
        # Always add the high-level phone_task tool
        self.tools.append(self._create_phone_task_tool())

        # Optionally add low-level tools
        if self.config.expose_low_level_tools:
            self.tools.extend(self._create_low_level_tools())

    def _create_phone_task_tool(self) -> Any:
        """Create the phone_task tool for autonomous task execution.

        Returns:
            A tool that can execute phone automation tasks.
        """

        @tool("phone_task")
        def phone_task_tool(
            task: str,
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Execute a task on the connected Android phone using autonomous GUI automation.

            This tool uses a vision-language model to understand the phone screen and
            perform actions to complete the requested task. It autonomously navigates
            the UI, taps buttons, enters text, and performs other actions as needed.

            Args:
                task: Description of the task to perform on the phone.
                      Examples:
                      - "Open WeChat and send a message to Alice saying 'Hello'"
                      - "Search for coffee shops near me on the Maps app"
                      - "Add a reminder for tomorrow at 9 AM to call the dentist"

            Returns:
                A message describing the result of the task execution.

            Examples:
                >>> phone_task("Open Settings and turn on WiFi")
                "Task completed successfully. WiFi has been turned on in Settings."

                >>> phone_task("Search for 'sushi' on Meituan")
                "Task completed. Found 15 sushi restaurants. The top result is..."
            """
            return self._execute_phone_task(task, runtime.tool_call_id)

        return phone_task_tool

    def _execute_phone_task(self, task: str, tool_call_id: str | None) -> ToolMessage | str:
        """Execute a phone automation task (async wrapper).

        This wraps the async implementation to provide a synchronous interface
        for the tool system.

        Args:
            task: Task description from user.
            tool_call_id: Tool call ID for creating ToolMessage.

        Returns:
            ToolMessage with task result.
        """
        # Run the async implementation
        return asyncio.run(self._execute_phone_task_async(task, tool_call_id))

    async def _execute_phone_task_async(self, task: str, tool_call_id: str | None) -> ToolMessage | str:
        """Execute a phone automation task asynchronously.

        This implements the autonomous agent loop with interruptible model calls:
        1. Take screenshot
        2. Send to vision model with task description (interruptible)
        3. Parse model response to get action
        4. Execute action via ADB
        5. Repeat until task complete or max_steps reached

        Args:
            task: Task description from user.
            tool_call_id: Tool call ID for creating ToolMessage.

        Returns:
            ToolMessage with task result.
        """
        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"Starting phone task: {task}")
            print(f"{'='*60}\n")

        # Reset interrupt flag at start of new task
        self._interrupt_flag.clear()
        self._original_ime = None

        # Initialize conversation history
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        step = 0
        last_thinking = ""
        is_first_step = True

        try:
            while step < self.config.max_steps:
                # Check for interrupt signal
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print(f"\n{'='*60}")
                        print(f"⚠️  Task Interrupted by User")
                        print(f"Stopped at step: {step}/{self.config.max_steps}")
                        print(f"{'='*60}\n")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                step += 1

                if self.config.verbose:
                    print(f"\n--- Step {step}/{self.config.max_steps} ---")

                # Check interrupt before expensive operations
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print("\n[Interrupt detected before screenshot]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                # Take screenshot
                screenshot = adb_controller.take_screenshot(self.config.device_id)

                # Check interrupt after screenshot
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print("\n[Interrupt detected after screenshot]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                # Get current app for context
                current_app = adb_controller.get_current_app(self.config.device_id)

                # Save screenshot for debugging
                if self.config.screenshot_dir:
                    screenshot_path = self.screenshot_dir / f"step_{step:03d}.png"
                    with open(screenshot_path, "wb") as f:
                        # Decode base64 string to binary data for file writing
                        f.write(base64.b64decode(screenshot.base64_data))

                # Build screen info in JSON format (matching Open-AutoGLM)
                import json

                screen_info = json.dumps({"current_app": current_app}, ensure_ascii=False)

                # Build multimodal message (base64_data is already base64 encoded)
                image_base64 = screenshot.base64_data

                # Different format for first step vs subsequent steps
                if is_first_step:
                    text_content = f"{task}\n\n{screen_info}"
                    is_first_step = False
                else:
                    text_content = f"** Screen Info **\n\n{screen_info}"

                content = [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                    {
                        "type": "text",
                        "text": text_content,
                    },
                ]

                user_message = {"role": "user", "content": content}
                messages.append(user_message)

                # Check interrupt before expensive model call
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print("\n[Interrupt detected before model call]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                # Call vision model asynchronously with interrupt checking
                if self.config.verbose:
                    print("Calling vision model... (Press Ctrl+C to cancel)")

                # Create async task for model call
                model_task = asyncio.create_task(
                    self.config.vision_model.ainvoke(messages)
                )

                # Wait for model response while checking interrupt flag
                response = None
                try:
                    while not model_task.done():
                        # Check interrupt every 0.1 seconds
                        if self._interrupt_flag.is_set():
                            if self.config.verbose:
                                print("\n[Interrupt detected during model call - cancelling]")
                            model_task.cancel()
                            self._cleanup_resources()
                            return ToolMessage(
                                content=f"Phone task interrupted by user at step {step} during model call. Task was cancelled.",
                                tool_call_id=tool_call_id,
                                name="phone_task",
                                status="error",
                            )
                        # Wait a short time before checking again
                        await asyncio.sleep(0.1)

                    # Get the result
                    response = await model_task
                    response_text = response.content

                except asyncio.CancelledError:
                    if self.config.verbose:
                        print("\n[Model call cancelled successfully]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Model call was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                # Check interrupt immediately after model returns
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print("\n[Interrupt detected after model call]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                if self.config.verbose:
                    print(f"Model response: {response_text[:200]}...")

                # Parse response
                thinking, action_str = action_parser.parse_response(response_text)
                last_thinking = thinking

                if self.config.verbose and thinking:
                    print(f"Thinking: {thinking}")

                # Parse action
                try:
                    action = action_parser.parse_action(action_str)
                except ValueError as e:
                    if self.config.verbose:
                        print(f"Failed to parse action: {e}")
                    # Add error message and retry
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: Failed to parse action. Please provide a valid action. Error: {e}",
                        }
                    )
                    continue

                if self.config.verbose:
                    print(f"Action: {action}")

                # Check if task is complete
                if action_parser.is_finish_action(action):
                    finish_message = action.get("message", "Task completed")
                    if self.config.verbose:
                        print(f"\n{'='*60}")
                        print(f"✅ Task Completed Successfully!")
                        print(f"Message: {finish_message}")
                        print(f"Total steps: {step}/{self.config.max_steps}")
                        print(f"{'='*60}\n")
                    self._cleanup_resources()

                    # Return with clear completion message to prevent Agent from retrying
                    return ToolMessage(
                        content=(
                            f"✅ PHONE TASK COMPLETED SUCCESSFULLY ✅\n\n"
                            f"{finish_message}\n\n"
                            f"The task has been fully completed. No further action is needed."
                        ),
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="success",
                    )

                # Remove image from previous message to save context space (matching Open-AutoGLM)
                if isinstance(messages[-1].get("content"), list):
                    messages[-1]["content"] = [
                        item for item in messages[-1]["content"] if item.get("type") == "text"
                    ]

                # Execute action
                action_result = self._execute_action(action, screenshot.width, screenshot.height)

                # Check interrupt after action execution
                if self._interrupt_flag.is_set():
                    if self.config.verbose:
                        print("\n[Interrupt detected after action execution]")
                    self._cleanup_resources()
                    return ToolMessage(
                        content=f"Phone task interrupted by user at step {step}. Task was cancelled.",
                        tool_call_id=tool_call_id,
                        name="phone_task",
                        status="error",
                    )

                if self.config.verbose:
                    print(f"Action result: {action_result}")

                # Add assistant response to history in Open-AutoGLM format
                assistant_message = f"<think>{thinking}</think><answer>{action_str}</answer>"
                messages.append({"role": "assistant", "content": assistant_message})

                # If action failed, add error message
                if not action_result["success"]:
                    messages.append(
                        {"role": "user", "content": f"Action failed: {action_result['message']}"}
                    )

                # Small delay between actions (check interrupt during sleep)
                for _ in range(5):  # Split 0.5s into 5x 0.1s for responsive interrupt
                    if self._interrupt_flag.is_set():
                        break
                    await asyncio.sleep(0.1)

            # Max steps reached
            if self.config.verbose:
                print(f"\n{'='*60}")
                print(f"⚠️  Task Incomplete - Max Steps Reached")
                print(f"Reached maximum steps: {self.config.max_steps}")
                print(f"Last thinking: {last_thinking}")
                print(f"{'='*60}\n")
            self._cleanup_resources()
            return ToolMessage(
                content=f"Phone task incomplete. Reached maximum steps ({self.config.max_steps}). The task did not finish within the step limit. Last status: {last_thinking}",
                tool_call_id=tool_call_id,
                name="phone_task",
                status="error",
            )

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            if self.config.verbose:
                print(f"\n{'='*60}")
                print(f"⚠️  Task Interrupted by Ctrl+C")
                print(f"Cleaning up resources...")
                print(f"{'='*60}\n")
            self._cleanup_resources()
            return ToolMessage(
                content=f"Phone task interrupted by user (Ctrl+C) at step {step}. Resources cleaned up.",
                tool_call_id=tool_call_id,
                name="phone_task",
                status="error",
            )

        except Exception as e:
            error_msg = f"Phone task failed: {e}"
            if self.config.verbose:
                import traceback

                print(f"\n{error_msg}")
                traceback.print_exc()
            self._cleanup_resources()
            return ToolMessage(
                content=f"✗ {error_msg}",
                tool_call_id=tool_call_id,
                name="phone_task",
                status="error",
            )

        finally:
            # Ensure cleanup always runs
            self._cleanup_resources()

    def _cleanup_resources(self) -> None:
        """Clean up resources after task completion or interruption.

        This ensures:
        - Keyboard is restored to original IME if it was changed
        - Resources are properly released
        """
        try:
            # Restore keyboard if it was changed
            if self._original_ime and self.config.device_id:
                if self.config.verbose:
                    print("Restoring original keyboard...")
                adb_controller.restore_keyboard(self._original_ime, self.config.device_id)
                self._original_ime = None
        except Exception as e:
            if self.config.verbose:
                print(f"Warning: Failed to restore keyboard: {e}")

    def _execute_action(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> dict[str, Any]:
        """Execute a parsed action via ADB.

        Args:
            action: Parsed action dictionary.
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.

        Returns:
            Dictionary with 'success' (bool) and 'message' (str) keys.
        """
        action_name = action.get("action")
        device_id = self.config.device_id

        try:
            if action_name == "Launch":
                app_name = action.get("app")
                if not app_name:
                    return {"success": False, "message": "No app name provided"}
                # launch_app now accepts app_name directly and handles conversion internally
                success = adb_controller.launch_app(app_name, device_id)
                if success:
                    return {"success": True, "message": f"Launched {app_name}"}
                return {"success": False, "message": f"Failed to launch {app_name}"}

            if action_name in ["Tap", "Double Tap", "Long Press"]:
                element = action.get("element")
                if not element or len(element) != 2:
                    return {"success": False, "message": "Invalid element coordinates"}
                # Convert relative (0-999) to absolute coordinates
                x = int(element[0] / 1000 * screen_width)
                y = int(element[1] / 1000 * screen_height)

                if action_name == "Tap":
                    adb_controller.tap(x, y, device_id)
                elif action_name == "Double Tap":
                    adb_controller.double_tap(x, y, device_id)
                else:  # Long Press
                    adb_controller.long_press(x, y, 3000, device_id)  # 3 seconds (match original)

                return {"success": True, "message": f"Executed {action_name} at ({x}, {y})"}

            if action_name in ["Type", "Type_Name"]:
                text = action.get("text", "")

                try:
                    # Switch to ADB keyboard and save original IME for cleanup
                    original_ime = adb_controller.set_adb_keyboard(device_id)
                    self._original_ime = original_ime  # Track for cleanup on interrupt
                    time.sleep(1.0)  # keyboard_switch_delay - increased to ensure keyboard is fully activated

                    # Clear existing text and type new text
                    adb_controller.clear_text(device_id)
                    time.sleep(0.5)  # text_clear_delay - increased for stability

                    adb_controller.type_text(text, device_id)
                    time.sleep(1.0)  # text_input_delay - increased to ensure text is fully processed

                    return {"success": True, "message": f"Typed: {text}"}

                finally:
                    # Always restore keyboard, even if interrupted
                    try:
                        if self._original_ime:
                            adb_controller.restore_keyboard(self._original_ime, device_id)
                            time.sleep(0.5)  # keyboard_restore_delay
                            self._original_ime = None  # Clear after restoration
                    except Exception as e:
                        if self.config.verbose:
                            print(f"Warning: Failed to restore keyboard in Type action: {e}")

            if action_name == "Swipe":
                start = action.get("start")
                end = action.get("end")
                if not start or not end or len(start) != 2 or len(end) != 2:
                    return {"success": False, "message": "Invalid swipe coordinates"}
                # Convert to absolute coordinates
                start_x = int(start[0] / 1000 * screen_width)
                start_y = int(start[1] / 1000 * screen_height)
                end_x = int(end[0] / 1000 * screen_width)
                end_y = int(end[1] / 1000 * screen_height)

                # Use None for duration to auto-calculate based on distance (1000-2000ms range)
                adb_controller.swipe(start_x, start_y, end_x, end_y, None, device_id)
                return {"success": True, "message": "Executed swipe"}

            if action_name == "Back":
                adb_controller.press_back(device_id)
                return {"success": True, "message": "Pressed back"}

            if action_name == "Home":
                adb_controller.press_home(device_id)
                return {"success": True, "message": "Pressed home"}

            if action_name == "Wait":
                duration_str = action.get("duration", "1 seconds")
                try:
                    duration = float(duration_str.replace("seconds", "").strip())
                except ValueError:
                    duration = 1.0
                time.sleep(duration)
                return {"success": True, "message": f"Waited {duration} seconds"}

            if action_name in ["Take_over", "Interact"]:
                message = action.get("message", "User intervention required")
                # TODO: Implement proper HITL integration
                return {"success": True, "message": f"Requesting user help: {message}"}

            if action_name in ["Note", "Call_API"]:
                # Placeholder actions
                return {"success": True, "message": f"{action_name} acknowledged"}

            return {"success": False, "message": f"Unknown action: {action_name}"}

        except Exception as e:
            return {"success": False, "message": f"Action execution failed: {e}"}

    def _create_low_level_tools(self) -> list[Any]:
        """Create low-level ADB control tools.

        Returns:
            List of low-level tools for direct ADB control.
        """
        tools = []

        @tool("phone_tap")
        def phone_tap_tool(
            x: int,
            y: int,
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Tap a specific location on the phone screen.

            Args:
                x: X coordinate in pixels.
                y: Y coordinate in pixels.

            Returns:
                Confirmation message.
            """
            try:
                adb_controller.tap(x, y, self.config.device_id)
                return ToolMessage(
                    content=f"Tapped at ({x}, {y})",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_tap",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Tap failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_tap",
                    status="error",
                )

        @tool("phone_swipe")
        def phone_swipe_tool(
            start_x: int,
            start_y: int,
            end_x: int,
            end_y: int,
            duration_ms: int = 300,
            runtime: ToolRuntime[None, AgentState] = None,
        ) -> ToolMessage | str:
            """Swipe on the phone screen.

            Args:
                start_x: Starting X coordinate.
                start_y: Starting Y coordinate.
                end_x: Ending X coordinate.
                end_y: Ending Y coordinate.
                duration_ms: Swipe duration in milliseconds.

            Returns:
                Confirmation message.
            """
            try:
                adb_controller.swipe(start_x, start_y, end_x, end_y, duration_ms, self.config.device_id)
                return ToolMessage(
                    content=f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})",
                    tool_call_id=runtime.tool_call_id if runtime else None,
                    name="phone_swipe",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Swipe failed: {e}",
                    tool_call_id=runtime.tool_call_id if runtime else None,
                    name="phone_swipe",
                    status="error",
                )

        @tool("phone_type")
        def phone_type_tool(
            text: str,
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Type text on the phone using ADB Keyboard.

            Args:
                text: Text to type.

            Returns:
                Confirmation message.
            """
            try:
                adb_controller.type_text(text, self.config.device_id)
                return ToolMessage(
                    content=f"Typed: {text}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_type",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Type failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_type",
                    status="error",
                )

        @tool("phone_screenshot")
        def phone_screenshot_tool(
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Take a screenshot of the phone screen.

            Returns:
                Path to the saved screenshot.
            """
            try:
                screenshot = adb_controller.take_screenshot(self.config.device_id)
                screenshot_path = self.screenshot_dir / f"manual_{int(time.time())}.png"
                with open(screenshot_path, "wb") as f:
                    # Decode base64 string to binary data for file writing
                    f.write(base64.b64decode(screenshot.base64_data))
                return ToolMessage(
                    content=f"Screenshot saved to: {screenshot_path}\nSize: {screenshot.width}x{screenshot.height}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_screenshot",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Screenshot failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_screenshot",
                    status="error",
                )

        @tool("phone_back")
        def phone_back_tool(
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Press the back button on the phone.

            Returns:
                Confirmation message.
            """
            try:
                adb_controller.press_back(self.config.device_id)
                return ToolMessage(
                    content="Pressed back button",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_back",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Back failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_back",
                    status="error",
                )

        @tool("phone_home")
        def phone_home_tool(
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Press the home button on the phone.

            Returns:
                Confirmation message.
            """
            try:
                adb_controller.press_home(self.config.device_id)
                return ToolMessage(
                    content="Pressed home button",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_home",
                    status="success",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Home failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_home",
                    status="error",
                )

        @tool("phone_launch")
        def phone_launch_tool(
            app_name: str,
            runtime: ToolRuntime[None, AgentState],
        ) -> ToolMessage | str:
            """Launch an app on the phone by name.

            Args:
                app_name: Name of the app to launch (e.g., "WeChat", "Chrome", "Settings").

            Returns:
                Confirmation message.
            """
            try:
                package_name = apps.find_package_name(app_name)
                if not package_name:
                    return ToolMessage(
                        content=f"Unknown app: {app_name}. Use phone_list_apps to see supported apps.",
                        tool_call_id=runtime.tool_call_id,
                        name="phone_launch",
                        status="error",
                    )
                success = adb_controller.launch_app(package_name, self.config.device_id)
                if success:
                    return ToolMessage(
                        content=f"Launched {app_name} ({package_name})",
                        tool_call_id=runtime.tool_call_id,
                        name="phone_launch",
                        status="success",
                    )
                return ToolMessage(
                    content=f"Failed to launch {app_name}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_launch",
                    status="error",
                )
            except Exception as e:
                return ToolMessage(
                    content=f"Launch failed: {e}",
                    tool_call_id=runtime.tool_call_id,
                    name="phone_launch",
                    status="error",
                )

        tools.extend([
            phone_tap_tool,
            phone_swipe_tool,
            phone_type_tool,
            phone_screenshot_tool,
            phone_back_tool,
            phone_home_tool,
            phone_launch_tool,
        ])

        return tools


__all__ = ["AutoGLMMiddleware", "AutoGLMConfig"]
