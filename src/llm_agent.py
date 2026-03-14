import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def summarize_issue(issue_title: str, issue_body: str) -> str:
    """
    调用大模型 API，对 GitHub Issue 进行一句话总结。
    """
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    # 如果你在 .env 中配置了模型名称也可以读取，这里默认写死一个通用的作为示例
    model_name = os.getenv("LLM_MODEL_NAME", "qwen-plus") # 以通义千问为例，如果是豆包可能是 ep-xxx

    if not api_key or not base_url:
        print("❌ 调试错误：未找到 LLM_API_KEY 或 LLM_BASE_URL，请检查 .env 文件。")
        return "无法生成摘要：LLM 配置缺失。"

    # 构造 Prompt（提示词工程初体验）
    system_prompt = "你是一个资深的开源项目维护者。请根据提供的 GitHub Issue 标题和描述，用一句简练、专业的话总结这个 Issue 的核心诉求或问题。不要任何废话，直接输出结果。"
    user_prompt = f"【标题】: {issue_title}\n【描述】: {issue_body[:500]}" # 截断描述，节省 token

    # 兼容 OpenAI 格式的请求 Payload
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3, # 较低的温度，保证输出的确定性和精简
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🧠 正在呼叫大模型 ({model_name}) 分析 Issue...")
        response = requests.post(
            url=f"{base_url}/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            print("✅ 大模型总结完成！")
            return summary
        else:
            print(f"❌ LLM 请求失败！状态码: {response.status_code}")
            print(f"调试信息: {response.text}")
            return f"生成摘要失败 (HTTP {response.status_code})"
            
    except requests.exceptions.RequestException as e:
        print(f"❌ LLM 网络请求异常: {e}")
        return "生成摘要失败 (网络异常)"

# ================= 测试入口 =================
if __name__ == "__main__":
    # 使用刚才我们拉取到的 requests 库的真实数据作为测试
    test_title = "HTTPDigestAuth fails on non-latin credentials"
    test_body = "When passing non-latin characters to HTTPDigestAuth, it raises an encoding error because it tries to encode the string as latin-1 instead of utf-8. This breaks authentication for users with special characters in their passwords."
    
    summary = summarize_issue(test_title, test_body)
    print("\n" + "="*40)
    print(f"原始标题: {test_title}")
    print(f"大模型总结: {summary}")
    print("="*40)