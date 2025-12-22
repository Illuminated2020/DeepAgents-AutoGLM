# AutoGLM Middleware for deepagents-cli

Android GUI automation middleware for deepagents-cli using vision-language models and ADB.

## Overview

AutoGLM middleware integrates [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM)'s phone agent capabilities into deepagents-cli, enabling autonomous Android device control through vision-guided automation.

### Features

- **Autonomous Task Execution**: High-level `phone_task` tool for natural language commands
- **Vision-Guided Control**: Uses vision-language models to understand and interact with GUI
- **Multi-Device Support**: Control multiple Android devices via ADB
- **18 Action Types**: Comprehensive action set (Tap, Swipe, Type, Launch, Back, Home, Wait, etc.)
- **Optional Low-Level Tools**: Direct ADB control when needed
- **Human-in-the-Loop**: Built-in support for sensitive operation confirmation
- **Bilingual Support**: Chinese (full feature set) and English prompts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    deepagents-cli Agent                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              AutoGLMMiddleware                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  phone_task Tool                                │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │  Vision Model Loop                      │    │  │  │
│  │  │  │  1. Take Screenshot (ADB)               │    │  │  │
│  │  │  │  2. Analyze Screen (Vision LLM)         │    │  │  │
│  │  │  │  3. Parse Action (action_parser)        │    │  │  │
│  │  │  │  4. Execute Action (adb_controller)     │    │  │  │
│  │  │  │  5. Repeat until task complete          │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  │                                                  │  │  │
│  │  │  Optional: Low-Level Tools (if enabled)         │  │  │
│  │  │  - phone_tap, phone_swipe, phone_type           │  │  │
│  │  │  - phone_screenshot, phone_back, phone_home     │  │  │
│  │  │  - phone_launch                                 │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
  ┌──────────────┐                   ┌──────────────┐
  │ Vision Model │                   │ Android      │
  │ (AutoGLM-    │                   │ Device       │
  │  Phone-9B)   │                   │ (via ADB)    │
  └──────────────┘                   └──────────────┘
```

## Installation

### 1. Install Dependencies

```bash
# Install deepagents-cli with AutoGLM support
cd DeepAgents/libs/deepagents-cli
uv pip install -e ".[autoglm]"

# Or with pip
pip install -e ".[autoglm]"
```

### 2. Setup ADB

**macOS:**
```bash
brew install android-platform-tools
```

**Ubuntu/Debian:**
```bash
sudo apt-get install android-tools-adb
```

**Windows:**
Download from: https://developer.android.com/studio/releases/platform-tools

**Verify:**
```bash
adb --version
```

### 3. Connect Android Device

**USB Connection:**
```bash
# 1. Enable USB debugging on Android device:
#    Settings → About Phone → Tap "Build Number" 7 times
#    Settings → Developer Options → Enable USB Debugging

# 2. Connect device via USB
adb devices  # Should show your device
```

**WiFi Connection (Optional):**
```bash
# 1. Connect via USB first, then:
adb tcpip 5555
adb connect <device-ip>:5555

# 2. Disconnect USB, verify WiFi connection:
adb devices
```

### 4. Install ADB Keyboard (Required for Text Input)

```bash
# Download ADB Keyboard APK
wget https://github.com/senzhk/ADBKeyBoard/raw/master/ADBKeyboard.apk

# Install on device
adb install -r ADBKeyboard.apk

# Enable in device settings:
# Settings → Language & Input → Current Keyboard → Select ADB Keyboard
```

### 5. Setup Vision Model

**Option A: Local vLLM Deployment (Recommended)**

```bash
# Install vLLM
pip install vllm

# Start vLLM server with AutoGLM-Phone-9B
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs '{"max_pixels":5000000}' \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt '{"image":10}' \
  --model zai-org/AutoGLM-Phone-9B \
  --port 8000

# Verify server is running
curl http://localhost:8000/health
```

**Option B: Remote API**

Use any OpenAI-compatible vision model API.

## Configuration

### 1. Create .env File

```bash
cp .env.autoglm.example .env
```

### 2. Configure Environment Variables

```bash
# Enable AutoGLM middleware
AUTOGLM_ENABLED=true

# Vision model settings (REQUIRED)
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY

# Device settings (optional, auto-detects first device if not set)
# AUTOGLM_DEVICE_ID=

# Language (zh=Chinese full features, en=English simplified)
AUTOGLM_LANG=zh

# Task execution settings
AUTOGLM_MAX_STEPS=100

