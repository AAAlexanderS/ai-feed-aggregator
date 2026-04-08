"""
ai_processor.py
AI screening layer for the AI × Creative Production feed aggregator.
"""

import os
import json
import anthropic

AGENT_SYSTEM_PROMPT = """You are a STRICT editorial curator for AI × Creative Production content. Your job is to filter out 90% of noise and surface only the most concrete, actionable, technically-grounded posts. Be ruthless.
## Domains (pick the best fit):
- ui_ux_design: UI/UX, Product Design, Figma AI, design-to-code, prototyping
- 3d_rendering: 3D rendering/generation, Blender AI, ComfyUI 3D, text-to-3D, 3DGS, NeRF
- film_video: Film editing, AI video workflows, cinematic editing, shot consistency
- motion_design: Motion design, animation, After Effects AI, hybrid workflows
## INCLUSION CRITERIA — A post must satisfy AT LEAST 3 of these to pass:
1. Names specific tools AND describes how they were used together
2. Includes concrete steps, settings, parameters, or workflow nodes
3. Shows before/after, demos, repos, video clips, or real screenshots
4. Author is a practitioner sharing first-hand experience (not commentary)
5. Provides quantifiable details (time saved, output count, success rate, costs)
6. Reveals failures, limitations, or honest trade-offs
## REJECT IMMEDIATELY if ANY of these apply:
- Generic AI hype with no concrete process ("AI is changing everything")
- Personal essays or reflections without technical substance
- Marketing posts promoting courses, newsletters, books, paid communities
- Job postings, hiring announcements, "we're growing" posts
- "I built X with AI" without explaining HOW
- Pure tool/feature announcements without showing actual usage
- Reposts, news summaries, content aggregation
- Posts under 80 words
- Vague claims like "AI will replace designers" or "the future of work"
- Self-promotion of consulting / coaching services
- Engagement-bait questions ("What's your favorite AI tool?")
- LinkedIn-style motivational content
- Posts that mention AI tools but don't actually demonstrate using them
- Content where author is selling something (course, template, service)
## QUALITY THRESHOLD
- credibility_score (1-10): based on author expertise, specificity, evidence
- creative_workflow_value (1-10): how actionable for someone doing creative work
- BOTH scores MUST be >= 7 to pass. If fewer than 10 posts qualify, return fewer. NEVER pad with mediocre content.
## Output format
Return a JSON array. For each post that passes:
{
  "index": 0,
  "pass": true,
  "domain": "ui_ux_design",
  "title": "Concrete headline based on actual post content (under 120 chars, original language)",
  "author_role": "Inferred role from headline",
  "keywords": ["specific", "technical", "terms"],
  "workflow_stage": "concept / ideation | asset creation | layout / composition | animation / motion | rendering / export | iteration / refinement | handoff / production",
  "tools_mentioned": ["specific tools named"],
  "has_demo_or_repo": true,
  "summary": "2 sentences: WHAT they did and HOW. Original language.",
  "why_important": "One sentence: why this matters to creative practitioners. Original language.",
  "learnings": "Specific technical takeaway someone could apply. Original language.",
  "worth_bookmarking": true,
  "credibility_score": 8,
  "creative_workflow_value": 9
}
Rules:
- Keep ALL text fields in the original language of the post (do NOT translate)
- It is BETTER to return 3 excellent posts than 10 mediocre ones
- Quality over quantity — be ruthless"""


def _build_user_prompt(posts: list[dict]) -> str:
    """Format posts list into a prompt for Claude."""
    lines = []
    for i, post in enumerate(posts):
        lines.append(f"=== POST {i} ===")
        lines.append(f"Author: {post.get('author', {}).get('name', 'Unknown')}")
        lines.append(f"Text: {post.get('text', post.get('content', ''))}")
        url = post.get('url', post.get('postUrl', ''))
        if url:
            lines.append(f"URL: {url}")
        lines.append("")
    return "\n".join(lines)


def _call_claude(posts: list[dict]) -> list[dict]:
    """Call Claude API and return parsed JSON results."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_prompt = _build_user_prompt(posts)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=AGENT_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Screen these {len(posts)} posts. Return ONLY a JSON array, no markdown, no preamble.\n\n{user_prompt}"
            }
        ]
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def process_posts(posts: list[dict], config: dict = None) -> list[dict]:
    """
    Live mode: screen posts through Claude API.
    Returns enriched posts with ai field populated, sorted by score desc.
    """
    if not posts:
        return []

    BATCH_SIZE = 30
    enriched = []

    for i in range(0, len(posts), BATCH_SIZE):
        batch = posts[i:i + BATCH_SIZE]
        print(f"    [AI] Screening batch {i // BATCH_SIZE + 1} ({len(batch)} posts)...")
        try:
            results = _call_claude(batch)
            for result in results:
                if result.get("pass") is not True:
                    continue
                idx = result.get("index")
                if idx is None or idx >= len(batch):
                    continue
                # Preserve original post structure, attach AI fields under "ai"
                post = batch[idx].copy()
                post["ai"] = {
                    "domain": result.get("domain", "ui_ux_design"),
                    "title": result.get("title", post.get("content", "")[:100]),
                    "author_role": result.get("author_role", ""),
                    "keywords": result.get("keywords", []),
                    "workflow_stage": result.get("workflow_stage", ""),
                    "tools_mentioned": result.get("tools_mentioned", []),
                    "has_demo_or_repo": result.get("has_demo_or_repo", False),
                    "summary": result.get("summary", ""),
                    "why_important": result.get("why_important", ""),
                    "learnings": result.get("learnings", ""),
                    "worth_bookmarking": result.get("worth_bookmarking", False),
                    "credibility_score": result.get("credibility_score", 5),
                    "creative_workflow_value": result.get("creative_workflow_value", 5),
                }
                enriched.append(post)
        except json.JSONDecodeError as e:
            print(f"    [AI] JSON parse error: {e}")
        except Exception as e:
            print(f"    [AI] Error: {e}")

    # Sort by combined score
    enriched.sort(
        key=lambda p: (
            p.get("ai", {}).get("credibility_score", 0)
            + p.get("ai", {}).get("creative_workflow_value", 0)
        ),
        reverse=True
    )

    print(f"    [AI] {len(enriched)} posts passed out of {len(posts)} screened")
    return enriched
