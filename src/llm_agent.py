import os
import json
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 引入全局日志对象
from src.logger import logger

# 加载环境变量
load_dotenv()

def summarize_issue(issue_title: str, issue_body: str) -> str:
    """
    调用大模型 API，对 GitHub Issue 进行一句话总结。
    """
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    # 如果你在 .env 中配置了模型名称也可以读取，这里默认写死一个通用的作为示例
    model_name = os.getenv("LLM_MODEL_NAME", "qwen-plus") 

    if not api_key or not base_url:
        logger.error("调试错误：未找到 LLM_API_KEY 或 LLM_BASE_URL，请检查 .env 文件。")
        return "无法生成摘要：LLM 配置缺失。"

    # 构造 Prompt
    system_prompt = "你是一个资深的开源项目维护者。请根据提供的 GitHub Issue 标题和描述，用一句简练、专业的话总结这个 Issue 的核心诉求或问题。不要任何废话，直接输出结果。"
    user_prompt = f"【标题】: {issue_title}\n【描述】: {issue_body[:500]}" 

    # 兼容 OpenAI 格式的请求 Payload
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3, 
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # ================= 核心重试逻辑 =================
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10), 
        retry=retry_if_exception_type(requests.exceptions.RequestException), 
        reraise=True 
    )
    def _do_request():
        logger.info(f"🧠 正在尝试呼叫大模型 ({model_name}) 分析 Issue (带有重试机制)...")
        response = requests.post(
            url=f"{base_url}/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    try:
        result = _do_request()
        summary = result["choices"][0]["message"]["content"].strip()
        logger.info("✅ 大模型总结完成！")
        return summary
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ LLM 网络请求最终失败(已耗尽重试次数): {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"调试信息: {e.response.text}")
        return "生成摘要失败 (网络或接口异常)"

# ================= 测试入口 =================
if __name__ == "__main__":
    test_title = "HTTPDigestAuth fails on non-latin credentials"
    test_body = "When passing non-latin characters to HTTPDigestAuth, it raises an encoding error because it tries to encode the string as latin-1 instead of utf-8. This breaks authentication for users with special characters in their passwords."
    
    summary = summarize_issue(test_title, test_body)
    print("\n" + "="*40)
    print(f"原始标题: {test_title}")
    print(f"大模型总结: {summary}")
    print("="*40)