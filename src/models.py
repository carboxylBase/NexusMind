from typing import TypedDict, List, Optional

class GitHubIssue(TypedDict):
    """
    标准化的 GitHub Issue 数据模型
    继承自 TypedDict，运行时依然是字典，完全兼容老代码。
    """
    number: int
    title: str
    state: str
    html_url: str
    body: str
    labels: List[str]

# 未来如果有 PR 监控或者大模型返回结果的结构，都可以统一加在这里