# Tool exposure (false=high-level only, true=include low-level tools)
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# Debugging
AUTOGLM_VERBOSE=false
```

### Configuration Options Explained

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOGLM_ENABLED` | `false` | Enable/disable AutoGLM middleware |
| `AUTOGLM_VISION_MODEL_URL` | - | **Required**: Vision model API base URL |
| `AUTOGLM_VISION_MODEL_NAME` | `autoglm-phone-9b` | Model name |
| `AUTOGLM_VISION_API_KEY` | `EMPTY` | API key (use "EMPTY" for local vLLM) |
| `AUTOGLM_DEVICE_ID` | Auto-detect | ADB device ID (leave empty for auto-detection) |
| `AUTOGLM_LANG` | `zh` | Prompt language: `zh` (Chinese, 18 actions) or `en` (English, 7 actions) |
| `AUTOGLM_MAX_STEPS` | `100` | Maximum steps per task before timeout |
| `AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS` | `false` | Expose low-level ADB tools to main agent |
| `AUTOGLM_VERBOSE` | `false` | Enable detailed logging for debugging |

## Usage

### Basic Usage

```bash
# Start deepagents-cli
deepagents

# Use the phone_task tool
User: "Use phone_task to open WeChat"
Agent: *Autonomously controls phone to open WeChat*

User: "Use phone_task to search for 'coffee shops' on Maps"
Agent: *Opens Maps app, searches for coffee shops, shows results*
```

### Example Tasks

**Simple Tasks:**
```
- "Open Settings app"
- "Open Chrome and go to google.com"
- "Take a screenshot"
- "Press the back button"
- "Go to home screen"
```

**Complex Tasks:**
```
- "Open WeChat, find the chat with Alice, and send her 'Hello'"
- "Search for 'sushi restaurants' on Meituan and show me the top result"
- "Open Gmail, compose a new email to john@example.com with subject 'Meeting'"
- "On Taobao, search for 'wireless headphones' under 200 yuan"
```

**Multi-Step Tasks:**
```
- "Open Maps, search for 'gas stations near me', select the closest one, and show directions"
- "Open Settings, go to WiFi settings, and connect to 'Home-Network'"
- "Open Camera, switch to video mode, and start recording"
```

### Using Low-Level Tools

When `AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=true`, the agent has direct access to:

```python
# Direct ADB control tools
phone_tap(x=500, y=300)              # Tap at coordinates
phone_swipe(100, 500, 900, 500)      # Swipe gesture
phone_type("Hello World")             # Type text
phone_screenshot()                    # Capture screen
phone_back()                          # Press back
phone_home()                          # Press home
phone_launch("WeChat")                # Launch app
```

Example usage:
```
User: "Tap at coordinates (500, 300) on the phone"
Agent: *Uses phone_tap tool directly*

User: "Take a screenshot of the phone"
Agent: *Uses phone_screenshot tool*
```

## Supported Actions

### Chinese Prompt (AUTOGLM_LANG=zh) - 18 Actions

1. **Launch**: Launch app by name
2. **Tap**: Single tap at coordinates
3. **Tap** (with message): Sensitive operation tap with confirmation
4. **Type**: Input text
5. **Type_Name**: Input person name
6. **Interact**: User choice required
7. **Swipe**: Swipe gesture
8. **Note**: Record page content
9. **Call_API**: Summarize content
10. **Long Press**: Press and hold
11. **Double Tap**: Double tap
12. **Take_over**: Request human intervention
13. **Back**: Press back button
14. **Home**: Press home button
15. **Wait**: Wait for page load
16. **Check**: Verify element (placeholder)
17. **Select**: Select from options (placeholder)
18. **Open**: Open URL/deep link (placeholder)

### English Prompt (AUTOGLM_LANG=en) - 7 Basic Actions

1. **Launch**: Launch app
2. **Tap**: Tap at coordinates
3. **Type**: Input text
4. **Swipe**: Swipe gesture
5. **Long Press**: Press and hold
6. **Back**: Press back button
7. **Finish**: Complete task

## Supported Apps

The middleware includes mappings for 150+ popular apps:

**Chinese Apps:**
- WeChat (微信), QQ, Weibo (微博)
- Taobao (淘宝), JD (京东), Pinduoduo (拼多多)
- Meituan (美团), Ele.me (饿了么)
- Douyin (抖音), Bilibili, Kuaishou (快手)
- Amap (高德地图), Baidu Maps (百度地图)
- And 100+ more...

**International Apps:**
- Chrome, Gmail, Google Maps, Google Drive
- WhatsApp, Telegram, Twitter/X
- McDonald's, Booking.com, Expedia
- Duolingo, Quora, Reddit, TikTok
- And many more...

See `apps.py` for the complete list.

## Troubleshooting

### Device Not Found

```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices

# Check USB connection and debugging settings
# Verify USB debugging is enabled on device
```

### Text Input Not Working

```bash
# Verify ADB Keyboard is installed
adb shell pm list packages | grep adbkeyboard

# Check available input methods
adb shell ime list -s

# Should show: com.android.adbkeyboard/.AdbIME
```

### Vision Model Connection Failed

```bash
# Verify model server is running
curl http://localhost:8000/health

# Check environment variable
echo $AUTOGLM_VISION_MODEL_URL

# Test model API
curl http://localhost:8000/v1/models
```

