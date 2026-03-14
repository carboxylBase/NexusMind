import os
import json
import requests
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv()

def send_feishu_card(title: str, markdown_content: str, color_theme: str = "blue"):
    """
    向飞书自定义机器人发送 Markdown 卡片消息。
    :param title: 卡片标题
    :param markdown_content: Markdown 格式的正文内容
    :param color_theme: 标题栏颜色，可选 blue, wathet, red, green, yellow, orange, purple 等
    """
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ 调试错误：未找到 FEISHU_WEBHOOK_URL 环境变量，请检查 .env 文件。")
        return False

    # 飞书卡片 (interactive) 的标准 Payload 格式
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True # 开启宽屏展示，排版更美观
            },
            "header": {
                "template": color_theme, 
                "title": {
                    "content": title,
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": markdown_content
                },
                {
                    "tag": "hr" # 添加一条原生的视觉分割线
                },
                {
                    "tag": "note", # 卡片底部的注脚
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "🤖 由 NexusMind 自动化引擎生成"
                        }
                    ]
                }
            ]
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"🔄 正在尝试向飞书发送 Markdown 卡片...")
        response = requests.post(
            url=webhook_url, 
            headers=headers, 
            data=json.dumps(payload),
            timeout=10
        )
        
        status_code = response.status_code
        response_data = response.json()
        
        if status_code == 200 and response_data.get("code") == 0:
            print("✅ Markdown 卡片发送成功！快去飞书群看看排版效果吧。")
            return True
        else:
            print(f"❌ 卡片发送失败！")
            print(f"调试信息 -> 状态码: {status_code}")
            print(f"调试信息 -> 飞书返回信息: {response_data}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求发生异常！")
        print(f"调试信息 -> 异常详情: {e}")
        return False

# ================= 测试入口 =================
if __name__ == "__main__":
    # 测试数据：构造一个模拟的 GitHub 项目动态摘要
    test_title = "📦 NexusMind 架构升级通告"
    test_markdown = (
        "**今日 GitHub 核心动态摘要：**\n"
        "这是我们使用 `Markdown` 格式发送的卡片消息。\n\n"
        "🌟 **亮点功能支持：**\n"
        "- 支持文本加粗与 *斜体*\n"
        "- 支持 [超链接点击](https://github.com)\n"
        "- 支持原生代码块展示：\n"
        "```python\n"
        "def hello_nexus_mind():\n"
        "    print('Markdown is awesome!')\n"
        "```\n"
        "> 💡 **LLM 总结**：这是一个引用块，未来这里会用来展示大模型自动提炼的 PR 摘要或 Issue 的一句话解释，让阅读体验更具层次感。"
    )
    
    # 颜色使用 wathet (浅蓝色)，你可以尝试改成 red 或 green 看看效果
    send_feishu_card(title=test_title, markdown_content=test_markdown, color_theme="wathet")