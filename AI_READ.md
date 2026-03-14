# NexusMind

## 项目概述 (Project Overview)

**NexusMind** 是一个基于 **Python 与轻量级 LLM 链** 的开源项目核心动态自动化播报机器人。
**核心宗旨：** 以极低的开发和运行成本，实现“GitHub 数据获取 -> 大模型智能提炼摘要 -> 飞书 Webhook 触达”的闭环，帮助开发者和团队高效跟踪开源项目的日常更新（MVP 1.0 阶段专注 Issue 跟踪）。
**设计哲学：** 实用主义与极简架构。摒弃 LangGraph、向量数据库和全量企业机器人接入等复杂技术栈，采用无状态运行、直连 API 以及轻量级本地 JSON 去重，确保项目易于部署、维护和二次开发。

## 完整的目录结构 (Directory Structure)

当前 MVP 1.0 版本的完整文件结构如下：

```text
NexusMind/
├── .env                    # 本地环境变量配置（包含各类 API Key 与 Webhook，不提交至 Git）
├── .env.example            # 环境变量模板（用于说明需要哪些配置项）
├── .gitignore              # Git 忽略规则
├── requirements.txt        # Python 依赖清单 (requests, python-dotenv, schedule)
├── pushed_history.json     # 动态生成的轻量级本地数据库，记录已推送的 Issue ID，用于去重
└── src/                    # 核心源代码目录
    ├── github_api.py       # GitHub 数据获取层：封装 REST API 调用，处理 Issue 拉取与 PR 过滤
    ├── llm_agent.py        # 智能提炼层：调用火山引擎（豆包）兼容 OpenAI 格式的 API 进行文本总结
    ├── feishu_bot.py       # 消息触达层：封装飞书自定义机器人 Webhook，构建并推送 Markdown 交互式卡片
    └── main.py             # 调度主入口：串联上述三大模块，处理本地去重逻辑并提供定时任务入口

```

## 核心设计与实现细节 (Core Design & Implementation)

1. **A. 数据获取层 (`github_api.py`)**
* **接口规范**：使用 GitHub REST API v3 (`application/vnd.github.v3+json`)。
* **去噪逻辑**：由于 GitHub 底层视 PR 为 Issue，代码中通过显式检查数据字典中是否包含 `pull_request` 键来剔除 PR，确保只处理纯 Issue。
* **字段裁剪**：为防止撑爆 LLM 上下文窗口，仅截取 Issue Body 的前 1000 个字符。


2. **B. 智能提炼层 (`llm_agent.py`)**
* **模型接入**：目前接入火山引擎（豆包）大模型，使用 OpenAI 兼容格式 (`/chat/completions`)。
* **特殊标识**：针对火山方舟平台的特性，`LLM_MODEL_NAME` 环境变量填写的并非模型通用名称，而是专属的**接入点 ID (`ep-` 开头)**。
* **Prompt 工程**：采用极简的 System Prompt，要求以“开源项目维护者”身份用一句话总结核心诉求。设定 `temperature=0.3` 以保证输出的稳定性和客观性。


3. **C. 触达层 (`feishu_bot.py`)**
* **极简接入**：仅使用飞书群组的“自定义机器人 Webhook”，无需处理复杂的鉴权和事件回调订阅。
* **卡片渲染**：使用飞书的 `interactive` 消息类型，渲染包含宽屏模式、彩色标题栏、Markdown 正文、视觉分割线以及底部注脚的精美卡片。


4. **D. 调度与防扰机制 (`main.py`)**
* **去重逻辑**：在推送前比对 `pushed_history.json`，推送成功后将 Issue 编号追加写入文件，彻底防止重复播报。
* **流控限制**：每次推送成功后硬编码 `time.sleep(2)`，避免触发飞书 Webhook 或 LLM API 的高频流控惩罚。



## 维护指南 (Maintenance Guide)

### 环境依赖

* **Python 版本**：推荐使用 `Python 3.11` (本项目开发时使用的是 Conda 环境 `python=3.11`)。
* **依赖安装**：进入环境后执行 `pip install -r requirements.txt`。

### 环境变量配置 (`.env`)

项目运行强依赖根目录下的 `.env` 文件，必须包含以下内容：

```env
# 1. 飞书配置
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的真实webhook地址

# 2. 大模型配置 (火山引擎-豆包)
LLM_API_KEY=你的火山引擎API_KEY
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL_NAME=ep-xxxxxxxxxx-xxxx  # 必须是火山方舟的接入点 ID

# 3. GitHub 配置 (可选，不填则仅能访问公开仓库且限流 60次/小时)
# GITHUB_ACCESS_TOKEN=ghp_xxxxxx

```

### 🤝 AI 协作与代码维护规范 (致接手的 AI 助手)

在后续协助开发者维护或新增功能时，**必须**严格遵守以下原则：

1. **原子化拆分**：如果任务包含多个步骤，尽可能将其分解为足够原子化的步骤，引导用户一步步确认，保证操作安全性。
2. **完整代码交付**：每次提交代码修改时，**必须在顶部指明文件路径**，并提供**修改后的完整文件代码**，绝不可只发送代码片段。
3. **先读后写**：修改任何不熟悉或关键的功能前，必须先向用户索取该文件的当前源文件代码进行查看。
4. **调试驱动**：若需获取数据结构或排查 Bug，主动在代码中添加 `print()` 探针，并向用户索取调试终端的输出信息。

## 关键代码片段备份 (Key Code Snippets)

**大模型调用核心逻辑 (`src/llm_agent.py`)：**

```python
payload = {
    "model": model_name,  # 火山引擎的 ep- 接入点 ID
    "messages": [
        {"role": "system", "content": "你是一个资深的开源项目维护者。请根据提供的 GitHub Issue 标题和描述，用一句简练、专业的话总结这个 Issue 的核心诉求或问题。不要任何废话，直接输出结果。"},
        {"role": "user", "content": f"【标题】: {issue_title}\n【描述】: {issue_body[:500]}"}
    ],
    "temperature": 0.3,
    "max_tokens": 100
}

```

**主流程调度核心与防重逻辑 (`src/main.py`)：**

```python
pushed_history = load_pushed_history()
new_issues = [issue for issue in issues if issue["number"] not in pushed_history]

for issue in new_issues:
    summary = summarize_issue(issue["title"], issue["body"])
    # ...构造 markdown_content...
    success = send_feishu_card(title=f"📝 动态: {issue['title']}", markdown_content=markdown_content, color_theme="blue")
    
    if success:
        pushed_history.append(issue["number"])
        save_pushed_history(pushed_history)
        time.sleep(2)

```

## 尚未解决的问题 (Pending Tasks / Roadmap)

本项目目前已完成 Phase 1 (核心流打通)，未来演进需解决以下问题：

1. **Pull Request (PR) 监控支持**：目前 API 仅拉取了 Issue，需在 `github_api.py` 中新增拉取 PR 的逻辑（或修改现有逻辑以分离 Issue 和 PR），并根据 PR 的代码 Diff 生成相应的审查摘要。
2. **规则化定向过滤 (Phase 2)**：目前是全量拉取最新内容。需引入基于 GitHub Label（如 `bug`, `help wanted`）或标题正则匹配的过滤机制，进一步剔除低价值的动态。
3. **单次上下文长文本问答支持**：需要新增一个入口，允许用户直接传入单次长文本（如具体的 PR 详情/报错日志）让 LLM 提供修复建议。
4. **生产环境部署**：将基于 `schedule` 的 Python 脚本转换为 `Dockerfile`，或编写标准的 `Crontab` 部署文档，以便将其挂载到云服务器长期稳定运行。