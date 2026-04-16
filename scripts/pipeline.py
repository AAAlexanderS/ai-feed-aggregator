def ai_process(posts, config):
    try:
        from ai_processor import process_posts
        if os.getenv("ANTHROPIC_API_KEY"):
            return process_posts(posts, config)
    except Exception as e:
        print(f"    [AI] Error: {e}")
    from ai_processor import process_posts_mock
    return process_posts_mock(posts, config)


def prefilter_posts(posts: list) -> list:
    """Drop low-quality posts before sending to Claude to save tokens and improve quality."""
    SPAM_KEYWORDS = [
        "we're hiring", "we are hiring", "join our team", "open role",
        "open position", "we are looking for", "looking to join", "now hiring",
        "newsletter", "subscribe to my", "join my course", "enroll now",
        "sign up", "limited spots", "early bird", "early access",
        "dm me", "link in bio", "comment below", "ping me",
        "join the waitlist", "join waitlist", "book a call",
        "follow for more", "follow me for", "follow for daily",
        "what's your favorite", "what do you think", "agree?", "thoughts?",
        "tag someone", "tag a friend", "drop a 🔥",
        "🚨", "🔥🔥🔥", "important update:", "breaking:",
        "i'm looking for", "i am looking for",
        "repost from", "reposting", "shared from",
    ]
    SPAM_PHRASES_LOW = [
        "ai is changing", "ai will change", "ai will replace",
        "future of design", "future of work", "future of creativity",
        "the next big thing", "game changer",
    ]
    filtered = []
    for p in posts:
        content = (p.get("content") or "").strip()
        if len(content) < 100:
            continue
        cl = content.lower()
        if any(kw in cl for kw in SPAM_KEYWORDS):
            continue
        spam_count = sum(1 for phrase in SPAM_PHRASES_LOW if phrase in cl)
        if spam_count >= 2:
            continue
        filtered.append(p)
    return filtered


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
    fresh_before = len(fresh)
    fresh = prefilter_posts(fresh)
    print(f"  [Prefilter] {fresh_before} -> {len(fresh)} after spam filter")
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
