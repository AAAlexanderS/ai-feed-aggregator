"""
X (Twitter) 数据采集模块
使用 Apify 的 Twitter Scraper Actor 采集高热度 AI 相关推文
"""

import json
import os
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient


def fetch_x_posts(config_path="config/keywords.json"):
    """
    从 X 采集 AI 相关高热度帖子
    
    Returns:
        list[dict]: 标准化后的帖子列表
    """
    # 加载配置
    with open(config_path, "r") as f:
        config = json.load(f)

    x_config = config["x_twitter"]
    filters = x_config["filters"]

    # 初始化 Apify client
    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

    # 计算时间范围
    since_date = (datetime.now(timezone.utc) - timedelta(days=filters["days_back"])).strftime("%Y-%m-%d")

    all_posts = []

    for query in x_config["search_queries"]:
        print(f"  [X] 搜索: {query}")

        # Apify Twitter Scraper actor
        # Actor ID: apify/twitter-scraper
        run_input = {
            "searchTerms": [query],
            "maxTweets": x_config["max_results_per_query"],
            "sort": "Top",  # 按热度排序
            "tweetLanguage": filters.get("language", "en"),
            "since": since_date,
            "until": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }

        try:
            run = client.actor("apify/twitter-scraper").call(run_input=run_input)
            dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

            for item in dataset_items:
                # 过滤低热度内容
                likes = item.get("likeCount", 0) or 0
                retweets = item.get("retweetCount", 0) or 0
                replies = item.get("replyCount", 0) or 0

                if likes < filters["min_likes"]:
                    continue
                if retweets < filters["min_retweets"]:
                    continue

                # 标准化数据格式
                post = normalize_x_post(item)
                if post:
                    all_posts.append(post)

        except Exception as e:
            print(f"  [X] 采集失败 ({query}): {e}")
            continue

    # 去重 (按帖子 ID)
    seen_ids = set()
    unique_posts = []
    for post in all_posts:
        if post["source_id"] not in seen_ids:
            seen_ids.add(post["source_id"])
            unique_posts.append(post)

    print(f"  [X] 共采集 {len(unique_posts)} 条去重后的帖子")
    return unique_posts


def normalize_x_post(raw: dict) -> dict | None:
    """将 Apify 原始数据标准化为统一格式"""
    try:
        text = raw.get("text") or raw.get("full_text") or ""
        if not text.strip():
            return None

        return {
            "source": "x_twitter",
            "source_id": raw.get("id") or raw.get("id_str", ""),
            "url": raw.get("url", ""),
            "author": {
                "name": raw.get("author", {}).get("name", "Unknown"),
                "username": raw.get("author", {}).get("userName", ""),
                "followers": raw.get("author", {}).get("followers", 0),
                "verified": raw.get("author", {}).get("isVerified", False),
            },
            "content": text,
            "media": [m.get("url", "") for m in raw.get("media", []) if m.get("url")],
            "metrics": {
                "likes": raw.get("likeCount", 0) or 0,
                "retweets": raw.get("retweetCount", 0) or 0,
                "replies": raw.get("replyCount", 0) or 0,
                "views": raw.get("viewCount", 0) or 0,
                "bookmarks": raw.get("bookmarkCount", 0) or 0,
            },
            "published_at": raw.get("createdAt", ""),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": raw.get("lang", "en"),
        }
    except Exception:
        return None


# ──────────────────────────────────────────────
# 备用方案: 不用 Apify 时的模拟数据 (用于开发测试)
# ──────────────────────────────────────────────

def fetch_x_posts_mock():
    """生成模拟数据用于测试 pipeline"""
    return [
        {
            "source": "x_twitter",
            "source_id": "mock_x_001",
            "url": "https://x.com/example/status/001",
            "author": {
                "name": "AI Builder",
                "username": "aibuilder",
                "followers": 52000,
                "verified": True,
            },
            "content": "Just launched our AI design assistant that turns wireframes into production-ready code. 10x faster than manual coding. Built with Claude API + custom vision model. Thread 🧵",
            "media": [],
            "metrics": {"likes": 2340, "retweets": 567, "replies": 189, "views": 450000, "bookmarks": 890},
            "published_at": datetime.now(timezone.utc).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
        {
            "source": "x_twitter",
            "source_id": "mock_x_002",
            "url": "https://x.com/example/status/002",
            "author": {
                "name": "Design × AI",
                "username": "designxai",
                "followers": 31000,
                "verified": False,
            },
            "content": "The gap between AI-generated UI and human-designed UI is closing fast. Here's what I learned after using Cursor + v0 + Claude for 30 days straight as a product designer...",
            "media": [],
            "metrics": {"likes": 1890, "retweets": 423, "replies": 156, "views": 320000, "bookmarks": 670},
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
        {
            "source": "x_twitter",
            "source_id": "mock_x_003",
            "url": "https://x.com/example/status/003",
            "author": {
                "name": "Startup Weekly",
                "username": "startupweekly",
                "followers": 120000,
                "verified": True,
            },
            "content": "🚀 AI Startup Funding This Week:\n\n1. Cognition (Devin) - $175M Series B\n2. ElevenLabs - $250M at $3B valuation\n3. Hebbia - $130M Series B\n4. Glean - $260M Series E\n\nAI infrastructure and vertical AI agents are dominating the funding landscape.",
            "media": [],
            "metrics": {"likes": 5670, "retweets": 1230, "replies": 345, "views": 890000, "bookmarks": 2100},
            "published_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
    ]


if __name__ == "__main__":
    # 测试模式
    posts = fetch_x_posts_mock()
    print(json.dumps(posts, indent=2, ensure_ascii=False))
