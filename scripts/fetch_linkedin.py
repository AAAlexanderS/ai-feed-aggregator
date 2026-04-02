"""
LinkedIn 数据采集模块
使用 Apify 的 LinkedIn Scraper Actor 采集高热度 AI 相关帖子
"""

import json
import os
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient


def fetch_linkedin_posts(config_path="config/keywords.json"):
    """
    从 LinkedIn 采集 AI 相关高热度帖子
    
    Returns:
        list[dict]: 标准化后的帖子列表
    """
    with open(config_path, "r") as f:
        config = json.load(f)

    li_config = config["linkedin"]
    filters = li_config["filters"]

    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

    since_date = datetime.now(timezone.utc) - timedelta(days=filters["days_back"])
    all_posts = []

    for query in li_config["search_queries"]:
        print(f"  [LinkedIn] 搜索: {query}")

        # Apify LinkedIn Posts Scraper
        # Actor: apify/linkedin-posts-scraper
        run_input = {
            "searchKeywords": query,
            "maxResults": li_config["max_results_per_query"],
            "sortBy": "relevance",
            "contentType": filters.get("content_type", "posts"),
            "limitPerQuery": li_config["max_results_per_query"],
        }

        try:
            run = client.actor("apify/linkedin-posts-scraper").call(run_input=run_input)
            dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

            for item in dataset_items:
                likes = item.get("numLikes", 0) or 0
                if likes < filters["min_likes"]:
                    continue

                post = normalize_linkedin_post(item)
                if post:
                    all_posts.append(post)

        except Exception as e:
            print(f"  [LinkedIn] 采集失败 ({query}): {e}")
            continue

    # 去重
    seen_ids = set()
    unique_posts = []
    for post in all_posts:
        if post["source_id"] not in seen_ids:
            seen_ids.add(post["source_id"])
            unique_posts.append(post)

    print(f"  [LinkedIn] 共采集 {len(unique_posts)} 条去重后的帖子")
    return unique_posts


def normalize_linkedin_post(raw: dict) -> dict | None:
    """将 Apify 原始数据标准化为统一格式"""
    try:
        text = raw.get("text") or raw.get("commentary") or ""
        if not text.strip():
            return None

        return {
            "source": "linkedin",
            "source_id": raw.get("urn") or raw.get("postUrl", ""),
            "url": raw.get("postUrl", ""),
            "author": {
                "name": raw.get("authorName") or raw.get("author", {}).get("name", "Unknown"),
                "username": raw.get("authorProfileUrl", ""),
                "followers": raw.get("authorFollowers", 0) or 0,
                "verified": False,
                "headline": raw.get("authorHeadline", ""),
            },
            "content": text,
            "media": [img for img in raw.get("images", []) if img],
            "metrics": {
                "likes": raw.get("numLikes", 0) or 0,
                "comments": raw.get("numComments", 0) or 0,
                "reposts": raw.get("numReposts", 0) or 0,
                "views": raw.get("numViews", 0) or 0,
            },
            "published_at": raw.get("postedAt") or raw.get("publishedAt", ""),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        }
    except Exception:
        return None


# ──────────────────────────────────────────────
# 备用方案: 模拟数据 (用于开发测试)
# ──────────────────────────────────────────────

def fetch_linkedin_posts_mock():
    """生成模拟数据用于测试 pipeline"""
    return [
        {
            "source": "linkedin",
            "source_id": "mock_li_001",
            "url": "https://linkedin.com/posts/example-001",
            "author": {
                "name": "Sarah Chen",
                "username": "https://linkedin.com/in/sarah-chen",
                "followers": 45000,
                "verified": False,
                "headline": "VP of Design @ Figma | Ex-Google",
            },
            "content": "Hot take: AI won't replace designers. But designers who use AI will replace those who don't.\n\nHere's my workflow after 6 months of integrating AI into my design process:\n\n1. Research: Claude for competitive analysis\n2. Ideation: Midjourney for moodboards\n3. Wireframing: v0 for rapid prototyping\n4. Testing: AI-powered usability analysis\n\nResult: 3x faster from concept to shipped product.\n\nThe key insight? AI handles the mechanical work. Humans handle the judgment calls.",
            "media": [],
            "metrics": {"likes": 3420, "comments": 234, "reposts": 567, "views": 180000},
            "published_at": datetime.now(timezone.utc).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
        {
            "source": "linkedin",
            "source_id": "mock_li_002",
            "url": "https://linkedin.com/posts/example-002",
            "author": {
                "name": "James Liu",
                "username": "https://linkedin.com/in/james-liu-ai",
                "followers": 89000,
                "verified": False,
                "headline": "Founder & CEO @ AIStudio | Forbes 30 Under 30",
            },
            "content": "We just closed our $12M Series A 🎉\n\nBuilding AI-native design tools for the next generation of product teams.\n\nWhat we learned raising in this market:\n- Investors want to see AI that saves TIME, not just generates content\n- B2B AI companies with clear ROI metrics are getting funded\n- The 'AI wrapper' stigma is real — you need genuine technical moats\n\n18 months ago we were 2 people in a garage. Now we're 25 and serving 500+ design teams.\n\nGrateful for the journey. Hiring across the board — DM me.",
            "media": [],
            "metrics": {"likes": 8900, "comments": 567, "reposts": 1200, "views": 450000},
            "published_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
        {
            "source": "linkedin",
            "source_id": "mock_li_003",
            "url": "https://linkedin.com/posts/example-003",
            "author": {
                "name": "Maria Rodriguez",
                "username": "https://linkedin.com/in/maria-r-design",
                "followers": 23000,
                "verified": False,
                "headline": "Principal Product Designer @ Anthropic",
            },
            "content": "The biggest UX challenge in AI products isn't the AI — it's trust.\n\nAfter 2 years designing AI interfaces, here are the patterns that actually work:\n\n→ Show confidence levels, not just answers\n→ Let users verify AI outputs easily\n→ Progressive disclosure of AI capabilities\n→ Always provide a human override path\n→ Make the AI's limitations visible\n\nThe best AI products feel like a knowledgeable colleague, not a magic oracle.",
            "media": [],
            "metrics": {"likes": 5670, "comments": 345, "reposts": 890, "views": 290000},
            "published_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "language": "en",
        },
    ]


if __name__ == "__main__":
    posts = fetch_linkedin_posts_mock()
    print(json.dumps(posts, indent=2, ensure_ascii=False))
