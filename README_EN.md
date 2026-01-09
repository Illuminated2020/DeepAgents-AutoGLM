# 🚀🧠 DeepAgents-AutoGLM

English | [中文](./README.md)

An open-source intelligent assistant based on the [deepagents](https://github.com/langchain-ai/deepagents) framework integrated with [AutoGLM](https://github.com/zai-org/Open-AutoGLM) phone control capabilities. Runs in the terminal and supports Android and iOS device automation.

## 💡 Project Highlights

Compared to the original [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) project, this project is based on the deepagents framework and integrates AutoGLM through **middleware mechanism**, bringing the following core advantages:

- **🔗 Capability Composition**: AutoGLM seamlessly integrates with Web search, Shell, skills system, and memory system, enabling full automation of "search information → analyze decisions → phone operations"
- **🧠 Intelligent Division of Labor**: Main Agent handles task planning and complex decision-making, while sub-Agent `phone_task` focuses on phone operation execution with clear responsibility boundaries
- **🎯 Fine-Grained Control**: Leverage Anthropic's [Agent SKILL](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) to create customized operation workflows for specific apps (like Xiaohongshu, QQ), enabling automation of complex scenarios
- **🔌 Modular Extension**: Pluggable design, AutoGLM as an optional middleware, enabled on-demand via environment variables

**Typical Scenario Example**:

```bash
$ deepagents
> Search for the latest AI news, summarize it in Xiaohongshu style, and post it on Xiaohongshu

# Execution flow:
# 1. web_search searches for AI news
# 2. LLM analyzes and generates Xiaohongshu content
# 3. Main Agent plans posting workflow via xiaohongshu-post skill
# 4. Invokes sub-Agent phone_task to execute phone operations (open app, input, publish)
# 5. agent.md records posting history
```

**Core Features:**

- **Built-in Toolset**: File operations (read, write, edit, search), Shell commands, web search, sub-agent delegation
- **Customizable Skills**: Add domain-specific capabilities through progressive disclosure skill system
- **Persistent Memory**: Agent remembers your preferences, coding style, and project context
- **Project-Aware**: Automatically detects project root directory and loads project-specific configurations
- **Android/iOS Automation** (Optional): Integrated AutoGLM for intelligent phone control (tap, swipe, input, etc.)
- **Vision-Guided Control** (Optional): Use vision-language models to understand and operate phone GUI

<img src="./DA-AutoGLM.png" alt="deep agent" width="100%"/>

## 📺 Live Demos

See DeepAgents-AutoGLM in action with real-world use cases:

- 🎨 **[Xiaohongshu Auto-Posting Demo](http://xhslink.com/o/FdRsaQQpUz)** - Demonstrates how the Agent automatically searches content, generates posts, and publishes to Xiaohongshu
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

### Environment Variables Configuration

Create a `.env` file in the project root directory to configure environment variables. You can copy `.env.example` as a starting point:

```bash
cp .env.example .env
```

Then edit the `.env` file as needed. Here are the environment variable descriptions:

#### Required Configuration

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `OPENAI_API_KEY` | OpenAI API key (or compatible API key, supports OpenAI, DeepSeek, Qwen, etc.) | `sk-xxxx` |
| `OPENAI_MODEL` | Model name to use | `glm-4.7`, `deepseek-v3.2`, `gpt-5` |

#### Optional Configuration

**API Configuration:**

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `OPENAI_BASE_URL` | API base URL (not required for official OpenAI service; must be set for other compatible services) | `https://api.deepseek.com/v1` |

**LangSmith Tracing (Optional):**

For monitoring and debugging Agent behavior. Get API key at [https://smith.langchain.com/](https://smith.langchain.com/).

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `LANGSMITH_TRACING` | Enable LangSmith tracing | `true` / `false` |
| `LANGSMITH_ENDPOINT` | LangSmith API endpoint | `https://api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | LangSmith API key | `ls_xxxx` |
| `LANGSMITH_PROJECT` | LangSmith project name | `deepagents-project` |

**Tavily Web Search (Optional):**

Provides web search capabilities. Get API key at [https://tavily.com/](https://tavily.com/).

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `TAVILY_API_KEY` | Tavily API key | `tvly-xxxx` |

**AutoGLM Configuration (Optional):**

If you don't need Android/iOS automation features, set `AUTOGLM_ENABLED=false`. For detailed configuration, refer to the [AutoGLM Installation](#autoglm-installation-optional---androidios-automation) section below.

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `AUTOGLM_ENABLED` | Enable AutoGLM functionality | `false` |
| `AUTOGLM_PLATFORM` | Platform to control: `android` or `ios` | `android` |
| `AUTOGLM_LANG` | System prompt language: `zh` or `en` | `zh` |
| `AUTOGLM_MAX_STEPS` | Maximum steps for autonomous tasks | `100` |
| `AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS` | Expose low-level tools to main Agent | `false` |
| `AUTOGLM_VERBOSE` | Enable verbose logging | `false` |

**AutoGLM Vision Model Configuration** (Required when `AUTOGLM_ENABLED=true`):

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `AUTOGLM_VISION_MODEL_URL` | Vision model API base URL | Local: `http://localhost:8000/v1`<br/>Zhipu AI: `https://open.bigmodel.cn/api/paas/v4` |
| `AUTOGLM_VISION_MODEL_NAME` | Vision model name | Local: `autoglm-phone-9b`<br/>Zhipu AI: `autoglm-phone` |
| `AUTOGLM_VISION_API_KEY` | Vision model API key | Local: `EMPTY`<br/>Zhipu AI: API key |

**AutoGLM Android Device Configuration** (Optional when `AUTOGLM_PLATFORM=android`):

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `AUTOGLM_DEVICE_ID` | ADB device ID (leave empty to auto-use first connected device) | USB: `ABCD1234567890`<br/>WiFi: `192.168.1.100:5555`<br/>Emulator: `emulator-5554` |

**AutoGLM iOS Device Configuration** (When `AUTOGLM_PLATFORM=ios`):

| Environment Variable | Description | Example Values |
|---------------------|-------------|----------------|
| `AUTOGLM_WDA_URL` | WebDriverAgent URL | `http://localhost:8100` |
| `AUTOGLM_IOS_DEVICE_ID` | iOS device UDID (leave empty to auto-use first connected device) | `00008030-001234567890001E` |

### AutoGLM Installation (Optional - Android/iOS Automation)

If you need Android or iOS device automation features, install AutoGLM support.

> **Note**: AutoGLM is an optional feature. Not installing it won't affect other deepagents-cli functionalities. Set AUTOGLM_ENABLED to false.

**Quick Start:**

1. **Install dependencies**
   ```bash
   pip install -e ".[autoglm]"
   # or using uv
   uv pip install -e ".[autoglm]"
   ```

2. **Android Device Configuration**
   - Install ADB tools: `brew install android-platform-tools` (macOS)
   - Enable USB debugging: Settings → Developer options → USB debugging
   - Install ADB Keyboard: for text input
   - Configure vision model: local deployment or cloud service

   📚 Detailed steps: [Android Device Configuration](docs/autoglm_setup_en.md#android-device-setup)

3. **iOS Device Configuration**
   - Install Xcode and configure developer account
   - Configure WebDriverAgent: iOS automation core component
   - Enable UI Automation: Settings → Developer → UI Automation
   - Configure vision model: local deployment or cloud service

   📱 Detailed steps: [iOS Device Configuration](docs/autoglm_setup_en.md#ios-device-setup)

**Complete Configuration Guide:** 📚 [AutoGLM Setup Guide](docs/autoglm_setup_en.md)

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

> [!WARNING]
> **Human-in-the-Loop (HITL) Requirements**
>
> Potentially destructive operations require user approval before execution:
>
> - **File operations**: `write_file`, `edit_file`
> - **Command execution**: `shell`, `execute`
> - **External requests**: `web_search`, `fetch_url`
> - **Delegation**: `task` (sub-agents)
> - **Phone operations**: `phone_task`, `phone_tap`, `phone_swipe`, etc.
>
> Each operation will display details and prompt for approval. Use `--auto-approve` to skip prompts:
>
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
- **xiaohongshu-posting** - Xiaohongshu automated posting workflow, supports both regular notes and long articles

To use example skills globally in the default Agent, simply copy them to your Agent's global or project-level skills directory:

```bash
# Create skills directory
mkdir -p ~/.deepagents/agent/skills

# Copy single skill
cp -r examples/skills/web-research ~/.deepagents/agent/skills/

# Or copy all example skills at once
cp -r examples/skills/* ~/.deepagents/agent/skills/
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

## Roadmap

### ✅ Completed Features

- ✅ AutoGLM middleware integration (vision-guided phone control)
- ✅ Xiaohongshu auto-posting skill
- ✅ Two-level interrupt mechanism (Ctrl+C graceful exit)
- ✅ Long text input support
- ✅ Improved AutoGLM interrupt handling mechanism
- ✅ iOS device support
- ✅ Android sensitive screen detection and manual intervention (password input, payment confirmation, etc.)

### 🚧 In Progress / 📋 Planned

- 🚧 `phone_task` may need to return more specific ToolMessage when interrupted, optimization under consideration
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
2. Use `deepagents skills create <skill-name>` to create skill framework
3. Write `SKILL.md` (including YAML metadata and usage instructions)
4. Submit Pull Request to `examples/skills/` directory

## Acknowledgments

This project is built upon the following open-source projects:

- [deepagents](https://github.com/langchain-ai/deepagents) - Powerful Agent framework provided by LangChain
- [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) - Vision-guided phone automation capabilities provided by Zhipu AI

Thanks to the contributors of these projects for their hard work and open-source spirit!
