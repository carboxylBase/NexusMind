import os
import json
import time
import schedule
from github_api import fetch_latest_issues
from llm_agent import summarize_issue
from feishu_bot import send_feishu_card

# 本地轻量级数据库（JSON文件），用于记录已经推送过的 Issue 编号
HISTORY_FILE = "pushed_history.json"

def load_pushed_history():
    """读取已推送的记录"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_pushed_history(history):
    """保存推送记录到本地"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def run_pipeline():
    """NexusMind 核心调度流水线"""
    print("\n🚀 [NexusMind] 开始执行监控任务...")
    
    # 1. 配置你想监控的仓库 (这里依然用 requests 测试)
    repo_name = "psf/requests"
    
    # 2. 拉取最新 Issue
    issues = fetch_latest_issues(repo_name, limit=3)
    if not issues:
        print("📭 当前没有拉取到 Issue 或请求失败。")
        return

    # 3. 加载历史推送记录，进行去重过滤
    pushed_history = load_pushed_history()
    new_issues = [issue for issue in issues if issue["number"] not in pushed_history]
    
    if not new_issues:
        print("💤 所有拉取到的 Issue 都已经推送过了，无需重复打扰。")
        return
        
    print(f"🔍 发现 {len(new_issues)} 个新的 Issue，准备进行 LLM 分析与推送...\n")

    # 4. 遍历处理新 Issue
    for issue in new_issues:
        # 调用豆包大模型生成摘要
        summary = summarize_issue(issue["title"], issue["body"])
        
        # 构造 Markdown 飞书卡片内容
        labels_str = ", ".join(issue["labels"]) if issue["labels"] else "无标签"
        markdown_content = (
            f"**📦 项目**: [{repo_name}](https://github.com/{repo_name})\n"
            f"**🏷️ 标签**: {labels_str}\n"
            f"**🔗 链接**: [点击查看 Issue #{issue['number']}]({issue['html_url']})\n\n"
            f"---\n"
            f"> 🤖 **AI 核心摘要**：\n"
            f"> {summary}"
        )
        
        # 推送精美的飞书卡片
        success = send_feishu_card(
            title=f"📝 动态: {issue['title']}", 
            markdown_content=markdown_content, 
            color_theme="blue"
        )
        
        # 如果推送成功，记录到本地 JSON 防止下次重复推送
        if success:
            pushed_history.append(issue["number"])
            save_pushed_history(pushed_history)
            # 稍微休眠一下，防止触发飞书或大模型 API 的频率限制
            time.sleep(2) 

    print("\n✅ [NexusMind] 本轮监控任务执行完毕！")

# ================= 调度入口 =================
if __name__ == "__main__":
    # 第一次运行：立刻执行一次流水线测试
    run_pipeline()
    
    # --- 以下是定时任务代码，目前注释掉了 ---
    # 如果你想让它挂在后台每天早上 9 点自动跑，可以取消下面三行的注释：
    # schedule.every().day.at("09:00").do(run_pipeline)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)