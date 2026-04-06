"""
AI × Creative Production — Intelligence Processor
Uses Claude to evaluate posts against strict creative production criteria.
"""

import json, os
from anthropic import Anthropic

AGENT_SYSTEM_PROMPT = """You are an "AI × Creative Production Intelligence Screening Agent".

Your job: evaluate social media posts and GitHub repos for their relevance and learning value to creative professionals who use AI in their production workflows.

## Domains (pick the best fit):
- ui_ux_design: UI/UX, Product Design, Figma AI, design-to-code, prototyping
- 3d_rendering: 3D rendering/generation, Blender AI, ComfyUI 3D, text-to-3D, 3DGS, NeRF
- film_video: Film editing, AI video workflows, cinematic editing, shot consistency, timeline editing
- motion_design: Motion design, animation, After Effects AI, motion control, hybrid workflows

## Priority content (COLLECT):
- Original experience sharing with process detail
- Practical workflow breakdown with steps
- Content with demo / repo / timeline / scene file / workflow nodes
- Explains HOW AI enters the creative process, not just shows results
- Comments section has professional discussion

## Exclude (REJECT):
- Generic AI news unrelated to creative production
- Pure showcase without process explanation
- No-opinion reposts and content farms
- Pure marketing posts
- High engagement but no learning value

## For each post, you MUST evaluate:
1. Which creative domain it belongs to
2. Which production stage it impacts
3. Whether it can be reused as a workflow
4. Whether it demonstrates controllability (scene / camera / motion / timeline / consistency)
5. How high the learning value is for designers, motion designers, 3D artists, or creative technologists

## Output exactly 10 posts as a JSON array. Each object must have ALL these fields:
{
  "index": 0,
  "pass": true,
  "domain": "ui_ux_design",
  "title": "Original language title extracted or summarized from the post (keep original language, under 120 chars)",
  "author_role": "Product Designer / 3D Artist / Motion Designer / Creative Technologist / etc.",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "workflow_stage": "concept / ideation | asset creation | layout / composition | animation / motion | rendering / export | iteration / refinement | handoff / production",
  "tools_mentioned": ["Figma", "Claude", "ComfyUI"],
  "has_demo_or_repo": true,
  "summary": "2-3 sentence summary of what the post covers and the process described. Keep original language.",
  "why_important": "One sentence: why this matters to creative professionals. Keep original language.",
  "learnings": "What specific technique, workflow, or insight can be extracted. Keep original language.",
  "worth_bookmarking": true,
  "credibility_score": 8,
  "creative_workflow_value": 9
}

Rules:
- credibility_score (1-10): based on author expertise, evidence provided, specificity of claims
- creative_workflow_value (1-10): how useful this is for someone building AI into their creative pipeline
- Only pass=true posts that genuinely teach something about AI in creative production
- Keep ALL text fields in the original language of the post (do NOT translate)
- Pick the 10 best posts, ensure diversity across domains when possible
- If fewer than 10 qualify, return fewer — quality over quantity"""


def process_posts(posts: list, config: dict) -> list:
    """Process posts through the AI Creative Production agent."""
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    except Exception:
        return process_posts_mock(posts, config)

    # Build post block
    posts_block = ""
    for i, p in enumerate(posts):
        src = p.get("source", "?")
        author = p.get("author", {})
        metrics = p.get("metrics", {})
        posts_block += f"""
[{i}] Platform: {src}
Author: {author.get('name', '?')} | {author.get('headline', author.get('username', ''))}
Content: {p.get('content', '')[:600]}
Metrics: {json.dumps(metrics)}
Topics: {', '.join(p.get('topics', []))}
---"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            system=AGENT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Evaluate these posts and return the top 10 as JSON:\n{posts_block}"}],
        )

        text = resp.content[0].text.strip()
        if text.startswith("```"): text = text.split("\n", 1)[1]
        if text.endswith("```"): text = text[:-3]
        results = json.loads(text.strip())

        enriched = []
        for r in results:
            if not r.get("pass", True):
                continue
            idx = r.get("index", 0)
            if idx >= len(posts):
                continue
            post = posts[idx].copy()
            post["ai"] = {
                "domain": r.get("domain", "ui_ux_design"),
                "title": r.get("title", post.get("content", "")[:100]),
                "author_role": r.get("author_role", ""),
                "keywords": r.get("keywords", []),
                "workflow_stage": r.get("workflow_stage", ""),
                "tools_mentioned": r.get("tools_mentioned", []),
                "has_demo_or_repo": r.get("has_demo_or_repo", False),
                "summary": r.get("summary", ""),
                "why_important": r.get("why_important", ""),
                "learnings": r.get("learnings", ""),
                "worth_bookmarking": r.get("worth_bookmarking", False),
                "credibility_score": r.get("credibility_score", 5),
                "creative_workflow_value": r.get("creative_workflow_value", 5),
            }
            enriched.append(post)

        return enriched[:10]

    except Exception as e:
        print(f"  [AI] Processing error: {e}")
        return process_posts_mock(posts, config)


def process_posts_mock(posts: list, config: dict) -> list:
    """Fallback: generate basic AI fields from post content when Claude API fails."""
    enriched = []
    for i, post in enumerate(posts[:10]):
        post = post.copy()
        content = post.get("content", "")[:200]
        content_lower = content.lower()
        if any(w in content_lower for w in ["3d", "blender", "comfyui", "gaussian", "nerf", "render"]):
            domain = "3d_rendering"
        elif any(w in content_lower for w in ["video", "film", "runway", "kling", "sora", "cinema", "vfx"]):
            domain = "film_video"
        elif any(w in content_lower for w in ["motion", "animation", "after effects", "rive", "lottie"]):
            domain = "motion_design"
        else:
            domain = "ui_ux_design"
        post["ai"] = {
            "domain": domain,
            "title": content[:120].split("\n")[0],
            "author_role": post.get("author", {}).get("headline", "")[:60],
            "keywords": [],
            "workflow_stage": "",
            "tools_mentioned": [],
            "has_demo_or_repo": "github.com" in post.get("url", ""),
            "summary": content[:200],
            "why_important": "",
            "learnings": "",
            "worth_bookmarking": False,
            "credibility_score": 5,
            "creative_workflow_value": 5,
        }
        enriched.append(post)
    return enriched
