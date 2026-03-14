## 🚀 项目名称：NexusMind

**定位：** 基于 **Python 与轻量级 LLM 链** 的 GitHub 核心动态自动化播报机器人。
**核心理念：** 快速跑通“数据获取-大模型提炼-飞书触达”的 MVP（最小可行性产品），以极低的开发成本实现开源项目的日常跟踪。

---

### 1. 核心功能场景 (Use Cases)

* **项目摘要生成：** 输入 GitHub URL，调用 API 获取 README 和最近的 Commits，利用大模型生成一句话总结和核心功能列表。
* **规则化定向监控：** 每天定时拉取指定仓库的 Issue/PR 更新，通过预设的**关键词与标签规则**（如 Label 为 "bug", "help wanted" 或正则匹配特定字符）进行基础过滤，再交由大模型生成简报推送到飞书。
* **单次上下文问答：** 基于单次输入的长文本（如某个具体的 PR 详情或报错日志），调用 LLM 解释代码变更或提供修复建议，不做跨文件的深度关联推理。

---

### 2. 演进后的技术架构 (MVP 1.0)

#### **A. 调度核心 (Lightweight Controller)**

* **直连 API (Direct API Calls)：** 放弃复杂的 LangGraph，直接使用 Python 的 `requests` 库或基础的 `LangChain` 顺序链（Sequential Chain）调用豆包或通义千问 API。
* **定时任务 (Cron Jobs)：** 使用基础的定时任务脚本（如 Python 的 `schedule` 库或操作系统的 Crontab）触发监控流，无需维护复杂的状态机。

#### **B. 智能连接层 (Connectivity)**

* **飞书 Webhook 推送：** 不做全量企业机器人接入和事件订阅，仅通过飞书群组的 **自定义机器人 Webhook** 接口单向推送消息，开发成本极低。
* **标准 Markdown 卡片：** 使用飞书支持的基础 Markdown 格式展示项目动态、代码 Diff 链接和 LLM 分析总结，剔除复杂的交互式回调按钮。

#### **C. 记忆与检索 (Stateless / Basic Context)**

* **无状态运行 (Stateless)：** 每次分析作为一个独立的任务运行，降低内存和处理开销。
* **L1 (轻量级状态记录)：** 放弃向量库（Vector DB）和图数据库。仅使用本地 JSON 文件或轻量级的 SQLite 数据库记录“已推送过的 Issue/PR ID”，防止重复打扰。

---

### 3. 开发路线图 (Roadmap) - 极速落地版

| 阶段 | 关键里程碑 | 核心突破 |
| --- | --- | --- |
| **Phase 1** | **核心流打通** | 使用 Python 脚本跑通 `GitHub API 拉取 -> LLM 总结 -> 飞书 Webhook 推送` 链路。 |
| **Phase 2** | **规则过滤器** | 引入基础的正则匹配和 GitHub Label 过滤逻辑，初步剔除无关信息。 |
| **Phase 3** | **Prompt 调优** | 针对豆包/千问等国产大模型进行 Prompt 工程优化，确保输出的 Markdown 格式稳定且排版美观。 |
