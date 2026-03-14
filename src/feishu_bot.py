import os
import json
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 引入全局日志对象
from src.logger import logger

# 加载项目根目录的 .env 文件
load_dotenv()

def send_feishu_card(title: str, markdown_content: str, color_theme: str = "blue") -> bool:
    """
    向飞书自定义机器人发送 Markdown 卡片消息。
    :param title: 卡片标题
    :param markdown_content: Markdown 格式的正文内容
    :param color_theme: 标题栏颜色
    """
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    
    if not webhook_url:
        logger.error("调试错误：未找到 FEISHU_WEBHOOK_URL 环境变量，请检查 .env 文件。")
        return False

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True 
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
                    "tag": "hr" 
                },
                {
                    "tag": "note", 
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

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10), 
        retry=retry_if_exception_type(requests.exceptions.RequestException), 
        reraise=True 
    )
    def _do_request():
        logger.info("🔄 正在尝试向飞书发送 Markdown 卡片 (带有重试机制)...")
        response = requests.post(
            url=webhook_url, 
            headers=headers, 
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()
        return response

    try:
        response = _do_request()
        status_code = response.status_code
        response_data = response.json()
        
        if status_code == 200 and response_data.get("code") == 0:
            logger.info("✅ Markdown 卡片发送成功！快去飞书群看看排版效果吧。")
            return True
        else:
            logger.error("❌ 卡片发送业务逻辑失败！这类错误通常是配置或格式问题，不会进行重试。")
            logger.error(f"调试信息 -> 飞书返回信息: {response_data}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error("❌ 飞书网络请求最终失败(已耗尽重试次数)！")
        logger.error(f"调试信息 -> 异常详情: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"调试信息 -> 响应体: {e.response.text}")
        return False

# ================= 测试入口 =================
if __name__ == "__main__":
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
    
    send_feishu_card(title=test_title, markdown_content=test_markdown, color_theme="wathet")