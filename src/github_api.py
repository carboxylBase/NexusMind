import os
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List

# 引入我们刚刚新建的日志和数据模型
from src.logger import logger
from src.models import GitHubIssue

# 加载环境变量
load_dotenv()

def fetch_latest_issues(repo_name: str, limit: int = 5) -> List[GitHubIssue]:
    """
    拉取指定 GitHub 仓库的最新 Open 状态的 Issues。
    
    :param repo_name: 仓库名称，例如 "tiangolo/fastapi"
    :param limit: 获取的数量限制
    :return: 包含标准 Issue 核心信息的列表
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    url = f"https://api.github.com/repos/{repo_name}/issues"
    params = {
        "state": "open",
        "sort": "updated",
        "direction": "desc",
        "per_page": limit * 2  
    }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True
    )
    def _do_request():
        logger.info(f"🔄 正在尝试拉取仓库 {repo_name} 的最新动态...")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status() 
        return response.json()

    try:
        raw_issues = _do_request()
        processed_issues: List[GitHubIssue] = []

        for item in raw_issues:
            if "pull_request" not in item:
                # 使用标准的 GitHubIssue 类型构建数据
                issue_data: GitHubIssue = {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "html_url": item.get("html_url"),
                    "body": (item.get("body") or "")[:1000], 
                    "labels": [label["name"] for label in item.get("labels", [])]
                }
                processed_issues.append(issue_data)
                
                if len(processed_issues) >= limit:
                    break

        logger.info(f"✅ 成功获取 {len(processed_issues)} 个最新的纯 Issue！")
        return processed_issues

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 网络请求最终失败(已耗尽重试次数)！异常详情: {e}")
        return []

# ================= 测试入口 =================
if __name__ == "__main__":
    test_repo = "psf/requests" 
    issues = fetch_latest_issues(test_repo, limit=3)
    
    print("\n" + "="*40)
    for idx, issue in enumerate(issues, 1):
        # 注意这里依然可以用 issue['title'] 取值，完全兼容之前的写法
        print(f"[{idx}] Issue #{issue['number']}: {issue['title']}")
        print(f"标签: {issue['labels']}")
        print(f"链接: {issue['html_url']}")
        print("-" * 40)