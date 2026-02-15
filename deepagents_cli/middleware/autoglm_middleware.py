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
import signal
import tempfile
import threading
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.tools import ToolRuntime, tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from deepagents_cli.middleware.autoglm import (
    action_parser,
    adb_controller,
    apps,
    prompts,
)
from deepagents_cli.middleware.autoglm.platform import (
    PlatformConfig,
    PlatformController,
    create_controller,
)

# AutoGLM Phone Task Usage Guide
AUTOGLM_SYSTEM_PROMPT = """

## Phone Control Tool Usage (phone_task)

**Important - Tool Responsibility Division:**

YOU (Main Agent):
- Task planning & decomposition
- Web search & information gathering
- Complex analysis & decision making
- Orchestrating multiple phone_task calls

phone_task (Phone Operator):
- Execute phone operations (tap, swipe, type, open apps)
- Multi-step UI navigation on the phone
- Read & return screen content
- Cannot do web searches or complex reasoning

**Usage Patterns:**

1. **Information Retrieval:** phone_task reads → you analyze → phone_task acts
   ```
   phone_task("Check WeChat messages from Alice") → "Alice asks: weather tomorrow?"
   web_search("weather tomorrow") → "Sunny, 20-25°C"
   phone_task("Reply to Alice: 'Sunny, 20-25°C'") → Done
   ```

2. **Operation with Data:** You provide complete data
   ```
   phone_task("Send WeChat message to Bob: 'Meeting at 3pm'")
   ```

3. **Task Decomposition:** Break complex tasks into simple phone operations
   ```
   ✗ Don't: phone_task("Answer Alice's question")
   ✓ Do: Get question → You find answer → Send answer
   ```

**Key Principle:** If it requires external knowledge or complex reasoning, YOU do it first, then give phone_task specific instructions.
"""


# ForceExitException removed - no longer needed with improved interrupt handling
# We now use only KeyboardInterrupt which is caught and converted to ToolMessage