### Task Times Out or Fails

1. **Increase max steps:**
   ```bash
   AUTOGLM_MAX_STEPS=200
   ```

2. **Enable verbose logging:**
   ```bash
   AUTOGLM_VERBOSE=true
   ```

3. **Check device screen:**
   - Ensure screen is on and unlocked
   - Disable auto-lock during automation
   - Check for dialogs or popups blocking the UI

### WiFi ADB Disconnects Frequently

```bash
# Use USB connection for stability
# Or reconnect WiFi:
adb connect <device-ip>:5555

# Keep-alive script (optional)
while true; do
  adb connect <device-ip>:5555
  sleep 60
done
```

### Debugging Tips

1. **Enable verbose mode:**
   ```bash
   AUTOGLM_VERBOSE=true deepagents
   ```

2. **Check saved screenshots:**
   Screenshots are saved to temporary directory (printed in verbose mode)

3. **Monitor ADB logcat:**
   ```bash
   adb logcat | grep -i error
   ```

4. **Test ADB commands manually:**
   ```bash
   adb shell screencap -p /sdcard/screenshot.png
   adb shell input tap 500 500
   ```

## Architecture Details

### Module Structure

```
deepagents_cli/middleware/
├── autoglm_middleware.py          # Main middleware class
└── autoglm/
    ├── __init__.py                # Module init
    ├── adb_controller.py          # ADB control layer (575 lines)
    ├── action_parser.py           # Action parsing (315 lines)
    ├── prompts.py                 # System prompts (232 lines)
    ├── apps.py                    # App mappings (280 lines)
    └── README.md                  # This file
```

### Core Components

**1. ADB Controller (`adb_controller.py`)**
- Device connection management
- Screenshot capture
- Touch interactions (tap, swipe, long press)
- Text input via ADB Keyboard
- App launching and management
- System key presses (back, home)

**2. Action Parser (`action_parser.py`)**
- Parses vision model output
- Handles 18 action types
- Validates action parameters
- Supports multiple response formats

**3. System Prompts (`prompts.py`)**
- Chinese prompt: Full feature set (18 actions + 18 execution rules)
- English prompt: Simplified version (7 basic actions)
- Dynamic date injection

**4. App Mappings (`apps.py`)**
- 150+ app name → package name mappings
- Fuzzy matching support
- Case-insensitive lookup

**5. Middleware (`autoglm_middleware.py`)**
- Middleware integration with deepagents-cli
- Vision model setup
- Tool definition (phone_task + optional low-level tools)
- Error handling and logging

### Coordinate System

- **Model Output**: Relative coordinates (0-999, 0-999)
- **Actual Execution**: Absolute pixel coordinates
- **Conversion**: `absolute_x = relative_x / 1000 * screen_width`

This normalization allows the model to work across different screen sizes.

## Performance Tips

1. **Reduce max_steps for simple tasks:**
   ```bash
   AUTOGLM_MAX_STEPS=50  # For "open app" type tasks
   ```

2. **Use low-level tools for direct control:**
   ```bash
   AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=true
   ```

3. **Optimize vision model:**
   - Use quantized model for faster inference
   - Adjust `max_pixels` parameter in vLLM
   - Consider GPU acceleration

4. **Screenshot optimization (future):**
   - Compress images before sending to model
   - Reduce image resolution for faster processing

## Security Considerations

1. **ADB Access**: Grants full control over Android device
2. **Sensitive Operations**: Use human-in-the-loop for payments, logins
3. **API Keys**: Store securely in .env (not committed to git)
4. **Network**: Vision model API traffic may contain screenshots

**Best Practices:**
- Only enable AutoGLM when needed
- Use device lock screen between sessions
- Review actions before execution in sensitive contexts
- Keep .env file secure and in .gitignore

## Source Attribution

This middleware is adapted from the [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) project by Tsinghua University.

**Original Project:**
- Repository: https://github.com/zai-org/Open-AutoGLM
- License: Apache 2.0
- Model: AutoGLM-Phone-9B (based on GLM-4.1V-9B-Thinking)

**Key Adaptations:**
- Integrated into deepagents-cli middleware architecture
- Used LangChain for vision model integration
- Simplified execution loop (direct model invocation vs. sub-agent)
- Added optional low-level tool exposure
- Bilingual support (Chinese full, English simplified)

## Contributing

To contribute to AutoGLM middleware:

1. Follow deepagents-cli coding standards
2. Add tests for new features
3. Update documentation
4. Run code quality checks:
   ```bash
   ruff check deepagents_cli/middleware/
   mypy deepagents_cli/middleware/
   ```

## Support

For issues and questions:
- deepagents-cli: https://github.com/anthropics/deepagents
- Open-AutoGLM: https://github.com/zai-org/Open-AutoGLM

## License

This middleware inherits the licenses from:
- deepagents-cli: MIT License
- Open-AutoGLM: Apache 2.0 License
