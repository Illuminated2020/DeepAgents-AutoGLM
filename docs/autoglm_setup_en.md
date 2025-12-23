# AutoGLM Setup Guide

AutoGLM supports both Android and iOS device types. The configuration varies depending on your device type.

## Table of Contents

- [AutoGLM Setup Guide](#autoglm-setup-guide)
  - [Table of Contents](#table-of-contents)
  - [Android Device Setup](#android-device-setup)
    - [1. Install AutoGLM Dependencies](#1-install-autoglm-dependencies)
    - [2. Install ADB Tools](#2-install-adb-tools)
    - [3. Environment Variables Configuration](#3-environment-variables-configuration)
    - [4. Quick Device Setup](#4-quick-device-setup)
    - [5. Connect Android Device](#5-connect-android-device)
      - [Method 1: USB Connection (Recommended)](#method-1-usb-connection-recommended)
      - [Method 2: WiFi Connection (Android 11+)](#method-2-wifi-connection-android-11)
      - [Method 3: Enable TCP/IP Mode via USB (Android 7+)](#method-3-enable-tcpip-mode-via-usb-android-7)
    - [6. Install ADB Keyboard](#6-install-adb-keyboard)
    - [7. Vision Model Configuration](#7-vision-model-configuration)
      - [Option 1: Local Deployment (GPU Required)](#option-1-local-deployment-gpu-required)
      - [Option 2: Use Cloud Services (Recommended - No GPU Required)](#option-2-use-cloud-services-recommended---no-gpu-required)
    - [8. Usage Examples](#8-usage-examples)
  - [iOS Device Setup](#ios-device-setup)
    - [1. Environment Requirements](#1-environment-requirements)
    - [2. WebDriverAgent Configuration](#2-webdriveragent-configuration)
      - [1. Clone WebDriverAgent](#1-clone-webdriveragent)
      - [2. Set Up Signing \& Capabilities](#2-set-up-signing--capabilities)
      - [3. Test Xcode GUI Mode and UI Automation Settings](#3-test-xcode-gui-mode-and-ui-automation-settings)
      - [4. Device Trust Configuration](#4-device-trust-configuration)
      - [5. Xcode Command Line Deployment (Optional)](#5-xcode-command-line-deployment-optional)
    - [3. Configure DeepAgents-AutoGLM](#3-configure-deepagents-autoglm)
      - [1. Install iOS Dependencies](#1-install-ios-dependencies)
      - [2. Configure Environment Variables](#2-configure-environment-variables)
      - [3. Start WebDriverAgent](#3-start-webdriveragent)
      - [4. Use DeepAgents-AutoGLM](#4-use-deepagents-autoglm)
    - [4. Verify Installation](#4-verify-installation)
    - [5. iOS-Specific Notes](#5-ios-specific-notes)
  - [Common Issues](#common-issues)
    - [Android-Related](#android-related)
    - [iOS-Related](#ios-related)
  - [References](#references)

---

## Android Device Setup

> **Note**: AutoGLM is an optional feature. The CLI works fine without it if you set `AUTOGLM_ENABLED=false`.

### 1. Install AutoGLM Dependencies

Make sure you have installed AutoGLM support:

```bash
# In the project root directory
# Using pip
pip install -e ".[autoglm]"

# Or using uv
uv pip install -e ".[autoglm]"
```

### 2. Install ADB Tools

Android device automation requires ADB (Android Debug Bridge) tools.

**macOS:**

```bash
brew install android-platform-tools
```

**Ubuntu/Debian:**

```bash
sudo apt-get install android-tools-adb
```

**Windows:**

1. Download platform-tools from the [official website](https://developer.android.com/tools/releases/platform-tools)
2. Extract to a custom path (e.g., `C:\platform-tools`)
3. Configure environment variables:
   - Right-click `This PC` → `Properties` → `Advanced system settings` → `Environment Variables`
   - Find `Path` under `System variables`, click `Edit`
   - Click `New`, add the full path to platform-tools (e.g., `C:\platform-tools`)
   - Click `OK` to save

**Verify installation:**

```bash
adb version  # Should output version information
```

### 3. Environment Variables Configuration

**Create configuration file:**

```bash
# Copy the example configuration file
cp .env.example .env
```

**Edit the `.env` file:**

```bash
# ============ Basic LLM Configuration ============
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# ============ AutoGLM Android Configuration ============
# Enable AutoGLM
AUTOGLM_ENABLED=true

# Device type (android or ios)
AUTOGLM_PLATFORM=android

# Vision model configuration
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1  # Local deployment
# Or use cloud service:
# AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4  # Zhipu AI
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY  # Use EMPTY for local deployment, actual API Key for cloud

# Android device configuration (optional, leave empty to auto-detect first device)
# AUTOGLM_DEVICE_ID=

# Language configuration (zh=Chinese, en=English)
AUTOGLM_LANG=en

# Maximum steps
AUTOGLM_MAX_STEPS=100

# Expose low-level tools (false=only high-level phone_task)
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# Verbose logging (for debugging)
AUTOGLM_VERBOSE=false
```

For detailed configuration instructions, refer to the [.env.example](../.env.example) file.

### 4. Quick Device Setup

Before connecting your device, enable developer mode and USB debugging on your Android device:

```bash
# 1. Enable developer mode on your phone
#    Settings → About phone → Tap "Build number" 7-10 times

# 2. Enable USB debugging
#    Settings → Developer options → USB debugging → Enable
#    (Some models also require enabling "USB debugging (Security settings)")

# 3. Connect device and verify
adb devices
# Should show: XXXXXXXX    device
# If showing unauthorized, tap "Allow USB debugging" on your phone
```

### 5. Connect Android Device

#### Method 1: USB Connection (Recommended)

```bash
# 1. Enable developer mode on device
#    Settings → About phone → Find "Build number"
#    Tap "Build number" rapidly 7-10 times
#    You should see a "You are now a developer" message

# 2. Enable USB debugging
#    Settings → Developer options → USB debugging → Enable
#    (Some models also require enabling "USB debugging (Security settings)")

# 3. Connect device using USB cable
#    Note: Must use a data-transfer cable (not charge-only cable)

# 4. Verify connection
adb devices
# Should show: List of devices attached
#              XXXXXXXX    device

# Common issues:
# - Showing unauthorized: Tap "Allow USB debugging" on the authorization popup on your phone
# - Device not showing: Check if USB debugging is enabled, try a different cable or USB port
# - Some models may require device restart to take effect
```

#### Method 2: WiFi Connection (Android 11+)

```bash
# 1. Enable wireless debugging on your phone
#    Make sure phone and computer are on the same WiFi network
#    Go to: Settings → Developer options → Wireless debugging → Enable
#    Tap "Pair device with pairing code"

# 2. Pair device (execute on computer, enter the pairing code shown on phone)
adb pair <device-IP>:<pairing-port>
# Example: adb pair 192.168.1.100:46201
# Enter pairing code: 441750  (Enter the code shown on your phone)

# 3. Connect device (use the wireless debugging port, not the pairing port)
adb connect <device-IP>:<debugging-port>
# Example: adb connect 192.168.1.100:41589

# 4. Verify connection
adb devices
# Should show: 192.168.1.100:41589    device
```

#### Method 3: Enable TCP/IP Mode via USB (Android 7+)

```bash
# 1. Connect device via USB
adb devices

# 2. Enable TCP/IP mode (port 5555)
adb tcpip 5555

# 3. Get device IP address
adb shell ip addr show wlan0 | grep 'inet '
# Or check on phone: Settings → About phone → Status → IP address

# 4. Disconnect USB cable and connect via WiFi
adb connect <device-IP>:5555
# Example: adb connect 192.168.1.100:5555

# 5. Verify connection
adb devices
```

**Remote connection troubleshooting:**

- **Connection refused**: Ensure device and computer are on the same network, check if firewall is blocking port 5555
- **Connection dropped**: WiFi may have disconnected, use `adb connect <IP>:5555` to reconnect
- **Not working after device restart**: Some devices disable TCP/IP after restart, need to re-enable via USB

### 6. Install ADB Keyboard

Text input functionality requires ADB Keyboard:

Download the [APK](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk) and install it on your Android device.
Note: After installation, you need to enable `ADB Keyboard` in `Settings - Input method` or `Settings - Keyboard list` (or use the command `adb shell ime enable com.android.adbkeyboard/.AdbIME`). See [How-to-use](https://github.com/senzhk/ADBKeyBoard/blob/master/README.md#how-to-use) for details.

### 7. Vision Model Configuration

AutoGLM requires a vision model to understand phone screens. You can choose local deployment or cloud services.

#### Option 1: Local Deployment (GPU Required)

**Install vLLM:**

```bash
pip install vllm
```

**Start vision model service:**

```bash
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
```

**Configure environment variables:**

```bash
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY
```

#### Option 2: Use Cloud Services (Recommended - No GPU Required)

**2.1 Zhipu BigModel**

- **Documentation**: https://docs.bigmodel.cn/cn/api/introduction
- **Get API Key**: Register at Zhipu platform and apply

**Configure environment variables:**

```bash
AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4
AUTOGLM_VISION_MODEL_NAME=autoglm-phone
AUTOGLM_VISION_API_KEY=your-zhipu-api-key
```

**2.2 ModelScope**

- **Documentation**: https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B
- **Get API Key**: Register at ModelScope platform and apply

**Configure environment variables:**

```bash
AUTOGLM_VISION_MODEL_URL=https://api-inference.modelscope.cn/v1
AUTOGLM_VISION_MODEL_NAME=ZhipuAI/AutoGLM-Phone-9B
AUTOGLM_VISION_API_KEY=your-modelscope-api-key
```

**Available models:**

| Model                         | Download Links                                                                                                                                                       | Description                          |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| AutoGLM-Phone-9B              | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)`<br>`[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)                           | Optimized for Chinese phone apps     |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)`<br>`[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) | Supports English and other languages |

### 8. Usage Examples

After completing the above configuration, you can start using:

```bash
$ deepagents

User: Open WeChat
Agent: I will use the phone_task tool to open WeChat...

User: Search for nearby coffee shops
Agent: I will use the phone_task tool to open the maps app and search for coffee shops...

User: Send a WeChat message to John saying "see you tomorrow"
Agent: I will use the phone_task tool to open WeChat, find John's chat and send the message...
```

## iOS Device Setup

### 1. Environment Requirements

- macOS operating system
- Xcode (latest version, download from App Store)
- Apple Developer account (free account is sufficient, no paid account required)
- iOS device (iPhone/iPad)
- USB cable or same WiFi network

### 2. WebDriverAgent Configuration

WebDriverAgent is the core component for iOS automation and needs to run on your iOS device.

#### 1. Clone WebDriverAgent

```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

Simply click `WebDriverAgent.xcodeproj` to open it with Xcode.

#### 2. Set Up Signing & Capabilities

1. In Xcode, select `WebDriverAgent`, you'll see options like General, Signing&Capabilities
2. Go to the `Signing & Capabilities` tab
3. Check `Automatically manage signing`, select your developer account in Team
4. Change Bundle ID to a unique identifier, e.g., `com.yourname.WebDriverAgentRunner`

![Setup Signing 1](resources/ios0_WebDriverAgent0.png)

5. In TARGETS, it's recommended to set up `Signing & Capabilities` for WebDriverAgentLib, WebDriverAgentRunner, and IntegrationApp in the same way

![Setup Signing 2](resources/ios0_WebDriverAgent1.png)

#### 3. Test Xcode GUI Mode and UI Automation Settings

It's recommended to test if WebDriverAgent can be successfully installed via GUI mode before proceeding.
Mac and iPhone have two connection methods: USB and WiFi. USB method is recommended for higher success rate.

**Connect via WiFi (Optional):**

Requirements:

1. First connect via USB. In Finder, select the connected iPhone, check "Show this iPhone when on WiFi" in General
2. Mac and iPhone are on the same WiFi network

**Steps:**

1. Select `WebDriverAgentRunner` from the project Target
2. Select your device

![Select Device](resources/select-your-iphone-device.png)

3. Long-press the "▶️" run button, select "Test" to start compiling and deploying to your iPhone

![Start Testing](resources/start-wda-testing.png)

Signs of successful deployment:

1. Xcode shows no errors
2. You can find an app named WebDriverAgentRunner on your iPhone

#### 4. Device Trust Configuration

For first-time use, complete the following settings on your iPhone, then recompile and deploy:

1. **Enter unlock passcode**
2. **Trust developer application**

   - Go to: Settings → General → VPN & Device Management
   - Under "Developer App", select the corresponding developer
   - Tap Trust "XXX"

   ![Trust Device](resources/trust-dev-app.jpg)

3. **Enable UI Automation**

   - Go to: Settings → Developer
   - Turn on UI Automation

   ![Enable UI Automation](resources/enable-ui-automation.jpg)

#### 5. Xcode Command Line Deployment (Optional)

1. Install libimobiledevice for communication with iPhone/iPad:

```bash
brew install libimobiledevice

# Check devices
idevice_id -ln
```

2. Use xcodebuild to install WebDriverAgent (command line also requires "Device Trust Configuration", refer to GUI mode method):

```bash
cd WebDriverAgent

xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```

Here, `YOUR_PHONE_NAME` can be seen in Xcode GUI.

When WebDriverAgent runs successfully, it will output something like this in the Xcode console:

```
ServerURLHere->http://[device-IP]:8100<-ServerURLHere
```

Meanwhile, you should see WebDriverAgentRunner installed on your phone with "Automation Running" displayed on the screen.
Here, **http://[device-IP]:8100** is the WDA_URL needed for WiFi connection.

### 3. Configure DeepAgents-AutoGLM

#### 1. Install iOS Dependencies

Make sure you have installed AutoGLM support:

```bash
# In DeepAgents-AutoGLM project root directory
pip install -e ".[autoglm]"
# Or using uv
uv pip install -e ".[autoglm]"
```

#### 2. Configure Environment Variables

Add iOS configuration in `.deepagents/.env` or project root's `.env` file:

```bash
# ============ Basic LLM Configuration ============
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# ============ AutoGLM iOS Configuration ============
# Enable AutoGLM
AUTOGLM_ENABLED=true

# Device type: ios
AUTOGLM_PLATFORM=ios

# WebDriverAgent URL
# USB connection use: http://localhost:8100
# WiFi connection use: http://[device-IP]:8100
AUTOGLM_WDA_URL=http://localhost:8100

# Vision model configuration
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1  # Local deployment
# Or use cloud service:
# AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4  # Zhipu AI
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY  # Use EMPTY for local deployment, actual API Key for cloud

# Language configuration (zh=Chinese, en=English)
AUTOGLM_LANG=en

# Maximum steps
AUTOGLM_MAX_STEPS=100

# Expose low-level tools (false=only high-level phone_task)
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# Verbose logging (for debugging)
AUTOGLM_VERBOSE=false
```

#### 3. Start WebDriverAgent

In a new terminal, start according to your connection method:

**USB Connection:**

```bash
# Establish port mapping
iproxy 8100 8100
```

Keep this terminal running.

**WiFi Connection:**

No port mapping needed, directly use the URL output by WebDriverAgent, e.g., `http://192.168.1.100:8100`

#### 4. Use DeepAgents-AutoGLM

Start DeepAgents-AutoGLM in another terminal:

```bash
# Start Agent
deepagents

# Now you can control iPhone with natural language
> Open WeChat
> Search for "Beijing travel guide" on TikTok
> Send a WeChat message to John saying "hello"
```

### 4. Verify Installation

You can verify the iOS connection with the following command:

```bash
# Access WebDriverAgent status page
curl http://localhost:8100/status

# Should return device information in JSON format
```

### 5. iOS-Specific Notes

- ✅ iOS does not require ADB tools or ADB Keyboard
- ✅ Must connect device via WebDriverAgent
- ✅ First-time use requires trusting developer application on device
- ✅ USB connection requires keeping the `iproxy` process running
- ✅ WiFi connection requires device and computer on the same network
- ✅ WebDriverAgent needs to stay running in Xcode

---

## Common Issues

### Android-Related

**Device not found**

Try restarting ADB service:

```bash
adb kill-server
adb start-server
adb devices
```

If still not recognized, check:

1. USB debugging is enabled
2. Cable supports data transfer
3. Authorization dialog on phone has been allowed
4. Try a different USB port or cable

**Can open apps but cannot tap**

Some models require enabling both debugging options:

- **USB debugging**
- **USB debugging (Security settings)**

**Text input not working**

1. Ensure ADB Keyboard is installed on device
2. Enable ADB Keyboard in settings
3. Agent will automatically switch when input is needed

### iOS-Related

**WebDriverAgent cannot start**

1. Check if Bundle ID is unique
2. Check if signing certificate is correct
3. Check if device has trusted developer application

**Port mapping failed**

```bash
# Check if libimobiledevice is installed
brew install libimobiledevice

# Re-establish mapping
killall iproxy
iproxy 8100 8100
```

**Connection dropped**

- WiFi may have disconnected, check network connection
- USB cable may be loose, reconnect device
- Restart WebDriverAgent

**Device not found**

```bash
# Check device connection
idevice_id -ln

# Should display device UDID
```

---

## References

- [Open-AutoGLM Official Documentation](https://github.com/zai-org/Open-AutoGLM)
- [WebDriverAgent Official Repository](https://github.com/appium/WebDriverAgent)
- [Zhipu AI Open Platform](https://open.bigmodel.cn/)
- [ModelScope Platform](https://modelscope.cn/)