@dataclass
class AutoGLMConfig:
    """Configuration for AutoGLM middleware."""

    # Vision model settings
    vision_model: BaseChatModel | None = None
    """Vision-language model for GUI understanding. Must support multimodal input."""

    # Platform settings
    platform: str = "android"
    """Platform to control: 'android' or 'ios'. Default is 'android'."""

    # Android device settings
    device_id: str | None = None
    """ADB device ID. If None, will use the first available device."""

    # iOS device settings
    wda_url: str = "http://localhost:8100"
    """WebDriverAgent URL for iOS devices. Default: http://localhost:8100"""

    ios_device_id: str | None = None
    """iOS device UDID. If None, will use the first available device."""

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

    ## Interrupt Handling

    This middleware implements a **hybrid interrupt mechanism**:

    1. **Execution-time interruption (Ctrl+C)**:
       - User can press Ctrl+C during phone_task execution to cancel
       - First Ctrl+C: Graceful cancellation (waits for current operation)
       - Second Ctrl+C: Immediate cancellation (cancels ongoing model call)
       - Returns ToolMessage with status="error" (agent can handle gracefully)

    2. **Pre-execution approval (HumanInTheLoopMiddleware)**:
       - Optional: Require approval before executing phone_task
       - Integrates with deepagents' standard interrupt mechanism
       - User can approve, reject, or edit task parameters

    ## Basic Usage Example

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
        expose_low_level_tools=False,  # Only expose high-level phone_task
    )
    middleware = AutoGLMMiddleware(config)

    # Use in agent
    agent = create_deep_agent(
        model=main_model,
        middleware=[middleware],
    )
    ```

    ## Advanced: Integration with HumanInTheLoopMiddleware

    For sensitive operations, you can require approval before executing phone tasks:

    ```python
    from deepagents.graph import create_deep_agent
    from deepagents_cli.middleware.autoglm_middleware import AutoGLMMiddleware, AutoGLMConfig

    # Create AutoGLM middleware (same as above)
    autoglm_middleware = AutoGLMMiddleware(config)

    # Create agent with pre-execution approval for phone_task
    agent = create_deep_agent(
        model=main_model,
        middleware=[autoglm_middleware],
        interrupt_on={
            # Require approval before executing phone tasks
            "phone_task": {
                "allowed_decisions": ["approve", "reject", "edit"],
                "description": lambda tc, state, rt: (
                    f"📱 Phone Task Approval Required\\n\\n"
                    f"Task: {tc['args']['task']}\\n\\n"
                    f"This will control the connected Android device.\\n"
                    f"Approve to proceed, reject to cancel, or edit to modify the task."
                ),
            },
            # Optional: Also require approval for low-level tools
            "phone_tap": True,  # All decisions allowed
            "phone_swipe": True,
            "phone_type": {
                "allowed_decisions": ["approve", "reject"],  # No editing
                "description": "Text input requires approval",
            },
        },
    )
    ```

    ## Interrupt Mechanism Comparison

    | Feature | Ctrl+C (Built-in) | HumanInTheLoopMiddleware |
    |---------|-------------------|--------------------------|
    | When | During execution | Before execution |
    | Use case | Cancel running task | Approve before starting |
    | Resumable | No (task cancelled) | Yes (with Command) |
    | Framework integration | Custom implementation | Standard deepagents |
    | Concurrency safe | Yes (with lock) | Yes (framework managed) |

    ## Best Practices

    1. **Use Ctrl+C for emergency stops**: Cancel tasks that are taking too long
    2. **Use HITL for sensitive operations**: Require approval for irreversible actions
    3. **Combine both**: HITL for approval + Ctrl+C for cancellation during execution
    4. **Avoid concurrent tasks**: Only one phone_task should run at a time (enforced by lock)
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

        # Platform controller will be initialized in before_agent after system checks
        self.controller: PlatformController | None = None

        # Interrupt handling
        # Note: These are instance-level variables, so concurrent phone_task calls
        # will share the same interrupt state. Since phone_task controls a physical
        # device, concurrent execution is not recommended. We use a lock to prevent it.
        self._task_lock = threading.Lock()
        self._interrupt_flag = threading.Event()
        self._interrupt_count = 0  # Track number of Ctrl+C presses
        self._last_interrupt_time = 0.0  # Track timestamp of last Ctrl+C
        self._interrupt_reset_timeout = 2.0  # Reset count after 2 seconds
        self._phone_task_active = False  # Flag to track if phone_task is running
        self._original_sigint_handler = None  # Store original signal handler
        self._original_ime = None  # Track original keyboard for cleanup
        self._active_task_count = 0  # Track number of active tasks

        # Rich console for beautiful output
        self._console = Console()

        # Build tool list
        self.tools = []
        self._define_tools()

    def before_agent(self, request: ModelRequest) -> ModelRequest | Command:
        """Perform system checks before agent starts.

        Checks platform-specific requirements:
        - Android: ADB availability, device connection, ADB Keyboard
        - iOS: libimobiledevice, device connection, WebDriverAgent

        Args:
            request: The initial model request.

        Returns:
            The original request if all checks pass, or Command to fail gracefully.

        Raises:
            RuntimeError: If platform requirements are not met.
        """
        # Setup signal handler in main thread (before any tasks start)
        # Save original handler and install custom one
        # The custom handler will only display panels when _phone_task_active is True
        if self._original_sigint_handler is None:
            self._original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
            self._setup_signal_handler()

        # Create platform configuration
        platform_config = PlatformConfig(
            platform=self.config.platform,
            device_id=self.config.device_id,
            wda_url=self.config.wda_url,
            ios_device_id=self.config.ios_device_id,
        )

        # Get app packages for platform controller
        app_packages = (
            apps.APP_PACKAGES
            if self.config.platform == "android"
            else apps.APP_PACKAGES_IOS
        )

        # Create platform controller (performs all platform-specific checks)
        try:
            self.controller = create_controller(platform_config, app_packages)
        except (ValueError, RuntimeError) as e:
            raise RuntimeError(str(e)) from e

        # Platform-specific additional checks
        if self.config.platform == "android":
            # Update device_id if it was auto-selected
            if self.config.device_id is None:
                devices = adb_controller.list_devices()
                self.config.device_id = devices[0].device_id
                if self.config.verbose:
                    print(
                        f"Using Android device: {self.config.device_id} ({devices[0].model})"
                    )

            # Check ADB Keyboard (warn only, don't fail)
            if not adb_controller.check_adb_keyboard(self.config.device_id):
                print(
                    "Warning: ADB Keyboard not found. Text input (Type action) will not work. "
                    "Install from: https://github.com/senzhk/ADBKeyBoard"
                )

        elif self.config.platform == "ios":
            # Update device_id if it was auto-selected
            if self.config.ios_device_id is None:
                from deepagents_cli.middleware.autoglm.ios import (
                    connection as ios_connection,
                )

                devices = ios_connection.list_devices()
                self.config.ios_device_id = devices[0].device_id
                if self.config.verbose:
                    device_name = devices[0].device_name or "Unknown"
                    print(
                        f"Using iOS device: {device_name} ({devices[0].device_id[:8]}...)"
                    )

        return request

    def _setup_signal_handler(self) -> None:
        """Setup signal handler for graceful interruption.

        This allows the phone_task to be interrupted with Ctrl+C and clean up properly.
        Supports two-level interruption:
        - First Ctrl+C: Graceful cancellation (waits for current operation)
        - Second Ctrl+C: Immediate cancellation (cancels model call in progress)

        IMPORTANT: Signal handlers should NEVER raise exceptions directly.
        Instead, we set flags that are checked in the main async loop.
        """

        def signal_handler(signum: int, frame: Any) -> None:
            """Handle interrupt signal with two-level graceful interruption.

            First Ctrl+C: Set interrupt flag for graceful cleanup at next checkpoint.
            Second Ctrl+C (within 2 seconds): Set flag for immediate cancellation.

            Note: We do NOT raise exceptions here as that's unsafe in signal handlers.
            The main loop checks _interrupt_flag and raises KeyboardInterrupt at safe points.

            IMPORTANT: Only responds when phone_task is active to avoid interfering
            with the main agent's Ctrl+C handling.
            """
            # signum and frame are required by signal.signal but not used
            _ = (signum, frame)

            # Only handle interrupt if phone_task is currently running
            if not self._phone_task_active:
                # Not in phone_task - call original handler (usually from main.py or execution.py)
                # This allows the main agent to handle Ctrl+C gracefully
                if self._original_sigint_handler and callable(
                    self._original_sigint_handler
                ):
                    self._original_sigint_handler(signum, frame)
                else:
                    # Fallback to default handler
                    signal.default_int_handler(signum, frame)
                return

            # Time-based interrupt detection: reset count if too much time has passed
            current_time = time.time()
            if current_time - self._last_interrupt_time > self._interrupt_reset_timeout:
                # More than 2 seconds since last interrupt - reset counter
                self._interrupt_count = 0

            self._interrupt_count += 1
            self._last_interrupt_time = current_time

            if self._interrupt_count == 1:
                # First Ctrl+C: Graceful cancellation
                message = Text()
                message.append("Cancelling task gracefully...\n\n", style="bold yellow")
                message.append("• ", style="dim")
                message.append(
                    "Waiting for current operation to complete\n", style="white"
                )
                message.append("• ", style="dim")
                message.append("Press ", style="white")
                message.append("Ctrl+C", style="bold cyan")
                message.append(" again to cancel immediately", style="white")

                self._console.print()
                self._console.print(
                    Panel(
                        message,
                        title="[bold yellow]⚠️  Task Interrupted[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 2),
                        width=70,  # Limit width for better appearance
                    )
                )

                # Set the interrupt flag for phone_task internal checking
                # phone_task will detect this and raise KeyboardInterrupt at a safe point
                self._interrupt_flag.set()

            else:
                # Second Ctrl+C: Immediate cancellation
                message = Text()
                message.append("Force cancelling...\n\n", style="bold red")
                message.append("• ", style="dim")
                message.append("Cancelling ongoing operations\n", style="white")
                message.append("• ", style="dim")
                message.append("Cleaning up resources", style="white")

                self._console.print()
                self._console.print(
                    Panel(
                        message,
                        title="[bold red]🛑 Immediate Cancellation[/bold red]",
                        border_style="red",
                        padding=(1, 2),
                        width=70,  # Limit width for better appearance
                    )
                )

                # Set interrupt flag (already set, but ensure it's set)
                self._interrupt_flag.set()

                # The main loop will detect the increased interrupt count
                # and cancel the model call immediately

        # Register signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)

    def _define_tools(self) -> None:
        """Define tools that will be added to the agent."""
        # Always add the high-level phone_task tool
        self.tools.append(self._create_phone_task_tool())

        # Optionally add low-level tools
        if self.config.expose_low_level_tools:
            self.tools.extend(self._create_low_level_tools())

    def _check_interrupt(self, step: int = 0) -> None:
        """Check if interrupt flag is set and raise KeyboardInterrupt.

        This is called at safe checkpoints in the task execution loop.

        Args:
            step: Current step number (for error messages)

        Raises:
            KeyboardInterrupt: If Ctrl+C was pressed (will be caught and converted to ToolMessage)
        """
        if self._interrupt_flag.is_set():
            # Clean up resources before interrupting
            self._cleanup_resources()

            # Raise KeyboardInterrupt to exit the task loop
            # This will be caught in _execute_phone_task_async and converted to a ToolMessage
            raise KeyboardInterrupt(f"Task interrupted at step {step}")

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
            """Execute phone operation tasks on the connected Android device.

            This tool is a phone operation specialist that handles all phone-related operations
            using a vision-language model to understand the screen and perform actions.

            IMPORTANT - Tool Responsibility:
            ✓ DOES: All phone operations (open apps, tap, swipe, type, view content, multi-step workflows)
            ✗ DOES NOT: Web searches, complex analysis, external knowledge queries

            Best Practices:
            1. For information retrieval: Ask the tool to get specific information and return it
               Example: "Open WeChat, find the chat with Alice, and tell me her latest message"

            2. For operations with data: Provide the data/content directly in the task
               Example: "Open WeChat and send Alice this message: 'The weather is sunny, 20-25°C'"

            3. Break down complex tasks: If a task requires web search or analysis, do that yourself
               first, then use phone_task with the results

            Anti-patterns (DON'T DO):
            ✗ "Read Alice's message and answer her question" (tool can't search for answers)
            ✓ INSTEAD: Use phone_task to read → you search/analyze → use phone_task to reply

            ✗ "Find a good restaurant and book it" (tool can't evaluate "good")
            ✓ INSTEAD: You find/evaluate restaurants → use phone_task to open app and book

            Args:
                task: Description of the phone operation task to perform.

            Examples:
                      - "Open WeChat and check if there are any unread messages from Alice"
                      - "Open WeChat and send Alice this message: 'Hello, how are you?'"
                      - "Open Maps and search for 'coffee shops near me', tell me the top 3 results"
                      - "Open Twitter and post this tweet: 'Having a great day!'"

            Returns:
                A message describing the operation result or retrieved information.

            Examples:
                >>> phone_task("Open Settings and turn on WiFi")
                "✅ Task completed. WiFi has been turned on in Settings."

                >>> phone_task("Open WeChat and check Alice's latest message")
                "✅ Task completed. Alice's latest message: 'What's the weather like tomorrow?'"

                >>> phone_task("Reply to Alice on WeChat: 'It will be sunny, 20-25°C'")
                "✅ Task completed. Message sent to Alice successfully."
            """
            return self._execute_phone_task(task, runtime.tool_call_id)

        return phone_task_tool

    def _execute_phone_task(
        self, task: str, tool_call_id: str | None
    ) -> ToolMessage | str:
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

    async def _execute_phone_task_async(
        self, task: str, tool_call_id: str | None
    ) -> ToolMessage | str:
        """Execute a phone automation task asynchronously.

        This implements the autonomous agent loop with interruptible model calls:
        1. Take screenshot
        2. Send to vision model with task description (interruptible)
        3. Parse model response to get action
        4. Execute action via ADB
        5. Repeat until task complete or max_steps reached

        IMPORTANT: Only one phone_task can run at a time since it controls a physical device.
        Concurrent calls will be queued.

        Args:
            task: Task description from user.
            tool_call_id: Tool call ID for creating ToolMessage.

        Returns:
            ToolMessage with task result.
        """
        # Acquire lock to prevent concurrent phone_task execution
        # Since we're controlling a physical device, only one task should run at a time
        if not self._task_lock.acquire(blocking=False):
            # Another task is already running
            if self.config.verbose:
                print("\n⚠️  Another phone_task is already running. Waiting...")

            # Wait for the lock (this makes the call blocking)
            self._task_lock.acquire()

        # Mark phone_task as active so signal handler will respond
        self._phone_task_active = True

        try:
            if self.config.verbose:
                print(f"\n{'=' * 60}")
                print(f"Starting phone task: {task}")
                print(f"{'=' * 60}\n")

            # Reset interrupt state at start of new task
            self._interrupt_flag.clear()
            # Note: _interrupt_count is now managed by time-based auto-reset in signal handler
            self._original_ime = None
            self._active_task_count += 1

            # Initialize conversation history
            messages = [
                {"role": "system", "content": self.system_prompt},
            ]

            step = 0
            last_thinking = ""
            is_first_step = True
            while step < self.config.max_steps:
                # Check for interrupt signal
                self._check_interrupt(step)

                step += 1

                if self.config.verbose:
                    print(f"\n--- Step {step}/{self.config.max_steps} ---")

                # Check interrupt before expensive operations
                self._check_interrupt(step)

                # Take screenshot using platform controller
                screenshot_result = self.controller.take_screenshot()

                # Check interrupt after screenshot
                self._check_interrupt(step)

                # 检测敏感页面 - 提示用户选择如何处理
                if screenshot_result.is_sensitive:
                    # 获取当前应用信息
                    current_app = self.controller.get_current_app()

                    if self.config.verbose:
                        print(f"\n⚠️  Step {step}: 检测到敏感页面 [{current_app}]")

                    # 提示用户选择如何处理
                    from rich.console import Console
                    from rich.panel import Panel

                    console = Console()

                    console.print()
                    console.print(
                        Panel(
                            f"[bold yellow]⚠️  检测到敏感页面[/bold yellow]\n\n"
                            f"平台: {self.config.platform.upper()}\n"
                            f"步骤: {step}\n"
                            f"应用: {current_app}\n\n"
                            f"检测到敏感页面（密码输入/支付确认等）。系统已阻止截图。\n\n"
                            f"[bold cyan]请在手机上手动完成此步骤（输入密码、确认支付等）[/bold cyan]",
                            border_style="yellow",
                            title="敏感页面",
                        )
                    )
                    console.print()
                    console.print("[cyan]选择操作：[/cyan]")
                    console.print("  [1] 手动完成后继续 (推荐)")
                    console.print("  [2] 终止任务")
                    console.print()

                    # 等待用户选择
                    while True:
                        try:
                            choice = input("请选择 [1/2] (默认=1): ").strip()
                            if not choice or choice == "1":
                                # 继续执行
                                console.print()
                                console.print("[green]✓ 继续执行任务...[/green]")
                                console.print()

                                if self.config.verbose:
                                    print("   用户已手动完成敏感操作，继续执行...")

                                # 构建屏幕信息（不发送黑屏图片）
                                import json

                                screen_info = json.dumps(
                                    {"current_app": current_app}, ensure_ascii=False
                                )
                                text_content = f"** Screen Info **\n\n{screen_info}\n\n[系统提示]: 上一步为敏感页面（无法截图）。用户已手动完成敏感操作。"

                                # 仅文本消息，不包含图片
                                user_message = {
                                    "role": "user",
                                    "content": [{"type": "text", "text": text_content}],
                                }
                                messages.append(user_message)
                                break
                            if choice == "2":
                                # 终止任务
                                console.print()
                                console.print("[yellow]任务已被用户终止[/yellow]")
                                console.print()
                                self._cleanup_resources()
                                return ToolMessage(
                                    content="⚠️ 任务已被用户终止（遇到敏感页面）",
                                    tool_call_id=tool_call_id,
                                    name="phone_task",
                                    status="error",
                                )
                            console.print("[red]无效选择，请输入 1 或 2[/red]")
                        except KeyboardInterrupt:
                            # Ctrl+C 视为终止任务
                            console.print()
                            console.print("[yellow]任务已被用户中断[/yellow]")
                            console.print()
                            self._cleanup_resources()
                            raise KeyboardInterrupt(
                                f"任务在敏感页面被用户中断（步骤 {step}）"
                            )

                    # 跳过本次截图的 AI 分析，直接进入下一步
                    continue

                # 正常截图流程（非敏感页面）
                screenshot_base64 = screenshot_result.base64_data
                screenshot_width = screenshot_result.width
                screenshot_height = screenshot_result.height

                # Get current app for context
                current_app = self.controller.get_current_app()

                # Save screenshot for debugging
                if self.config.screenshot_dir:
                    screenshot_path = self.screenshot_dir / f"step_{step:03d}.png"
                    with Path(screenshot_path).open("wb") as f:
                        # Decode base64 string to binary data for file writing
                        f.write(base64.b64decode(screenshot_base64))

                # Build screen info in JSON format (matching Open-AutoGLM)
                import json

                screen_info = json.dumps(
                    {"current_app": current_app}, ensure_ascii=False
                )

                # Build multimodal message (base64_data is already base64 encoded)
                image_base64 = screenshot_base64

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
                self._check_interrupt(step)

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
                                print(
                                    "\n[Interrupt detected during model call - cancelling]"
                                )
                            model_task.cancel()
                            # Wait for cancellation to complete
                            try:
                                await model_task
                            except asyncio.CancelledError:
                                pass
                            # Now raise appropriate interrupt exception
                            self._check_interrupt(step)
                        # Wait a short time before checking again
                        await asyncio.sleep(0.1)

                    # Get the result
                    response = await model_task
                    response_text = response.content

                except asyncio.CancelledError:
                    if self.config.verbose:
                        print("\n[Model call cancelled successfully]")
                    # Model was cancelled, check if it was due to interrupt
                    self._check_interrupt(step)

                # Check interrupt immediately after model returns
                self._check_interrupt(step)

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
                        print(f"\n{'=' * 60}")
                        print("✅ Task Completed Successfully!")
                        print(f"Message: {finish_message}")
                        print(f"Total steps: {step}/{self.config.max_steps}")
                        print(f"{'=' * 60}\n")
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
                        item
                        for item in messages[-1]["content"]
                        if item.get("type") == "text"
                    ]

                # Execute action
                action_result = self._execute_action(
                    action, screenshot_width, screenshot_height
                )

                # Check interrupt after action execution
                self._check_interrupt(step)

                if self.config.verbose:
                    print(f"Action result: {action_result}")

                # Add assistant response to history in Open-AutoGLM format
                assistant_message = (
                    f"<think>{thinking}</think><answer>{action_str}</answer>"
                )
                messages.append({"role": "assistant", "content": assistant_message})

                # If action failed, add error message
                if not action_result["success"]:
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Action failed: {action_result['message']}",
                        }
                    )

                # Small delay between actions (check interrupt during sleep)
                for _ in range(5):  # Split 0.5s into 5x 0.1s for responsive interrupt
                    if self._interrupt_flag.is_set():
                        break
                    await asyncio.sleep(0.1)

            # Max steps reached
            if self.config.verbose:
                print(f"\n{'=' * 60}")
                print("⚠️  Task Incomplete - Max Steps Reached")
                print(f"Reached maximum steps: {self.config.max_steps}")
                print(f"Last thinking: {last_thinking}")
                print(f"{'=' * 60}\n")
            self._cleanup_resources()
            return ToolMessage(
                content=f"Phone task incomplete. Reached maximum steps ({self.config.max_steps}). The task did not finish within the step limit. Last status: {last_thinking}",
                tool_call_id=tool_call_id,
                name="phone_task",
                status="error",
            )

        except KeyboardInterrupt:
            # Handle Ctrl+C - clean up resources and return error ToolMessage
            # Wait briefly to check if user presses Ctrl+C again (force cancel)
            # This gives time for the second Ctrl+C to increment _interrupt_count
            await asyncio.sleep(0.3)  # 300ms grace period for second Ctrl+C

            # Check if user pressed Ctrl+C multiple times (force cancel)
            was_force_cancelled = self._interrupt_count >= 2

            if self.config.verbose:
                cancel_type = (
                    "Force Cancelled" if was_force_cancelled else "Interrupted"
                )
                print(f"\n{'=' * 60}")
                print(f"⚠️  Task {cancel_type} by User (Ctrl+C)")
                print("Cleaning up phone resources...")
                print(f"Completed: {step} steps")
                print(f"{'=' * 60}\n")

            # Clean up phone resources
            self._cleanup_resources()

            # Return ToolMessage with appropriate message
            interrupt_type = "FORCE CANCELLED" if was_force_cancelled else "INTERRUPTED"
            return ToolMessage(
                content=(
                    f"⚠️ PHONE TASK {interrupt_type} BY USER ⚠️\n\n"
                    f"The task was {'force cancelled' if was_force_cancelled else 'cancelled'} by user request (Ctrl+C).\n"
                    f"Completed {step} of {self.config.max_steps} steps before interruption.\n\n"
                    f"Last status: {last_thinking or 'Task was interrupted early'}\n\n"
                    f"Resources have been cleaned up. You may retry the task if needed."
                ),
                tool_call_id=tool_call_id,
                name="phone_task",
                status="error",  # Mark as error so agent knows the task didn't complete
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
            # Mark phone_task as inactive so signal handler won't interfere with main agent
            self._phone_task_active = False

            # Ensure cleanup always runs
            self._cleanup_resources()
            # Note: _interrupt_count is managed by time-based auto-reset, no manual reset needed
            self._active_task_count = max(0, self._active_task_count - 1)
            # Release the lock to allow next task to run
            self._task_lock.release()

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
                adb_controller.restore_keyboard(
                    self._original_ime, self.config.device_id
                )
                self._original_ime = None
        except Exception as e:
            if self.config.verbose:
                print(f"Warning: Failed to restore keyboard: {e}")

    def _execute_action(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> dict[str, Any]:
        """Execute a parsed action via platform controller.

        Args:
            action: Parsed action dictionary.
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.

        Returns:
            Dictionary with 'success' (bool) and 'message' (str) keys.
        """
        action_name = action.get("action")

        try:
            if action_name == "Launch":
                app_name = action.get("app")
                if not app_name:
                    return {"success": False, "message": "No app name provided"}
                success = self.controller.launch_app(app_name)
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
                    self.controller.tap(x, y)
                elif action_name == "Double Tap":
                    # Double tap not in protocol - use tap twice
                    self.controller.tap(x, y)
                    time.sleep(0.2)
                    self.controller.tap(x, y)
                # Long press not in protocol - iOS uses long_press via device module
                elif self.config.platform == "android":
                    adb_controller.long_press(x, y, 3000, self.config.device_id)
                else:
                    from deepagents_cli.middleware.autoglm.ios import (
                        device as ios_device,
                    )

                    ios_device.long_press(
                        x, y, duration=3.0, wda_url=self.config.wda_url
                    )

                return {
                    "success": True,
                    "message": f"Executed {action_name} at ({x}, {y})",
                }

            if action_name in ["Type", "Type_Name"]:
                text = action.get("text", "")

                try:
                    # Platform-specific keyboard handling
                    if self.config.platform == "android":
                        # Switch to ADB keyboard and save original IME for cleanup
                        original_ime = adb_controller.set_adb_keyboard(
                            self.config.device_id
                        )
                        self._original_ime = (
                            original_ime  # Track for cleanup on interrupt
                        )
                        time.sleep(1.0)  # keyboard_switch_delay

                        # Clear existing text
                        adb_controller.clear_text(self.config.device_id)
                        time.sleep(0.5)  # text_clear_delay

                    # Log text length for debugging
                    if self.config.verbose:
                        print(f"[Type Action] Inputting text: {len(text)} characters")
                        print(
                            f"[Type Action] Text preview: {text[:100]}..."
                            if len(text) > 100
                            else f"[Type Action] Text: {text}"
                        )

                    # Type text via platform controller
                    self.controller.type_text(text)

                    # Delay for text to be processed
                    if len(text) > 500:
                        time.sleep(2.0)  # 2s for long text
                    else:
                        time.sleep(1.0)  # 1s for short text

                    return {
                        "success": True,
                        "message": f"Typed: {len(text)} characters",
                    }

                finally:
                    # Restore keyboard (Android only)
                    if self.config.platform == "android":
                        try:
                            if self._original_ime:
                                adb_controller.restore_keyboard(
                                    self._original_ime, self.config.device_id
                                )
                                time.sleep(0.5)  # keyboard_restore_delay
                                self._original_ime = None  # Clear after restoration
                        except Exception as e:
                            if self.config.verbose:
                                print(
                                    f"Warning: Failed to restore keyboard in Type action: {e}"
                                )

            if action_name == "Swipe":
                start = action.get("start")
                end = action.get("end")
                if not start or not end or len(start) != 2 or len(end) != 2:
                    return {"success": False, "message": "Invalid swipe coordinates"}
                coordinate_mode = action.get("coordinate_mode")
                if (
                    coordinate_mode == "pixel"
                    or max(start[0], start[1], end[0], end[1]) > 1000
                ):
                    start_x = int(start[0])
                    start_y = int(start[1])
                    end_x = int(end[0])
                    end_y = int(end[1])
                else:
                    start_x = int(start[0] / 1000 * screen_width)
                    start_y = int(start[1] / 1000 * screen_height)
                    end_x = int(end[0] / 1000 * screen_width)
                    end_y = int(end[1] / 1000 * screen_height)

                duration_ms = action.get("duration_ms")
                duration = None
                if isinstance(duration_ms, (int, float)):
                    duration = duration_ms / 1000.0
                self.controller.swipe(start_x, start_y, end_x, end_y, duration=duration)
                return {"success": True, "message": "Executed swipe"}

            if action_name == "Back":
                self.controller.press_back()
                return {"success": True, "message": "Pressed back"}

            if action_name == "Home":
                self.controller.press_home()
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
                self.controller.tap(x, y)
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
                # Convert duration from milliseconds to seconds for platform controller
                duration_sec = duration_ms / 1000.0 if duration_ms else None
                self.controller.swipe(
                    start_x, start_y, end_x, end_y, duration=duration_sec
                )
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
            """Type text on the phone.

            Args:
                text: Text to type.

            Returns:
                Confirmation message.
            """
            try:
                self.controller.type_text(text)
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
                screenshot_base64, width, height = self.controller.take_screenshot()
                screenshot_path = self.screenshot_dir / f"manual_{int(time.time())}.png"
                with Path(screenshot_path).open("wb") as f:
                    # Decode base64 string to binary data for file writing
                    f.write(base64.b64decode(screenshot_base64))
                return ToolMessage(
                    content=f"Screenshot saved to: {screenshot_path}\nSize: {width}x{height}",
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
                self.controller.press_back()
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
                self.controller.press_home()
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
                success = self.controller.launch_app(app_name)
                if success:
                    return ToolMessage(
                        content=f"Launched {app_name}",
                        tool_call_id=runtime.tool_call_id,
                        name="phone_launch",
                        status="success",
                    )
                return ToolMessage(
                    content=f"Failed to launch {app_name}. App may not be supported.",
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

        tools.extend(
            [
                phone_tap_tool,
                phone_swipe_tool,
                phone_type_tool,
                phone_screenshot_tool,
                phone_back_tool,
                phone_home_tool,
                phone_launch_tool,
            ]
        )

        return tools

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject AutoGLM usage documentation into the system prompt.

        This runs on every model call to ensure phone_task usage guidance is always available.

        Args:
            request: The model request being processed.
            handler: The handler function to call with the modified request.

        Returns:
            The model response from the handler.
        """
        # Inject AutoGLM usage documentation into system prompt
        if request.system_prompt:
            system_prompt = request.system_prompt + "\n\n" + AUTOGLM_SYSTEM_PROMPT
        else:
            system_prompt = AUTOGLM_SYSTEM_PROMPT

        return handler(request.override(system_prompt=system_prompt))

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """(async) Inject AutoGLM usage documentation into the system prompt.

        Args:
            request: The model request being processed.
            handler: The handler function to call with the modified request.

        Returns:
            The model response from the handler.
        """
        # Inject AutoGLM usage documentation into system prompt
        if request.system_prompt:
            system_prompt = request.system_prompt + "\n\n" + AUTOGLM_SYSTEM_PROMPT
        else:
            system_prompt = AUTOGLM_SYSTEM_PROMPT

        return await handler(request.override(system_prompt=system_prompt))


__all__ = ["AutoGLMConfig", "AutoGLMMiddleware"]
