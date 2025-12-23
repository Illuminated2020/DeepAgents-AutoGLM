# 🚀🧠 DeepAgents-AutoGLM

English | [中文](./README.md)

An open-source intelligent programming assistant based on the [deepagents](https://github.com/langchain-ai/deepagents) framework integrated with [AutoGLM](https://github.com/zai-org/Open-AutoGLM) phone control capabilities. Runs in the terminal and supports Android device automation.

## 💡 Project Highlights

Compared to the original [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) project, this project brings the following core advantages through **middleware architecture**:

- **🔗 Capability Composition**: AutoGLM seamlessly integrates with Web search, Shell, skills system, and memory system, enabling full automation of "search information → analyze decisions → phone operations"
- **🧠 Intelligent Division of Labor**: Main Agent handles task planning and complex decision-making, while sub-Agent `phone_task` focuses on phone operation execution with clear responsibility boundaries
- **🎯 Fine-Grained Control**: Leverage Anthropic's [Agent SKILL](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) to create customized operation workflows for specific apps (like Rednote, QQ), enabling automation of complex scenarios
- **🔌 Modular Extension**: Pluggable design, AutoGLM as an optional middleware, enabled on-demand via environment variables

**Typical Scenario Example**:
```bash
$ deepagents
> Search for the latest AI news, summarize it in Rednote style, and post it on Rednote

# Execution flow:
# 1. web_search searches for AI news
# 2. LLM analyzes and generates Rednote content
# 3. Main Agent plans posting workflow via xiaohongshu-post skill
# 4. Invokes sub-agent phone_task to execute phone operations (open app, input, publish)
# 5. agent.md records posting history
```

**Core Features:**
- **Built-in Toolset**: File operations (read, write, edit, search), shell commands, web search, sub-agent delegation
- **Customizable Skills**: Add domain-specific capabilities through progressive disclosure skill system
- **Persistent Memory**: Agent remembers your preferences, coding style, and project context
- **Project-Aware**: Automatically detects project root directory and loads project-specific configurations
- **Android Automation** (Optional): Integrated AutoGLM for intelligent phone control (tap, swipe, input, etc.)
- **Vision-Guided Control** (Optional): Use vision-language models to understand and operate phone GUI

<img src="./DA-AutoGLM.png" alt="deep agent" width="100%"/>

## 📺 Live Demos

See DeepAgents-AutoGLM in action with real-world use cases:

- 🎨 **[Rednote Auto-Posting Demo](http://xhslink.com/o/FdRsaQQpUz)** - Demonstrates how the Agent automatically searches content, generates posts, and publishes to Rednote
- 💬 **[QQ Auto-Reply Demo](http://xhslink.com/o/6v5umdBoznW)** - Shows how to intelligently identify and automatically reply to unread QQ messages

## 🚀 Quick Start

### Basic Installation

Clone this project and install dependencies.

**Install with pip:**
```bash
# Clone repository
git clone git@github.com:Illuminated2020/DeepAgents-AutoGLM.git
cd DeepAgents-AutoGLM

# Install basic dependencies
pip install -e .
```

**Or use uv (recommended):**
```bash
# Clone repository
git clone git@github.com:Illuminated2020/DeepAgents-AutoGLM.git
cd DeepAgents-AutoGLM

# Create virtual environment and install
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
uv pip install -e .
```

**Run Agent in terminal:**
```bash
deepagents
```

**Get help:**
```bash
deepagents help
```

**Common options:**
```bash
# Use specific Agent configuration
deepagents --agent mybot

# Create new Agent
deepagents create mybot

# List all Agents
deepagents list

# Auto-approve tool usage (skip manual confirmation prompts)
deepagents --auto-approve

# Execute code in remote sandbox (requires configuration)
deepagents --sandbox modal        # or runloop, daytona
deepagents --sandbox-id dbx_123   # Reuse existing sandbox

# Manage skills
deepagents skills list            # List all skills
deepagents skills create my-skill # Create new skill
```

Type naturally as you would in a chat interface. The Agent will use its built-in tools, skills, and memory to help you complete tasks.

### AutoGLM Installation (Optional - Android Automation)

If you need Android device automation features, install AutoGLM support.

> **Note**: AutoGLM is an optional feature. Not installing it won't affect other deepagents-cli functionalities.

**1. Install AutoGLM dependencies:**

```bash
# In project root directory
# Using pip
pip install -e ".[autoglm]"

# Or using uv
uv pip install -e ".[autoglm]"
```

**2. Install ADB tools:**

- **macOS:** `brew install android-platform-tools`
- **Ubuntu/Debian:** `sudo apt-get install android-tools-adb`
- **Windows:** 
  1. Download platform-tools from [official website](https://developer.android.com/tools/releases/platform-tools)
  2. Extract to a custom path (e.g., `C:\platform-tools`)
  3. Configure environment variables:
     - Right-click `This PC` → `Properties` → `Advanced system settings` → `Environment Variables`
     - Find `Path` in `System variables`, click `Edit`
     - Click `New`, add the full path to platform-tools (e.g., `C:\platform-tools`)
     - Click `OK` to save


Verify installation:
```bash
adb version  # Should output version information
```

**3. Quick device configuration:**

```bash
# 1. Enable Developer Mode on your phone
#    Settings → About phone → Tap "Build number" 7-10 times

# 2. Enable USB Debugging
#    Settings → Developer options → USB debugging → Enable
#    (Some devices also need to enable "USB debugging (Security settings)")

# 3. Connect device and verify
adb devices
# Should display: XXXXXXXX    device
# If showing unauthorized, tap "Allow USB debugging" on your phone
```

**4. Install ADB Keyboard (for text input):**

Download and install [ADBKeyboard.apk](https://github.com/senzhk/ADBKeyBoard/raw/master/ADBKeyboard.apk):

- **Method 1: Install via ADB** (execute on computer)
  ```bash
  wget https://github.com/senzhk/ADBKeyBoard/raw/master/ADBKeyboard.apk
  adb install -r ADBKeyboard.apk
  ```

- **Method 2: Manual installation**
  - Open the download link in your phone's browser
  - Download the APK file and tap to install
  - Allow installation from this source

**Enable ADB Keyboard:**

- **Method 1: Manual enable**
  - Go to `Settings` → `Language and input` → `Virtual keyboard` or `Keyboard list`
  - Find and enable `ADB Keyboard`

- **Method 2: Enable via command** (execute on computer)
  ```bash
  adb shell ime enable com.android.adbkeyboard/.AdbIME
  ```
**4. Configure environment variables and vision model:**

For detailed configuration steps (including environment variables, WiFi connection, model deployment, etc.), please refer to the [AutoGLM Configuration Details](#autoglm-configuration-details) section.

**Available models:**

| Model                          | Download Links                                                                                                                                                        | Description                                    |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| AutoGLM-Phone-9B               | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B)                           | Optimized for Chinese phone applications       |
| AutoGLM-Phone-9B-Multilingual  | [🤗 Hugging Face](https://huggingface.co/zai-org/AutoGLM-Phone-9B-Multilingual)<br>[🤖 ModelScope](https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B-Multilingual) | Supports English and other multilingual scenarios |

## Built-in Tools

The Agent comes with the following built-in tools (usable without configuration):

### Basic Tools

| Tool | Description |
|------|-------------|
| `ls` | List files and directories |
| `read_file` | Read file contents |
| `write_file` | Create or overwrite file |
| `edit_file` | Make targeted edits to existing files |
| `glob` | Find files matching patterns (e.g., `**/*.py`) |
| `grep` | Search text patterns across files |
| `shell` | Execute shell commands (local mode) |
| `execute` | Execute commands in remote sandbox (sandbox mode) |
| `web_search` | Search the web using Tavily API |
| `fetch_url` | Fetch webpage and convert to Markdown |
| `task` | Delegate work to sub-agents for parallel execution |
| `write_todos` | Create and manage task lists for complex work |

### AutoGLM Tools (Requires `AUTOGLM_ENABLED=true`)

| Tool | Description |
|------|-------------|
| `phone_task` | 🎯 **Advanced Task Tool** - Execute natural language phone tasks (Recommended) |
| `phone_tap` | Tap at specified coordinates |
| `phone_swipe` | Execute swipe gesture |
| `phone_type` | Input text |
| `phone_screenshot` | Capture screen |
| `phone_back` | Press back button |
| `phone_home` | Press home button |
| `phone_launch` | Launch app by name |

**AutoGLM Usage Examples:**

```bash
$ deepagents
User: Open WeChat
Agent: Using phone_task tool to automatically open WeChat app

User: Search for "Beijing travel guide" on Douyin
Agent: Using phone_task tool to open Douyin and search for content

User: Send WeChat message to Xiaoming saying "Hello"
Agent: Using phone_task tool to open WeChat, find the chat, and send message
```

> [!WARNING]
> **Human-in-the-Loop (HITL) Requirements**
>
> Potentially destructive operations require user approval before execution:
> - **File operations**: `write_file`, `edit_file`
> - **Command execution**: `shell`, `execute`
> - **External requests**: `web_search`, `fetch_url`
> - **Delegation**: `task` (sub-agents)
> - **Phone operations**: `phone_task`, `phone_tap`, `phone_swipe`, etc.
>
> Each operation will display details and prompt for approval. Use `--auto-approve` to skip prompts:
> ```bash
> deepagents --auto-approve
> ```

## Agent Configuration

Each Agent has its own configuration directory `~/.deepagents/<agent_name>/`, defaulting to `agent`.

```bash
# List all configured Agents
deepagents list

# Create new Agent
deepagents create <agent_name>
```

## Customization

There are two main ways to customize your Agent: **memory** and **skills**.

Each Agent has its own global configuration directory `~/.deepagents/<agent_name>/`:

```
~/.deepagents/<agent_name>/
  ├── agent.md              # Auto-loaded global personality/style
  └── skills/               # Auto-loaded Agent-specific skills
      ├── web-research/
      │   └── SKILL.md
      └── langgraph-docs/
          └── SKILL.md
```

Projects can extend global configuration with project-specific instructions and skills:

```
my-project/
  ├── .git/
  └── .deepagents/
      ├── agent.md          # Project-specific instructions
      ├── .env              # Project-specific environment config (AutoGLM, etc.)
      └── skills/           # Project-specific skills
          └── custom-tool/
              └── SKILL.md
```

The CLI automatically detects the project root directory (via `.git`) and loads:
- Project-specific `agent.md` (from `[project root]/.deepagents/agent.md`)
- Project-specific skills (from `[project root]/.deepagents/skills/`)
- Project-specific environment config (from `[project root]/.deepagents/.env`)

Global and project configurations load together, allowing you to:
- Maintain general coding style/preferences in global agent.md
- Add project-specific context, conventions, or guidelines in project agent.md
- Share project-specific skills through version control
- Override global skills with project-specific versions (when skill names match)
- Configure different AutoGLM settings for different projects

### agent.md File

The `agent.md` file provides persistent memory, automatically loaded at the start of each session. Global and project-level `agent.md` files load together and inject into the system prompt.

**Global `agent.md`** (`~/.deepagents/agent/agent.md`)
  - Your personality, style, and general coding preferences
  - General tone and communication style
  - Universal coding preferences (formatting, type hints, etc.)
  - Tool usage patterns applicable to all scenarios
  - Workflows and methodologies that don't change with projects

**Project `agent.md`** (`.deepagents/agent.md` in project root)
  - Project-specific context and conventions
  - Project architecture and design patterns
  - Coding conventions specific to this codebase
  - Testing strategies and deployment processes
  - Team guidelines and project structure

**How it works (AgentMemoryMiddleware):**
- Both files load at startup and inject as `<user_memory>` and `<project_memory>` into system prompt
- Adds [memory management instructions](deepagents_cli/agent_memory.py#L44-L158) explaining when/how to update memory files

**When Agent updates memory:**
- **Immediately** when you describe how it should behave
- **Immediately** when you give feedback on its work
- When you explicitly ask it to remember something
- When patterns or preferences emerge from interactions

Agent uses `edit_file` to update memory when learning preferences or receiving feedback.

### Project Memory Files

In addition to `agent.md`, you can create additional memory files in `.deepagents/` for structured project knowledge. These work similarly to [Anthropic's memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool). The Agent receives [detailed instructions](deepagents_cli/agent_memory.py#L123-L158) on when to read and update these files.

**How it works:**
1. Create Markdown files in `[project root]/.deepagents/` (e.g., `api-design.md`, `architecture.md`, `deployment.md`)
2. Agent checks these files when tasks are relevant (not auto-loaded into every prompt)
3. Agent uses `write_file` or `edit_file` to create/update memory files when learning project patterns

**Example workflow:**
```bash
# Agent discovers deployment patterns and saves
.deepagents/
├── agent.md           # Always loaded (personality + conventions)
├── architecture.md    # Loaded on demand (system design)
├── deployment.md      # Loaded on demand (deployment process)
└── .env              # AutoGLM and other environment config
```

**When Agent reads memory files:**
- At the start of new sessions (checks which files exist)
- Before answering project-specific topic questions
- When you reference past work or patterns
- When executing tasks that match saved knowledge domains

**Advantages:**
- **Persistent learning**: Agent remembers project patterns across sessions
- **Team collaboration**: Share project knowledge through version control
- **Context retrieval**: Only load relevant memory when needed (reduces token usage)
- **Structured knowledge**: Organize information by domain (API, architecture, deployment, etc.)

### Skills

Skills are reusable Agent capabilities that provide specialized workflows and domain knowledge. Example skills are provided in the `examples/skills/` directory:

- **web-research** - Structured web research workflow with planning, parallel delegation, and synthesis
- **langgraph-docs** - LangGraph documentation lookup and guidance
- **xiaohongshu-posting** - Rednote (Little Red Book) automated posting workflow, supports both short notes and long articles

To use example skills globally in the default Agent, simply copy them to your Agent's global or project-level skills directory:

```bash
mkdir -p ~/.deepagents/agent/skills
cp -r examples/skills/web-research ~/.deepagents/agent/skills/
```

Manage skills:

```bash
# List all skills (global + project)
deepagents skills list

# List only project skills
deepagents skills list --project

# Create new global skill from template
deepagents skills create my-skill

# Create new project skill
deepagents skills create my-tool --project

# View skill details
deepagents skills info web-research

# View only project skill info
deepagents skills info my-tool --project
```

To use a skill (e.g., langgraph-docs skill), simply enter a request related to the skill, and it will be automatically used.

```bash
$ deepagents
$ "Create an agent.py script implementing a LangGraph Agent"
```

Skills follow Anthropic's [progressive disclosure pattern](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - the Agent knows skills exist but only reads full instructions when needed.

1. **At startup** - SkillsMiddleware scans `~/.deepagents/agent/skills/` and `.deepagents/skills/` directories
2. **Parse metadata** - Extracts YAML frontmatter (name + description) from each `SKILL.md` file
3. **Inject prompt** - Adds skill list with descriptions to system prompt: "Available skills: web-research - for web research tasks..."
4. **Progressive loading** - Agent only uses `read_file` to read full `SKILL.md` content when task matches skill description
5. **Execute workflow** - Agent follows step-by-step instructions in skill file

## AutoGLM Configuration Details

### I. Environment Variable Configuration

**Create configuration file:**

```bash
# Copy example configuration file
cp .env.example .env
```

**Edit `.env` file:**

```bash
# ============ Basic LLM Configuration ============
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4

# ============ AutoGLM Configuration ============
# Enable AutoGLM
AUTOGLM_ENABLED=true

# Vision model configuration
AUTOGLM_VISION_MODEL_URL=http://localhost:8000/v1  # Local deployment
# Or use cloud service:
# AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4  # Zhipu AI
AUTOGLM_VISION_MODEL_NAME=autoglm-phone-9b
AUTOGLM_VISION_API_KEY=EMPTY  # Use EMPTY for local deployment, use actual API Key for cloud

# Device configuration (optional, leave empty to auto-detect first device)
# AUTOGLM_DEVICE_ID=

# Language configuration (zh=Chinese, en=English)
AUTOGLM_LANG=zh

# Maximum steps
AUTOGLM_MAX_STEPS=100

# Expose low-level tools (false=only high-level phone_task)
AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS=false

# Verbose logging (for debugging)
AUTOGLM_VERBOSE=false
```

For detailed configuration, please refer to the [.env.example](.env.example) file.

### II. Connecting Android Devices

#### Method 1: USB Connection (Recommended)

```bash
# 1. Enable Developer Mode on device
#    Settings → About phone → Find "Build number"
#    Tap "Build number" 7-10 times continuously
#    You should see "You are now a developer" message

# 2. Enable USB Debugging
#    Settings → Developer options → USB debugging → Enable
#    (Some devices also need to enable "USB debugging (Security settings)")

# 3. Connect device with USB cable
#    Note: Must use a data-capable cable (not charging-only cable)

# 4. Verify connection
adb devices
# Should display: List of devices attached
#                 XXXXXXXX    device

# Common issues:
# - Showing unauthorized: Tap "Allow USB debugging" authorization popup on your phone
# - Device not showing: Check if USB debugging is enabled, try different cable or USB port
# - Some devices may require a restart to take effect
```

#### Method 2: WiFi Connection (Android 11+)

```bash
# 1. Enable wireless debugging on your phone
#    Ensure phone and computer are on the same WiFi network
#    Go to: Settings → Developer options → Wireless debugging → Enable
#    Tap "Pair device with pairing code"

# 2. Pair device (execute on computer, enter pairing code shown on phone)
adb pair <device-IP>:<pairing-port>
# Example: adb pair 192.168.1.100:46201
# Enter pairing code: 441750  (enter code shown on phone)

# 3. Connect device (use wireless debugging port, not pairing port)
adb connect <device-IP>:<debug-port>
# Example: adb connect 192.168.1.100:41589

# 4. Verify connection
adb devices
# Should display: 192.168.1.100:41589    device
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

# 4. Disconnect USB cable, connect via WiFi
adb connect <device-IP>:5555
# Example: adb connect 192.168.1.100:5555

# 5. Verify connection
adb devices
```

**Remote connection troubleshooting:**

- **Connection refused**: Ensure device and computer are on the same network, check if firewall blocks port 5555
- **Connection dropped**: WiFi may have disconnected, use `adb connect <IP>:5555` to reconnect
- **Not working after device restart**: Some devices disable TCP/IP after restart, need to re-enable via USB

### III. Installing ADB Keyboard

Text input functionality requires ADB Keyboard:

```bash
# Download and install
wget https://github.com/senzhk/ADBKeyBoard/raw/master/ADBKeyboard.apk
adb install -r ADBKeyboard.apk

# Method 1: Enable via command (recommended)
adb shell ime enable com.android.adbkeyboard/.AdbIME

# Method 2: Enable manually on device
# Settings → Language and input → Virtual keyboard → Enable ADB Keyboard
```

### IV. Vision Model Configuration

AutoGLM requires a vision model to understand phone screens. You can choose local deployment or cloud services.

#### Option 1: Local Deployment (Requires GPU)

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

#### Option 2: Using Third-party Cloud Services (Recommended - No GPU Required)

**2.1 Zhipu BigModel**

- **Documentation**: https://docs.bigmodel.cn/cn/api/introduction
- **Apply for API Key**: Register and apply on Zhipu platform

**Configure environment variables:**

```bash
AUTOGLM_VISION_MODEL_URL=https://open.bigmodel.cn/api/paas/v4
AUTOGLM_VISION_MODEL_NAME=autoglm-phone
AUTOGLM_VISION_API_KEY=your-zhipu-api-key
```

**2.2 ModelScope**

- **Documentation**: https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B
- **Apply for API Key**: Register and apply on ModelScope platform

**Configure environment variables:**

```bash
AUTOGLM_VISION_MODEL_URL=https://api-inference.modelscope.cn/v1
AUTOGLM_VISION_MODEL_NAME=ZhipuAI/AutoGLM-Phone-9B
AUTOGLM_VISION_API_KEY=your-modelscope-api-key
```

### V. Usage Examples

After completing the above configuration, you can start using:

```bash
$ deepagents

User: Open WeChat
Agent: I will use the phone_task tool to open WeChat...

User: Search for nearby coffee shops
Agent: I will use the phone_task tool to open the Maps app and search for coffee shops...

User: Send WeChat message to Zhang San saying "See you tomorrow"
Agent: I will use the phone_task tool to open WeChat, find Zhang San's chat, and send the message...
```

### VI. Supported Apps

AutoGLM has built-in configurations for 50+ mainstream apps:

| Category | Apps |
|----------|------|
| Social & Communication | WeChat, QQ, Weibo, DingTalk |
| E-commerce & Shopping | Taobao, JD, Pinduoduo, Tmall |
| Food & Delivery | Meituan, Ele.me, KFC, McDonald's |
| Travel & Transportation | Ctrip, 12306, Didi, Amap, Baidu Maps |
| Video & Entertainment | Douyin, Kuaishou, Bilibili, iQIYI, Tencent Video |
| Music & Audio | NetEase Cloud Music, QQ Music, Ximalaya |
| Life Services | Dianping, Alipay |
| Content Communities | Rednote, Zhihu, Douban |
| System Apps | Phone, Messages, Camera, Settings, Browser |

## Technical Architecture

### Core Components

**deepagents-cli** is built on the [deepagents](https://github.com/langchain-ai/deepagents) framework, using LangChain Middleware mechanism for modular extension:

- **Agent Management**: Create and manage multiple Agent configurations based on `create_deep_agent`
- **Skills System**: Progressive disclosure skills, load domain knowledge on demand
- **Memory System**: Global and project-level persistent memory (`agent.md`)
- **Shell Integration**: Local shell command execution support
- **AutoGLM Middleware** (Optional): Android GUI automation capabilities

### AutoGLM Integration (Optional)

When AutoGLM is enabled, Android control capabilities are injected through the **Middleware mechanism**:

**Core Design**
- Use `content_blocks` to handle multimodal messages (text + screenshots)
- Use `HumanInTheLoopMiddleware` for sensitive operation approval
- Use sub-agent mechanism to create specialized Phone Agent

**Workflow**
```
User request → Main Agent → phone_task tool → Phone Sub-Agent
                                          ↓
                     ← Return result ← Execute action ← Vision Model understands screen
```

**Component Structure**
- `AutoGLMMiddleware`: Inject tools and system checks (`middleware/autoglm_middleware.py`)
- `ADBController`: ADB command encapsulation (`middleware/autoglm/adb_controller.py`)
- `ActionParser`: Parse model output actions (`middleware/autoglm/action_parser.py`)

## Development

### Running Tests

Run the test suite:

```bash
uv sync --all-groups

make test
```

### Running During Development

```bash
# In project root directory
uv run deepagents

# Or install in editable mode
uv pip install -e .
deepagents
```

### Modifying the CLI

- **UI changes** → Edit `ui.py` or `input.py`
- **Add new tools** → Edit `tools.py`
- **Change execution flow** → Edit `execution.py`
- **Add commands** → Edit `commands.py`
- **Agent configuration** → Edit `agent.py`
- **Skills system** → Edit `skills/` module
- **Constants/colors** → Edit `config.py`
- **AutoGLM middleware** → Edit `middleware/autoglm_middleware.py`

## Roadmap

### ✅ Completed Features

- ✅ AutoGLM middleware integration (vision-guided phone control)
- ✅ Rednote (Little Red Book) auto-posting skill
- ✅ Two-level interrupt mechanism (Ctrl+C graceful exit)
- ✅ Long text input support
- ✅ Improved AutoGLM interrupt handling mechanism

### 🚧 In Progress / 📋 Planned

- 🚧 `phone_task` may need to return more specific ToolMessage when interrupted, optimization under consideration
- 🚧 iOS device support
- 📋 More phone operation skills (**Contributions welcome!**)

## Contributing

**We especially welcome contributions of phone operation related skills!**

### Skill Contribution Areas

Automation skills for e-commerce, social media, lifestyle services, content creation, etc.

### How to Contribute

**Recommended: Use the `skill-creator` skill to create new skills:**

```bash
# 1. Copy skill-creator to your skills directory
cp -r examples/skills/skill-creator ~/.deepagents/agent/skills/

# 2. Let the Agent help you create a skill
deepagents
> Help me create a skill for [describe your skill]
# Agent will use skill-creator to guide you through the creation process
```

**Or create manually:**

1. Check `examples/skills/xiaohongshu-posting/SKILL.md` for skill format
2. Create new skill with `deepagents skills create <skill-name>`
3. Write `SKILL.md` (including YAML metadata and usage instructions)
4. Submit Pull Request to `examples/skills/` directory

## Acknowledgments

This project is built upon the following open-source projects:

- [deepagents](https://github.com/langchain-ai/deepagents) - Powerful Agent framework provided by LangChain
- [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) - Vision-guided phone automation capabilities provided by Zhipu AI

Thanks to the contributors of these projects for their hard work and open-source spirit!
