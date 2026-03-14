import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def fetch_latest_issues(repo_name: str, limit: int = 5):
    """
    拉取指定 GitHub 仓库的最新 Open 状态的 Issues。
    
    :param repo_name: 仓库名称，格式为 "owner/repo"，例如 "tiangolo/fastapi"
    :param limit: 获取的数量限制
    :return: 包含 Issue 核心信息的字典列表
    """
    # GitHub 官方推荐的 API v3 请求头
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取 GitHub Token（可选：如果有 Token，可以突破每小时 60 次的限制，提升到 5000 次）
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    # 构造请求参数，按更新时间倒序排列，只看 open 状态的
    url = f"https://api.github.com/repos/{repo_name}/issues"
    params = {
        "state": "open",
        "sort": "updated",
        "direction": "desc",
        "per_page": limit * 2  # 多拉取一些，因为后面要过滤掉 PR
    }

    try:
        print(f"🔄 正在拉取仓库 {repo_name} 的最新 Issues...")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ 请求失败！状态码: {response.status_code}")
            print(f"调试信息: {response.json()}")
            return []

        raw_issues = response.json()
        processed_issues = []

        for item in raw_issues:
            # 核心过滤逻辑：剔除 Pull Requests，只保留纯 Issue
            if "pull_request" not in item:
                # 提取有价值的特征字段
                issue_data = {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "html_url": item.get("html_url"),
                    # 限制 body 长度，防止后续把 LLM 的 Token 撑爆
                    "body": (item.get("body") or "")[:1000], 
                    "labels": [label["name"] for label in item.get("labels", [])]
                }
                processed_issues.append(issue_data)
                
                # 达到我们需要的数量就停止
                if len(processed_issues) >= limit:
                    break

        print(f"✅ 成功获取 {len(processed_issues)} 个最新的纯 Issue！")
        return processed_issues

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求发生异常！异常详情: {e}")
        return []

# ================= 测试入口 =================
if __name__ == "__main__":
    # 找一个活跃的著名开源项目测试，比如 requests 库
    test_repo = "psf/requests" 
    
    issues = fetch_latest_issues(test_repo, limit=3)
    
    # 打印结果供调试查看
    print("\n" + "="*40)
    for idx, issue in enumerate(issues, 1):
        print(f"[{idx}] Issue #{issue['number']}: {issue['title']}")
        print(f"标签: {issue['labels']}")
        print(f"链接: {issue['html_url']}")
        print("-" * 40)