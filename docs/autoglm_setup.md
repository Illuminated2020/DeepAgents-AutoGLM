# AutoGLM 配置详解

AutoGLM 支持 Android 和 iOS 两种设备类型。根据你使用的设备类型，配置方式会有所不同。

## 目录

- [AutoGLM 配置详解](#autoglm-配置详解)
  - [目录](#目录)
  - [Android 设备配置](#android-设备配置)
    - [一、安装 AutoGLM 依赖](#一安装-autoglm-依赖)
    - [二、安装 ADB 工具](#二安装-adb-工具)
    - [三、环境变量配置](#三环境变量配置)
    - [四、快速设备配置](#四快速设备配置)
    - [五、连接 Android 设备](#五连接-android-设备)
      - [方式一：USB 连接（推荐）](#方式一usb-连接推荐)
      - [方式二：WiFi 连接（Android 11+）](#方式二wifi-连接android-11)
      - [方式三：通过 USB 启用 TCP/IP 模式（Android 7+）](#方式三通过-usb-启用-tcpip-模式android-7)
    - [六、安装 ADB Keyboard](#六安装-adb-keyboard)
    - [七、视觉模型配置](#七视觉模型配置)
      - [选项 1：本地部署（需要 GPU）](#选项-1本地部署需要-gpu)
      - [选项 2：使用第三方云端服务（推荐 - 无需 GPU）](#选项-2使用第三方云端服务推荐---无需-gpu)
    - [八、使用示例](#八使用示例)
  - [iOS 设备配置](#ios-设备配置)
    - [一、环境要求](#一环境要求)
    - [二、WebDriverAgent 配置](#二webdriveragent-配置)
      - [1. 克隆 WebDriverAgent](#1-克隆-webdriveragent)
      - [2. 设置 Signing \& Capabilities](#2-设置-signing--capabilities)
      - [3. 测试 Xcode GUI 模式和 UI 自动化设置](#3-测试-xcode-gui-模式和-ui-自动化设置)
      - [4. 设备信任配置](#4-设备信任配置)
      - [5. Xcode 命令行模式部署（可选）](#5-xcode-命令行模式部署可选)
    - [三、配置 DeepAgents-AutoGLM](#三配置-deepagents-autoglm)
      - [1. 安装 iOS 依赖](#1-安装-ios-依赖)
      - [2. 配置环境变量](#2-配置环境变量)
      - [3. 启动 WebDriverAgent](#3-启动-webdriveragent)
      - [4. 使用 DeepAgents-AutoGLM](#4-使用-deepagents-autoglm)
    - [四、验证安装](#四验证安装)
    - [五、iOS 特定注意事项](#五ios-特定注意事项)
  - [常见问题](#常见问题)
    - [Android 相关](#android-相关)
    - [iOS 相关](#ios-相关)
  - [参考资源](#参考资源)

---

## Android 设备配置

> **注意**: AutoGLM 是可选功能，不安装也不影响 deepagents-cli 的其他功能使用。需要将AUTOGLM_ENABLED设置为false。

### 一、安装 AutoGLM 依赖

确保已经安装了 AutoGLM 支持：

```bash
# 在项目根目录下
# 使用 pip
pip install -e ".[autoglm]"

# 或使用 uv
uv pip install -e ".[autoglm]"
```

### 二、安装 ADB 工具

Android 设备自动化需要 ADB (Android Debug Bridge) 工具。

**macOS：**

```bash
brew install android-platform-tools
```

**Ubuntu/Debian：**

```bash
sudo apt-get install android-tools-adb
```

**Windows：**

1. 从 [官方网站](https://developer.android.com/tools/releases/platform-tools) 下载 platform-tools
2. 解压到自定义路径（如 `C:\platform-tools`）
3. 配置环境变量：
   - 右键 `此电脑` → `属性` → `高级系统设置` → `环境变量`
   - 在 `系统变量` 中找到 `Path`，点击 `编辑`
   - 点击 `新建`，添加 platform-tools 的完整路径（如 `C:\platform-tools`）
   - 点击 `确定` 保存

**验证安装：**

```bash
adb version  # 应输出版本信息
```

### 三、环境变量配置

**创建配置文件：**

```bash
# 复制示例配置文件
cp .env.example .env
```

**编辑 `.env` 文件：**

```bash
# ============ 基础 LLM 配置 ============
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# ============ AutoGLM Android 配置 ============
# 启用 AutoGLM
AUTOGLM_ENABLED=true

# 设备类型（android 或 ios）
AUTOGLM_DEVICE_TYPE=android

# 视觉模型配置
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1  # 本地部署
# 或使用云端服务：
# AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4  # 智谱 AI
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY  # 本地部署使用 EMPTY，云端使用实际 API Key

# Android 设备配置（可选，留空自动检测第一个设备）
# AUTOGLM_DEVICE_ID=

# 语言配置（zh=中文，en=英文）
AUTOGLM_LANG=zh

# 最大步骤数
AUTOGLM_MAX_STEPS=100

# 是否暴露底层工具（false=仅高级 phone_task）
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# 详细日志（调试用）
AUTOGLM_VERBOSE=false
```

详细配置说明请参考 [.env.example](../.env.example) 文件。

### 四、快速设备配置

在连接设备之前，需要在 Android 设备上启用开发者模式和 USB 调试：

```bash
# 1. 在手机上启用开发者模式
#    设置 → 关于手机 → 连续点击"版本号" 7-10 次

# 2. 启用 USB 调试
#    设置 → 开发者选项 → USB 调试 → 开启
#    （部分机型还需启用"USB 调试(安全设置)"）

# 3. 连接设备并验证
adb devices
# 应显示: XXXXXXXX    device
# 如显示 unauthorized，在手机上点击"允许 USB 调试"
```

### 五、连接 Android 设备

#### 方式一：USB 连接（推荐）

```bash
# 1. 在设备上启用开发者模式
#    设置 → 关于手机 → 找到"版本号"
#    连续快速点击"版本号" 7-10 次
#    看到"您已处于开发者模式"提示

# 2. 启用 USB 调试
#    设置 → 开发者选项 → USB 调试 → 开启
#    （部分机型还需启用"USB 调试(安全设置)"）

# 3. 使用 USB 数据线连接设备
#    注意：必须使用支持数据传输的数据线（非仅充电线）

# 4. 验证连接
adb devices
# 应显示: List of devices attached
#         XXXXXXXX    device

# 常见问题：
# - 显示 unauthorized：在手机上点击"允许 USB 调试"授权弹窗
# - 设备未显示：检查 USB 调试是否启用，尝试更换数据线或 USB 接口
# - 部分机型可能需要重启设备才能生效
```

#### 方式二：WiFi 连接（Android 11+）

```bash
# 1. 在手机上启用无线调试
#    确保手机和电脑在同一个 WiFi 网络
#    进入：设置 → 开发者选项 → 无线调试 → 启用
#    点击"使用配对码配对设备"

# 2. 配对设备（在电脑上执行，输入手机上显示的配对码）
adb pair <设备IP>:<配对端口>
# 示例: adb pair 192.168.1.100:46201
# Enter pairing code: 441750  （输入手机上显示的配对码）

# 3. 连接设备（使用无线调试端口，注意不是配对端口）
adb connect <设备IP>:<调试端口>
# 示例: adb connect 192.168.1.100:41589

# 4. 验证连接
adb devices
# 应显示: 192.168.1.100:41589    device
```

#### 方式三：通过 USB 启用 TCP/IP 模式（Android 7+）

```bash
# 1. 通过 USB 连接设备
adb devices

# 2. 启用 TCP/IP 模式（5555 端口）
adb tcpip 5555

# 3. 获取设备 IP 地址
adb shell ip addr show wlan0 | grep 'inet '
# 或在手机上查看：设置 → 关于手机 → 状态信息 → IP 地址

# 4. 拔掉 USB 线，通过 WiFi 连接
adb connect <设备IP>:5555
# 示例: adb connect 192.168.1.100:5555

# 5. 验证连接
adb devices
```

**远程连接问题排查：**

- **连接被拒绝**：确保设备和电脑在同一网络，检查防火墙是否阻止 5555 端口
- **连接断开**：WiFi 可能断开，使用 `adb connect <IP>:5555` 重新连接
- **设备重启后失效**：部分设备重启后会禁用 TCP/IP，需通过 USB 重新启用

### 六、安装 ADB Keyboard

文本输入功能需要 ADB Keyboard：

下载 [安装包](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk) 并在对应的安卓设备中进行安装。
注意，安装完成后还需要到 `设置-输入法` 或者 `设置-键盘列表` 中启用 `ADB Keyboard` 才能生效(或使用命令`adb shell ime enable com.android.adbkeyboard/.AdbIME`[How-to-use](https://github.com/senzhk/ADBKeyBoard/blob/master/README.md#how-to-use))

### 七、视觉模型配置

AutoGLM 需要视觉模型来理解手机屏幕。您可以选择本地部署或使用云端服务。

#### 选项 1：本地部署（需要 GPU）

**安装 vLLM：**

```bash
pip install vllm
```

**启动视觉模型服务：**

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

**配置环境变量：**

```bash
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY
```

#### 选项 2：使用第三方云端服务（推荐 - 无需 GPU）

**2.1 智谱 BigModel**

- **文档**: https://docs.bigmodel.cn/cn/api/introduction
- **申请 API Key**: 在智谱平台注册并申请

**配置环境变量：**

```bash
AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4
AUTOGLM_VISION_MODEL_NAME=autoglm-phone
AUTOGLM_VISION_API_KEY=your-zhipu-api-key
```

**2.2 ModelScope（魔搭社区）**

- **文档**: https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B
- **申请 API Key**: 在 ModelScope 平台注册并申请

**配置环境变量：**

```bash
AUTOGLM_VISION_MODEL_URL=https://api-inference.modelscope.cn/v1
AUTOGLM_VISION_MODEL_NAME=ZhipuAI/AutoGLM-Phone-9B
AUTOGLM_VISION_API_KEY=your-modelscope-api-key
```

**可选模型：**

| 模型                          | 下载链接                                                                                                                                                             | 说明                 |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| AutoGLM-Phone-9B              | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)`<br>`[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)                           | 针对中文手机应用优化 |
| AutoGLM-Phone-9B-Multilingual | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)`<br>`[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) | 支持英语等多语言场景 |

### 八、使用示例

完成以上配置后，即可开始使用：

```bash
$ deepagents

用户：打开微信
Agent：我将使用 phone_task 工具打开微信...

用户：搜索最近的咖啡店
Agent：我将使用 phone_task 工具打开地图应用并搜索咖啡店...

用户：给张三发微信消息说"明天见"
Agent：我将使用 phone_task 工具打开微信、找到张三的聊天并发送消息...
```

## iOS 设备配置

### 一、环境要求

- macOS 操作系统
- Xcode（最新版本，可在 App Store 中下载）
- 苹果开发者账号（免费账号即可，无需付费）
- iOS 设备（iPhone/iPad）
- USB 数据线或同一 WiFi 网络

### 二、WebDriverAgent 配置

WebDriverAgent 是 iOS 自动化的核心组件，需要在 iOS 设备上运行。

#### 1. 克隆 WebDriverAgent

```bash
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
```

直接点击 `WebDriverAgent.xcodeproj` 即可使用 Xcode 打开。

#### 2. 设置 Signing & Capabilities

1. 在 Xcode 中选中 `WebDriverAgent`，出现 General、Signing&Capabilities 等选项
2. 进入 `Signing & Capabilities` 选项卡
3. 勾选 `Automatically manage signing`，在 Team 中选择自己的开发者账号
4. 将 Bundle ID 改为唯一标识符，例如：`com.yourname.WebDriverAgentRunner`

![设置签名1](resources/ios0_WebDriverAgent0.png)

5. 在 TARGETS 中，建议将 WebDriverAgentLib、WebDriverAgentRunner、IntegrationApp 的 `Signing & Capabilities` 都按照相同方式设置

![设置签名2](resources/ios0_WebDriverAgent1.png)

#### 3. 测试 Xcode GUI 模式和 UI 自动化设置

建议先测试 GUI 模式能否成功安装 WebDriverAgent，再进行后续步骤。
Mac 和 iPhone 有 USB 和 WiFi 两种连接方式，建议通过 USB 方式，成功率更高。

**通过 WiFi 连接（可选）：**

需要满足以下条件：

1. 先通过 USB 连接。在 Finder 中选中连接的 iPhone，在"通用"中勾选"在 WiFi 中显示这台 iPhone"
2. Mac 与 iPhone 处于同一 WiFi 网络之下

**具体步骤：**

1. 从项目 Target 选择 `WebDriverAgentRunner`
2. 选择你的设备

![选择设备](resources/select-your-iphone-device.png)

3. 长按"▶️"运行按钮，选择 "Test" 后开始编译并部署到你的 iPhone 上

![开始测试](resources/start-wda-testing.png)

部署成功的标志：

1. Xcode 没有报错
2. 你可以在 iPhone 上找到名为 WebDriverAgentRunner 的 App

#### 4. 设备信任配置

首次运行时，需要在 iPhone 上完成以下设置，然后重新编译和部署：

1. **输入解锁密码**
2. **信任开发者应用**

   - 进入：设置 → 通用 → VPN与设备管理
   - 在"开发者 App"中选择对应开发者
   - 点击信任"XXX"

   ![信任设备](resources/trust-dev-app.jpg)
3. **启用 UI 自动化**

   - 进入：设置 → 开发者
   - 打开 UI 自动化设置

   ![启用UI自动化](resources/enable-ui-automation.jpg)

#### 5. Xcode 命令行模式部署（可选）

1. 安装 libimobiledevice，用于与 iPhone/iPad 建立连接与通信：

```bash
brew install libimobiledevice

# 设备检查
idevice_id -ln
```

2. 使用 xcodebuild 安装 WebDriverAgent（命令行也需要进行"设备信任配置"，参考 GUI 模式下的方法）：

```bash
cd WebDriverAgent

xcodebuild -project WebDriverAgent.xcodeproj \
           -scheme WebDriverAgentRunner \
           -destination 'platform=iOS,name=YOUR_PHONE_NAME' \
           test
```

这里，`YOUR_PHONE_NAME` 可以在 Xcode 的 GUI 中看到。

WebDriverAgent 成功运行后，会在 Xcode 控制台输出类似以下信息：

```
ServerURLHere->http://[设备IP]:8100<-ServerURLHere
```

同时，观察到手机上安装好了 WebDriverAgentRunner，屏幕显示 "Automation Running" 字样。
其中，**http://[设备IP]:8100** 为 WiFi 连接所需的 WDA_URL。

### 三、配置 DeepAgents-AutoGLM

#### 1. 安装 iOS 依赖

确保已经安装了 AutoGLM 支持：

```bash
# 在 DeepAgents-AutoGLM 项目根目录下
pip install -e ".[autoglm]"
# 或使用 uv
uv pip install -e ".[autoglm]"
```

#### 2. 配置环境变量

在 `.deepagents/.env` 或项目根目录的 `.env` 文件中添加 iOS 配置：

```bash
# ============ 基础 LLM 配置 ============
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# ============ AutoGLM iOS 配置 ============
# 启用 AutoGLM
AUTOGLM_ENABLED=true

# 设备类型：ios
AUTOGLM_DEVICE_TYPE=ios

# WebDriverAgent URL
# USB 连接使用：http://localhost:8100
# WiFi 连接使用：http://[设备IP]:8100
AUTOGLM_WDA_URL=http://localhost:8100

# 视觉模型配置
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1  # 本地部署
# 或使用云端服务：
# AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4  # 智谱 AI
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY  # 本地部署使用 EMPTY，云端使用实际 API Key

# 语言配置（zh=中文，en=英文）
AUTOGLM_LANG=zh

# 最大步骤数
AUTOGLM_MAX_STEPS=100

# 是否暴露底层工具（false=仅高级 phone_task）
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# 详细日志（调试用）
AUTOGLM_VERBOSE=false
```

#### 3. 启动 WebDriverAgent

在一个新的终端中，根据连接方式启动：

**USB 连接方式：**

```bash
# 建立端口映射
iproxy 8100 8100
```

保持此终端运行。

**WiFi 连接方式：**

无需端口映射，直接使用 WebDriverAgent 输出的 URL，例如：`http://192.168.1.100:8100`

#### 4. 使用 DeepAgents-AutoGLM

在另一个终端中启动 DeepAgents-AutoGLM：

```bash
# 启动 Agent
deepagents

# 现在可以使用自然语言控制 iPhone
> 打开微信
> 在抖音搜索"北京旅游攻略"
> 给张三发微信消息说"你好"
```

### 四、验证安装

可以通过以下命令验证 iOS 连接是否正常：

```bash
# 访问 WebDriverAgent 状态页面
curl http://localhost:8100/status

# 应该返回 JSON 格式的设备信息
```

### 五、iOS 特定注意事项

- ✅ iOS 不需要安装 ADB 工具和 ADB Keyboard
- ✅ 必须通过 WebDriverAgent 连接设备
- ✅ 首次使用需要在设备上信任开发者应用
- ✅ USB 连接需要保持 `iproxy` 进程运行
- ✅ WiFi 连接要求设备与电脑在同一网络
- ✅ WebDriverAgent 需要在 Xcode 中保持运行状态

---

## 常见问题

### Android 相关

**设备未找到**

尝试通过重启 ADB 服务来解决：

```bash
adb kill-server
adb start-server
adb devices
```

如果仍然无法识别，请检查：

1. USB 调试是否已开启
2. 数据线是否支持数据传输
3. 手机上弹出的授权框是否已点击「允许」
4. 尝试更换 USB 接口或数据线

**能打开应用，但无法点击**

部分机型需要同时开启两个调试选项：

- **USB 调试**
- **USB 调试(安全设置)**

**文本输入不工作**

1. 确保设备已安装 ADB Keyboard
2. 在设置中启用 ADB Keyboard
3. Agent 会在需要输入时自动切换

### iOS 相关

**WebDriverAgent 无法启动**

1. 检查 Bundle ID 是否唯一
2. 检查签名证书是否正确
3. 检查设备是否已信任开发者应用

**端口映射失败**

```bash
# 检查 libimobiledevice 是否安装
brew install libimobiledevice

# 重新建立映射
killall iproxy
iproxy 8100 8100
```

**连接断开**

- WiFi 可能断开，检查网络连接
- USB 线可能松动，重新连接设备
- 重启 WebDriverAgent

**设备未找到**

```bash
# 检查设备连接
idevice_id -ln

# 应该显示设备 UDID
```

---

## 参考资源

- [Open-AutoGLM 官方文档](https://github.com/zai-org/Open-AutoGLM)
- [WebDriverAgent 官方仓库](https://github.com/appium/WebDriverAgent)
- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [ModelScope 平台](https://modelscope.cn/)
