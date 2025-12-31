# 🚀🧠 DeepAgents-AutoGLM

[English](./README_EN.md) | 中文

基于 [deepagents](https://github.com/langchain-ai/deepagents) 框架集成 [AutoGLM](https://github.com/zai-org/Open-AutoGLM) 手机控制能力的开源智能助手，可在终端中运行，并支持 Android 和 iOS 设备自动化控制。

## 💡 项目亮点

相比原始 [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 项目，本项目基于 deepagents 框架，通过**中间件机制**集成 AutoGLM，实现以下核心优势：

- **🔗 能力组合**：AutoGLM 与 Web 搜索、Shell、技能系统、记忆系统无缝协同，实现"搜索信息 → 分析决策 → 手机操作"全流程自动化
- **🧠 智能分工**：主 Agent 负责任务规划和复杂决策，子Agent `phone_task` 专注手机操作执行，职责边界清晰
- **🎯 精细化操作**：利用 Anthropic 提出的 [Agent SKILL](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)，可为特定应用（如小红书、QQ）定制精细化的操作流程，实现复杂场景的自动化任务
- **🔌 模块化扩展**：可插拔设计，AutoGLM 作为可选中间件，通过环境变量按需启用

**典型场景示例**：

```bash
$ deepagents
> 搜索最新的 AI 新闻，总结成小红书风格的文案，然后在小红书上发布

# 执行流程：
# 1. web_search 搜索 AI 新闻
# 2. LLM 分析并生成小红书文案
# 3. 主Agent通过xiaohongshu-post skill 规划发布流程
# 4. 调用子Agent phone_task 执行手机操作（打开应用、输入、发布）
# 5. agent.md 记录发布历史
```

**核心特性：**

- **内置工具集**: 文件操作（读、写、编辑、搜索）、Shell 命令、网络搜索、子代理委托
- **可定制技能**: 通过渐进式披露技能系统添加特定领域能力
- **持久化记忆**: Agent 会记住您的偏好、编码风格和项目上下文
- **项目感知**: 自动检测项目根目录并加载项目特定配置
- **Android/iOS 自动化**（可选）: 集成 AutoGLM 实现智能手机控制（点击、滑动、输入等）
- **视觉引导控制**（可选）: 使用视觉-语言模型理解和操作手机 GUI

<img src="./DA-AutoGLM.png" alt="deep agent" width="100%"/>

## 📺 实际演示

查看 DeepAgents-AutoGLM 在真实场景中的实际应用效果：

- 🎨 **[小红书自动发布演示](http://xhslink.com/o/FdRsaQQpUz)** - 展示如何使用 Agent 自动搜索内容、生成文案并发布到小红书
- 💬 **[QQ 未读消息自动回复演示](http://xhslink.com/o/6v5umdBoznW)** - 展示如何智能识别并自动回复 QQ 未读消息

## 🚀 快速开始

### 基础安装

克隆本项目并安装依赖。

**使用 pip 安装：**

```bash
# 克隆仓库
git clone git@github.com:Illuminated2020/DeepAgents-AutoGLM.git
cd DeepAgents-AutoGLM

# 安装基础依赖
pip install -e .
```

**或使用 uv（推荐）：**

```bash
# 克隆仓库
git clone git@github.com:Illuminated2020/DeepAgents-AutoGLM.git
cd DeepAgents-AutoGLM

# 创建虚拟环境并安装
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
uv pip install -e .
```

**在终端中运行 Agent：**

```bash
deepagents
```

**获取帮助：**

```bash
deepagents help
```

**常用选项：**

```bash
# 使用特定的 Agent 配置
deepagents --agent mybot

# 创建新的 Agent
deepagents create mybot

# 列出所有 Agent
deepagents list

# 自动批准工具使用（跳过人工确认提示）
deepagents --auto-approve

# 在远程沙箱中执行代码（需要配置）
deepagents --sandbox modal        # 或 runloop, daytona
deepagents --sandbox-id dbx_123   # 重用现有沙箱

# 管理技能
deepagents skills list            # 列出所有技能
deepagents skills create my-skill # 创建新技能
```

像在聊天界面中一样自然输入。Agent 将使用其内置工具、技能和记忆来帮助您完成任务。

### 环境变量配置

在项目根目录创建 `.env` 文件来配置环境变量。您可以复制 `.env.example` 作为起点：

```bash
cp .env.example .env
```

然后根据需要编辑 `.env` 文件。以下是各环境变量的说明：

#### 必需配置

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥（或兼容的 API 密钥，支持 OpenAI、DeepSeek、通义千问等） | `sk-xxxx` |
| `OPENAI_MODEL` | 使用的模型名称 | `gpt-4`、`gpt-3.5-turbo`、`deepseek-chat`、`qwen-turbo` |

#### 可选配置

**API 配置：**

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `OPENAI_BASE_URL` | API 基础 URL（使用 OpenAI 官方服务时可不设置；使用其他兼容服务时必须设置） | `https://api.deepseek.com/v1` |

**LangSmith 追踪（可选）：**

用于监控和调试 Agent 行为。在 [https://smith.langchain.com/](https://smith.langchain.com/) 获取 API 密钥。

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `LANGSMITH_TRACING` | 是否启用 LangSmith 追踪 | `true` / `false` |
| `LANGSMITH_ENDPOINT` | LangSmith API 端点 | `https://api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | LangSmith API 密钥 | `ls_xxxx` |
| `LANGSMITH_PROJECT` | LangSmith 项目名称 | `deepagents-project` |

**Tavily 网络搜索（可选）：**

提供网络搜索能力。在 [https://tavily.com/](https://tavily.com/) 获取 API 密钥。

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `TAVILY_API_KEY` | Tavily API 密钥 | `tvly-xxxx` |

**AutoGLM 配置（可选）：**

如果不需要使用 Android/iOS 自动化功能，设置 `AUTOGLM_ENABLED=false` 即可。详细配置请参考下方的 [AutoGLM 安装](#autoglm-安装可选---androidios-自动化) 章节。

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `AUTOGLM_ENABLED` | 是否启用 AutoGLM 功能 | `false` |
| `AUTOGLM_PLATFORM` | 控制的平台：`android` 或 `ios` | `android` |
| `AUTOGLM_LANG` | 系统提示词语言：`zh` 或 `en` | `zh` |
| `AUTOGLM_MAX_STEPS` | 自主任务的最大步骤数 | `100` |
| `AUTOGLM_EXPOSE_LOW_LEVEL_TOOLS` | 是否向主 Agent 暴露底层工具 | `false` |
| `AUTOGLM_VERBOSE` | 是否启用详细日志 | `false` |

**AutoGLM 视觉模型配置**（当 `AUTOGLM_ENABLED=true` 时必需）：

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `AUTOGLM_VISION_MODEL_URL` | 视觉模型 API 基础 URL | 本地：`http://localhost:8000/v1`<br/>智谱 AI：`https://open.bigmodel.cn/api/paas/v4` |
| `AUTOGLM_VISION_MODEL_NAME` | 视觉模型名称 | 本地：`autoglm-phone-9b`<br/>智谱 AI：`autoglm-phone` |
| `AUTOGLM_VISION_API_KEY` | 视觉模型 API 密钥 | 本地：`EMPTY`<br/>智谱 AI：API 密钥 |

**AutoGLM Android 设备配置**（当 `AUTOGLM_PLATFORM=android` 时可选）：

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `AUTOGLM_DEVICE_ID` | ADB 设备 ID（留空则自动使用第一个连接的设备） | USB：`ABCD1234567890`<br/>WiFi：`192.168.1.100:5555`<br/>模拟器：`emulator-5554` |

**AutoGLM iOS 设备配置**（当 `AUTOGLM_PLATFORM=ios` 时）：

| 环境变量 | 说明 | 示例值 |
|---------|------|--------|
| `AUTOGLM_WDA_URL` | WebDriverAgent URL | `http://localhost:8100` |
| `AUTOGLM_IOS_DEVICE_ID` | iOS 设备 UDID（留空则自动使用第一个连接的设备） | `00008030-001234567890001E` |

### AutoGLM 安装（可选 - Android/iOS 自动化）

如果需要使用 Android 或 iOS 设备自动化功能，请安装 AutoGLM 支持。

> **注意**: AutoGLM 是可选功能，不安装也不影响 deepagents-cli 的其他功能使用。需要将AUTOGLM_ENABLED设置为false。

**快速开始：**

1. **安装依赖**
   ```bash
   pip install -e ".[autoglm]"
   # 或使用 uv
   uv pip install -e ".[autoglm]"
   ```

2. **Android 设备配置**
   - 安装 ADB 工具：`brew install android-platform-tools`（macOS）
   - 启用 USB 调试：设置 → 开发者选项 → USB 调试
   - 安装 ADB Keyboard：用于文本输入
   - 配置视觉模型：本地部署或云端服务

   📚 详细步骤：[Android 设备配置](docs/autoglm_setup.md#android-设备配置)

3. **iOS 设备配置**
   - 安装 Xcode 和配置开发者账号
   - 配置 WebDriverAgent：iOS 自动化核心组件
   - 启用 UI 自动化：设置 → 开发者 → UI 自动化
   - 配置视觉模型：本地部署或云端服务

   📱 详细步骤：[iOS 设备配置](docs/autoglm_setup.md#ios-设备配置)

**完整配置指南：** 📚 [AutoGLM 配置详解](docs/autoglm_setup.md)

## 内置工具

Agent 自带以下内置工具（无需配置即可使用）：

### 基础工具

| 工具            | 描述                                   |
| --------------- | -------------------------------------- |
| `ls`          | 列出文件和目录                         |
| `read_file`   | 读取文件内容                           |
| `write_file`  | 创建或覆写文件                         |
| `edit_file`   | 对现有文件进行针对性编辑               |
| `glob`        | 查找匹配模式的文件（例如 `**/*.py`） |
| `grep`        | 跨文件搜索文本模式                     |
| `shell`       | 执行 Shell 命令（本地模式）            |
| `execute`     | 在远程沙箱中执行命令（沙箱模式）       |
| `web_search`  | 使用 Tavily API 搜索网络               |
| `fetch_url`   | 获取网页并转换为 Markdown              |
| `task`        | 将工作委托给子代理进行并行执行         |
| `write_todos` | 为复杂工作创建和管理任务列表           |

### AutoGLM 工具（需要启用 `AUTOGLM_ENABLED=true`）

| 工具                 | 描述                                                    |
| -------------------- | ------------------------------------------------------- |
| `phone_task`       | 🎯**高级任务工具** - 执行自然语言手机任务（推荐） |
| `phone_tap`        | 在指定坐标点击                                          |
| `phone_swipe`      | 执行滑动手势                                            |
| `phone_type`       | 输入文本                                                |
| `phone_screenshot` | 截取屏幕                                                |
| `phone_back`       | 按返回键                                                |
| `phone_home`       | 按主屏幕键                                              |
| `phone_launch`     | 按名称启动应用                                          |

> [!WARNING]
> **人工确认（HITL）要求**
>
> 潜在破坏性操作在执行前需要用户批准：
>
> - **文件操作**: `write_file`、`edit_file`
> - **命令执行**: `shell`、`execute`
> - **外部请求**: `web_search`、`fetch_url`
> - **委托**: `task`（子代理）
> - **手机操作**: `phone_task`、`phone_tap`、`phone_swipe` 等
>
> 每个操作都会显示操作详情并提示批准。使用 `--auto-approve` 跳过提示：
>
> ```bash
> deepagents --auto-approve
> ```

## Agent 配置

每个 Agent 都有自己的配置目录 `~/.deepagents/<agent_name>/`，默认为 `agent`。

```bash
# 列出所有配置的 Agent
deepagents list

# 创建新的 Agent
deepagents create <agent_name>
```

## 自定义

自定义 Agent 有两种主要方式：**记忆（memory）** 和 **技能（skills）**。

每个 Agent 都有自己的全局配置目录 `~/.deepagents/<agent_name>/`：

```
~/.deepagents/<agent_name>/
  ├── agent.md              # 自动加载的全局个性/风格
  └── skills/               # 自动加载的 Agent 特定技能
      ├── web-research/
      │   └── SKILL.md
      └── langgraph-docs/
          └── SKILL.md
```

项目可以通过项目特定的指令和技能扩展全局配置：

```
my-project/
  ├── .git/
  └── .deepagents/
      ├── agent.md          # 项目特定指令
      ├── .env              # 项目特定环境配置（AutoGLM 等）
      └── skills/           # 项目特定技能
          └── custom-tool/
              └── SKILL.md
```

CLI 会自动检测项目根目录（通过 `.git`）并加载：

- 项目特定的 `agent.md`（来自 `[项目根]/.deepagents/agent.md`）
- 项目特定的技能（来自 `[项目根]/.deepagents/skills/`）
- 项目特定的环境配置（来自 `[项目根]/.deepagents/.env`）

全局和项目配置会一起加载，允许您：

- 在全局 agent.md 中保持通用编码风格/偏好
- 在项目 agent.md 中添加项目特定的上下文、约定或指南
- 通过版本控制与团队共享项目特定技能
- 用项目特定版本覆盖全局技能（当技能名称匹配时）
- 为不同项目配置不同的 AutoGLM 设置

### agent.md 文件

`agent.md` 文件提供持久化记忆，在每次会话开始时自动加载。全局和项目级别的 `agent.md` 文件会一起加载并注入到系统提示中。

**全局 `agent.md`**（`~/.deepagents/agent/agent.md`）

- 您的个性、风格和通用编码偏好
- 一般语气和沟通风格
- 通用编码偏好（格式化、类型提示等）
- 适用于所有场景的工具使用模式
- 不随项目变化的工作流和方法论

**项目 `agent.md`**（项目根目录中的 `.deepagents/agent.md`）

- 项目特定的上下文和约定
- 项目架构和设计模式
- 此代码库特定的编码约定
- 测试策略和部署流程
- 团队指南和项目结构

**工作原理（AgentMemoryMiddleware）：**

- 在启动时加载两个文件，并作为 `<user_memory>` 和 `<project_memory>` 注入系统提示
- 附加[记忆管理指令](deepagents_cli/agent_memory.py#L44-L158)，说明何时/如何更新记忆文件

**Agent 何时更新记忆：**

- 当您描述它应该如何行为时 **立即** 更新
- 当您对其工作给出反馈时 **立即** 更新
- 当您明确要求它记住某事时
- 当从交互中出现模式或偏好时

Agent 使用 `edit_file` 在学习偏好或收到反馈时更新记忆。

### 项目记忆文件

除了 `agent.md`，您还可以在 `.deepagents/` 中创建额外的记忆文件用于结构化项目知识。这些工作方式类似于 [Anthropic 的记忆工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)。Agent 会收到[详细指令](deepagents_cli/agent_memory.py#L123-L158)，说明何时读取和更新这些文件。

**工作原理：**

1. 在 `[项目根]/.deepagents/` 中创建 Markdown 文件（例如 `api-design.md`、`architecture.md`、`deployment.md`）
2. Agent 在任务相关时检查这些文件（不会自动加载到每个提示中）
3. Agent 在学习项目模式时使用 `write_file` 或 `edit_file` 创建/更新记忆文件

**示例工作流：**

```bash
# Agent 发现部署模式并保存
.deepagents/
├── agent.md           # 始终加载（个性 + 约定）
├── architecture.md    # 按需加载（系统设计）
├── deployment.md      # 按需加载（部署流程）
└── .env              # AutoGLM 和其他环境配置
```

**Agent 何时读取记忆文件：**

- 在新会话开始时（检查存在哪些文件）
- 在回答项目特定主题的问题之前
- 当您引用过去的工作或模式时
- 在执行与已保存知识领域匹配的任务时

**优势：**

- **持久化学习**：Agent 跨会话记住项目模式
- **团队协作**：通过版本控制共享项目知识
- **上下文检索**：仅在需要时加载相关记忆（减少 token 使用）
- **结构化知识**：按领域组织信息（API、架构、部署等）

### 技能（Skills）

技能是可重用的 Agent 能力，提供专业化的工作流和领域知识。`examples/skills/` 目录中提供了示例技能：

- **web-research** - 结构化网络研究工作流，包括规划、并行委托和综合
- **langgraph-docs** - LangGraph 文档查找和指导
- **xiaohongshu-posting** - 小红书自动发帖工作流，支持普通笔记和长文笔记发布

要在默认 Agent 中全局使用示例技能，只需将它们复制到 Agent 的全局或项目级技能目录：

```bash
# 创建技能目录
mkdir -p ~/.deepagents/agent/skills

# 复制单个技能
cp -r examples/skills/web-research ~/.deepagents/agent/skills/

# 或者一次性复制所有示例技能
cp -r examples/skills/* ~/.deepagents/agent/skills/
```

管理技能：

```bash
# 列出所有技能（全局 + 项目）
deepagents skills list

# 仅列出项目技能
deepagents skills list --project

# 从模板创建新的全局技能
deepagents skills create my-skill

# 创建新的项目技能
deepagents skills create my-tool --project

# 查看技能的详细信息
deepagents skills info web-research

# 仅查看项目技能的信息
deepagents skills info my-tool --project
```

使用技能（例如 langgraph-docs 技能），只需输入与技能相关的请求，技能就会自动使用。

```bash
$ deepagents 
$ "创建一个实现 LangGraph Agent 的 agent.py 脚本" 
```

技能遵循 Anthropic 的[渐进式披露模式](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Agent 知道技能存在，但仅在需要时读取完整指令。

1. **启动时** - SkillsMiddleware 扫描 `~/.deepagents/agent/skills/` 和 `.deepagents/skills/` 目录
2. **解析元数据** - 从每个 `SKILL.md` 文件中提取 YAML frontmatter（名称 + 描述）
3. **注入提示** - 将技能列表及描述添加到系统提示："可用技能：web-research - 用于网络研究任务..."
4. **渐进式加载** - Agent 仅在任务与技能描述匹配时使用 `read_file` 读取完整的 `SKILL.md` 内容
5. **执行工作流** - Agent 遵循技能文件中的逐步指令

## 路线图

### ✅ 已完成功能

- ✅ AutoGLM 中间件集成（视觉引导手机控制）
- ✅ 小红书自动发帖技能
- ✅ 双层中断机制（Ctrl+C 优雅退出）
- ✅ 长文本输入支持
- ✅ 改进 AutoGLM 中的中断处理机制
- ✅ iOS 设备支持
- ✅ Android 敏感屏幕自动检测与人工接管（密码输入、支付确认等）

### 🚧 开发中 / 📋 计划中

- 🚧 `phone_task`被中途中断时可能需要返回更具体的ToolMessage，考虑优化方案中
- 📋 更多手机操作技能（**欢迎贡献！**）

## 贡献指南

**欢迎贡献手机操作相关的技能（Skills）！**

### 技能贡献方向

电商购物、社交媒体、生活服务、内容创作等方向的自动化技能。

### 如何贡献

**推荐利用 `skill-creator` 技能来创建新技能：**

```bash
# 1. 将 skill-creator 复制到你的技能目录
cp -r examples/skills/skill-creator ~/.deepagents/agent/skills/

# 2. 让 Agent 帮你创建技能
deepagents
> 帮我创建一个 [描述你的技能] 的技能
# Agent 会利用 skill-creator 引导你完成创建过程
```

**或手动创建：**

1. 参考 `examples/skills/xiaohongshu-posting/SKILL.md` 了解技能格式
2. 使用 `deepagents skills create <skill-name>` 创建技能框架
3. 编写 `SKILL.md`（包含 YAML 元数据和使用说明）
4. 提交 Pull Request 到 `examples/skills/` 目录

## 致谢

本项目基于以下开源项目构建：

- [deepagents](https://github.com/langchain-ai/deepagents) - 由 LangChain 提供的强大 Agent 框架
- [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) - 由智谱 AI 提供的视觉引导手机自动化能力

感谢这些项目的贡献者们的辛勤工作和开源精神！
