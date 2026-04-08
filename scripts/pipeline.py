"""
AI x Creative Production - Daily Pipeline
X (xtdata/twitter-x-scraper) + LinkedIn (harvestapi/linkedin-post-search) + GitHub API
"""
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / "config" / ".env"
if env_path.exists(): load_dotenv(env_path)
BASE = Path(__file__).resolve().parent.parent

def load_config():
    with open(BASE / "config" / "keywords.json") as f:
        return json.load(f)

def load_seen_ids(window_days=30):
    seen = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    feeds_dir = BASE / "data" / "feeds"
    if not feeds_dir.exists(): return seen
    for f in feeds_dir.glob("*.json"):
        try:
            fd = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if fd < cutoff: continue
            with open(f) as fh:
                for p in json.load(fh).get("posts", []):
                    seen.add(p.get("source_id", ""))
        except: continue
    return seen

def fetch_github(config):
    gh = config["platforms"]["github"]
    filters = gh["filters"]
    since = (datetime.now(timezone.utc) - timedelta(days=filters["created_within_days"])).strftime("%Y-%m-%d")
    all_repos = []
    for query in gh["queries"]:
        q = f"{query} created:>{since} stars:>={filters['min_stars']}"
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page={gh['max_per_query']}"
        try:
            req = urllib.request.Request(url, headers={"Accept":"application/vnd.github.v3+json","User-Agent":"AI-Feed"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            for repo in data.get("items", []):
                all_repos.append({
                    "source":"github","source_id":f"gh_{repo['id']}","url":repo["html_url"],
                    "author":{"name":repo["owner"]["login"],"username":repo["owner"]["login"],"headline":""},
                    "content":f"{repo['name']}: {repo.get('description','') or ''}",
                    "metrics":{"stars":repo["stargazers_count"],"forks":repo["forks_count"]},
                    "topics":repo.get("topics",[]),
                    "published_at":repo["created_at"],
                })
        except Exception as e:
            print(f"    [GitHub] failed ({query}): {e}")
    seen = set()
    unique = [r for r in all_repos if r["source_id"] not in seen and not seen.add(r["source_id"])]
    print(f"    [GitHub] {len(unique)} repos")
    return unique

def fetch_x(config):
    from apify_client import ApifyClient
    token = os.getenv("APIFY_API_TOKEN")
    if not token: print("    [X] No token"); return []
    client = ApifyClient(token)
    x_conf = config["platforms"]["x_twitter"]
    filters = x_conf["filters"]
    since = (datetime.now(timezone.utc) - timedelta(days=filters["days_back"])).strftime("%Y-%m-%d")
    all_posts = []
    for query in x_conf["queries"]:
        search = f"{query} min_faves:{filters['min_likes']} since:{since}"
        print(f"    [X] {query}")
        try:
            run = client.actor("xtdata/twitter-x-scraper").call(run_input={
                "searchTerms": [search],
                "maxItems": x_conf["max_per_query"],
                "sort": "Top",
            }, timeout_secs=180)
            items = client.dataset(run["defaultDatasetId"]).list_items().items
            for item in items:
                text = item.get("full_text") or item.get("text") or ""
                if not text.strip(): continue
                likes = item.get("favorite_count", 0) or 0
                if likes < filters["min_likes"]: continue
                author = item.get("author", {})
                all_posts.append({
                    "source":"x_twitter",
                    "source_id": str(item.get("id", "")),
                    "url": item.get("twitterUrl") or item.get("url", ""),
                    "author":{
                        "name": author.get("name") or author.get("userName", "Unknown"),
                        "username": author.get("userName") or author.get("screen_name", ""),
                        "headline": author.get("description", ""),
                        "followers": author.get("followers_count") or author.get("followersCount", 0),
                    },
                    "content": text,
                    "metrics":{
                        "likes": likes,
                        "retweets": item.get("retweet_count", 0) or 0,
                        "replies": item.get("reply_count", 0) or 0,
                        "views": item.get("view_count") or item.get("views", 0) or 0,
                        "bookmarks": item.get("bookmark_count", 0) or 0,
                    },
                    "published_at": item.get("created_at") or item.get("createdAt", ""),
                })
        except Exception as e:
            print(f"    [X] failed ({query}): {e}")
    seen = set()
    unique = [p for p in all_posts if p["source_id"] not in seen and not seen.add(p["source_id"])]
    print(f"    [X] {len(unique)} tweets total")
    return unique

def fetch_linkedin(config):
    from apify_client import ApifyClient
    token = os.getenv("APIFY_API_TOKEN")
    if not token: print("    [LinkedIn] No token"); return []
    client = ApifyClient(token)
    li_conf = config["platforms"]["linkedin"]
    all_posts = []
    for query in li_conf["queries"]:
        print(f"    [LinkedIn] {query}")
        try:
            run = client.actor("harvestapi/linkedin-post-search").call(run_input={
                "searchQueries": [query],
                "maxPosts": li_conf["max_per_query"],
            }, timeout_secs=180)
            items = client.dataset(run["defaultDatasetId"]).list_items().items
            for item in items:
                text = item.get("content") or item.get("text") or ""
                if not text.strip(): continue
                author = item.get("author", {})
                sc = item.get("socialContent", {})
                likes = sc.get("numLikes", 0) or 0
                all_posts.append({
                    "source":"linkedin",
                    "source_id": str(item.get("id", "")),
                    "url": item.get("linkedinUrl", ""),
                    "author":{
                        "name": author.get("name", "Unknown"),
                        "username": author.get("publicIdentifier", ""),
                        "headline": author.get("info", ""),
                    },
                    "content": text,
                    "metrics":{
                        "likes": likes,
                        "comments": sc.get("numComments", 0) or 0,
                        "reposts": sc.get("numShares", 0) or 0,
                    },
                    "published_at": item.get("postedAt", {}).get("date", ""),
                })
        except Exception as e:
            print(f"    [LinkedIn] failed ({query}): {e}")
    seen = set()
    unique = [p for p in all_posts if p["source_id"] not in seen and not seen.add(p["source_id"])]
    print(f"    [LinkedIn] {len(unique)} posts total")
    return unique

def ai_process(posts, config):
    try:
        from ai_processor import process_posts
        if os.getenv("ANTHROPIC_API_KEY"):
            return process_posts(posts, config)
    except Exception as e:
        print(f"    [AI] Error: {e}")
    from ai_processor import process_posts_mock
    return process_posts_mock(posts, config)

def run_pipeline(live=False):
    print(f"\n{'='*56}")
    print(f"  AI x Creative Production  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode: {'LIVE' if live else 'MOCK'}")
    print(f"{'='*56}")
    config = load_config()
    seen = load_seen_ids(config["agent"]["dedup_window_days"])
    print(f"  [{len(seen)} in dedup history]\n")
    print("  Collecting...")
    if live:
        gh = fetch_github(config)
        x = fetch_x(config)
        li = fetch_linkedin(config)
        all_posts = gh + x + li
    else:
        all_posts = [
            {"source":"x_twitter","source_id":"mock1","url":"#","author":{"name":"Test","username":"test","headline":""},"content":"AI design workflow test post","metrics":{"likes":100},"published_at":"2026-04-01T00:00:00Z"},
        ]
    fresh = [p for p in all_posts if p["source_id"] not in seen]
    sc = {}
    for p in fresh: sc[p["source"]] = sc.get(p["source"],0)+1
    print(f"\n  {len(fresh)} fresh / {len(all_posts)} total")
    for s,c in sc.items():
        icon = {"x_twitter":"X","linkedin":"LinkedIn","github":"GitHub"}.get(s,s)
        print(f"     {icon}: {c}")
    if not fresh:
        print("\n  No fresh posts."); return None
    print(f"\n  AI screening {len(fresh)} posts...")
    top = ai_process(fresh, config) if live else fresh[:10]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = BASE / "data" / "feeds"; out_dir.mkdir(parents=True, exist_ok=True)
    daily = {"date":today,"generated_at":datetime.now(timezone.utc).isoformat(),"posts":top}
    out_file = out_dir / f"{today}.json"
    with open(out_file,"w",encoding="utf-8") as f:
        json.dump(daily,f,ensure_ascii=False,indent=2)
    print(f"\n  Saved {len(top)} posts -> {out_file.name}\n")
    for i,p in enumerate(top):
        try:
            ai = p.get("ai",{}) or {}
            src = {"x_twitter":"X","linkedin":"in","github":"GH"}.get(p.get("source",""),"?")
            title = ai.get("title") or (p.get("content") or "")
            print(f"  {i+1:2d}. [{src}] {str(title)[:80]}")
            if ai.get("tools_mentioned"):
                print(f"      tools: {', '.join(ai['tools_mentioned'][:4])} | value: {ai.get('creative_workflow_value','?')}/10")
        except Exception as e:
            print(f"  {i+1:2d}. [print error] {e}")
    return daily

if __name__ == "__main__":
    live = "--live" in sys.argv
    if not live: print("Mock mode (add --live for real data)")
    run_pipeline(live=live)
