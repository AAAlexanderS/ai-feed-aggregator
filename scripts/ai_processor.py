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
    """Mock AI processing for testing without API key."""
    mock_ai = [
        {"domain":"film_video","title":"I built a full short film pipeline with Runway + DaVinci Resolve + Claude for scripting — here's every step","author_role":"Filmmaker / Creative Technologist","keywords":["Runway","DaVinci","short-film"],"workflow_stage":"rendering / export","tools_mentioned":["Runway Gen-3","DaVinci Resolve","Claude"],"has_demo_or_repo":True,"summary":"Complete breakdown of a 3-minute AI short film production pipeline. Covers prompt iteration for shot consistency, temporal coherence tricks, and how Claude was used to generate shot lists and color grading notes.","why_important":"One of the first detailed process breakdowns showing AI video gen integrated into a real post-production pipeline with professional NLE.","learnings":"Shot consistency technique using seed locking + style reference frames; Claude-assisted color script generation.","worth_bookmarking":True,"credibility_score":9,"creative_workflow_value":10},
        {"domain":"3d_rendering","title":"ComfyUI + 3DGS: my workflow for turning phone scans into stylized game assets in under 10 minutes","author_role":"3D Artist / Technical Artist","keywords":["ComfyUI","3DGS","game-assets"],"workflow_stage":"asset creation","tools_mentioned":["ComfyUI","3D Gaussian Splatting","Blender"],"has_demo_or_repo":True,"summary":"Detailed node-by-node ComfyUI workflow for processing phone LiDAR scans through 3DGS, then applying style transfer for game-ready assets. Includes downloadable workflow JSON.","why_important":"Bridges the gap between casual 3D capture and production-ready game assets using an entirely open-source pipeline.","learnings":"ComfyUI node chain for 3DGS post-processing; style transfer technique that preserves geometric detail.","worth_bookmarking":True,"credibility_score":9,"creative_workflow_value":9},
        {"domain":"ui_ux_design","title":"How I use Figma AI + Claude to go from user research notes to interactive prototype in one afternoon","author_role":"Senior Product Designer","keywords":["Figma-AI","Claude","prototyping"],"workflow_stage":"layout / composition","tools_mentioned":["Figma AI","Claude","v0"],"has_demo_or_repo":False,"summary":"Step-by-step process: research synthesis with Claude → information architecture → Figma AI layout generation → v0 for interactive prototype. Shows real before/after of each stage.","why_important":"Demonstrates a complete AI-augmented design workflow that maintains design judgment while dramatically reducing mechanical work.","learnings":"Prompt structure for Claude research synthesis; Figma AI layout generation best practices; when to switch from AI to manual design.","worth_bookmarking":True,"credibility_score":8,"creative_workflow_value":9},
        {"domain":"motion_design","title":"After Effects + Runway + Rive: building a hybrid motion system for product launches","author_role":"Motion Designer / Art Director","keywords":["After-Effects","Runway","Rive"],"workflow_stage":"animation / motion","tools_mentioned":["After Effects","Runway","Rive","Lottie"],"has_demo_or_repo":True,"summary":"Shows how to combine traditional After Effects animation with AI-generated backgrounds from Runway, then export interactive components via Rive. Includes project file breakdown.","why_important":"Practical hybrid workflow that doesn't replace traditional motion design but augments it — the approach most studios will actually adopt.","learnings":"Compositing AI-generated elements with hand-animated motion; Rive export optimization for web; timeline synchronization technique.","worth_bookmarking":True,"credibility_score":8,"creative_workflow_value":9},
        {"domain":"3d_rendering","title":"text-to-3D is finally usable: my honest assessment after testing every major tool on real client projects","author_role":"Freelance 3D Artist","keywords":["text-to-3D","Meshy","Tripo"],"workflow_stage":"asset creation","tools_mentioned":["Meshy","Tripo","Blender","Substance Painter"],"has_demo_or_repo":False,"summary":"Comparative review of text-to-3D tools tested on actual client briefs. Covers mesh quality, texture fidelity, and what still requires manual cleanup. Brutally honest about limitations.","why_important":"Goes beyond hype to show exactly where text-to-3D fits in a professional 3D pipeline and where it still falls short.","learnings":"Which text-to-3D tool works best for which asset type; manual cleanup workflow for AI-generated meshes; client communication strategy for AI-assisted work.","worth_bookmarking":True,"credibility_score":9,"creative_workflow_value":8},
        {"domain":"film_video","title":"Shot consistency in AI video: the techniques that actually work after 200+ generation tests","author_role":"VFX Supervisor / AI Researcher","keywords":["shot-consistency","Kling","Sora"],"workflow_stage":"iteration / refinement","tools_mentioned":["Kling","Sora","Runway","ComfyUI"],"has_demo_or_repo":True,"summary":"Systematic comparison of consistency techniques across AI video platforms. Tests character locking, style reference, seed manipulation, and LoRA training. Quantifies success rates.","why_important":"Shot consistency is the #1 blocker for professional AI video adoption. This is the most rigorous comparison available.","learnings":"Seed + reference frame technique for Kling; LoRA training pipeline for character consistency; when to give up on gen AI and use traditional VFX.","worth_bookmarking":True,"credibility_score":9,"creative_workflow_value":9},
        {"domain":"ui_ux_design","title":"design-tokens-ai: open-source tool that extracts design tokens from any Figma file and generates theme code","author_role":"Design Engineer","keywords":["design-tokens","open-source","Figma"],"workflow_stage":"handoff / production","tools_mentioned":["Figma API","Tailwind","CSS Variables"],"has_demo_or_repo":True,"summary":"Open-source CLI tool that reads a Figma file, extracts all design tokens (colors, spacing, typography), and generates Tailwind config, CSS variables, or Swift/Kotlin theme files.","why_important":"Solves the design-to-dev token handoff problem that every team faces. Production-ready with 1.8K GitHub stars.","learnings":"Figma API token extraction patterns; multi-platform code generation architecture; how to maintain token parity across platforms.","worth_bookmarking":True,"credibility_score":8,"creative_workflow_value":8},
        {"domain":"motion_design","title":"I replaced 60% of my After Effects work with Rive + AI — here's what I gained and what I lost","author_role":"Senior Motion Designer","keywords":["Rive","After-Effects","workflow-shift"],"workflow_stage":"animation / motion","tools_mentioned":["Rive","After Effects","Midjourney"],"has_demo_or_repo":False,"summary":"Honest account of transitioning from After Effects to Rive for UI animation work, using Midjourney for asset generation. Covers what types of motion work well in each tool.","why_important":"Rare honest assessment of tool migration costs and benefits from someone with 8+ years of AE experience.","learnings":"Decision framework for AE vs Rive per project type; Midjourney prompt techniques for motion-ready assets; interactive animation patterns that don't work in traditional video export.","worth_bookmarking":True,"credibility_score":8,"creative_workflow_value":8},
        {"domain":"3d_rendering","title":"gaussian-splatting-editor: open-source web viewer and editor for 3DGS scenes with AI-powered inpainting","author_role":"Graphics Engineer","keywords":["3DGS","editor","open-source"],"workflow_stage":"iteration / refinement","tools_mentioned":["Three.js","3DGS","WebGPU"],"has_demo_or_repo":True,"summary":"Web-based 3DGS scene editor that runs in-browser with WebGPU. Supports direct manipulation, AI inpainting for scene editing, and export to standard 3D formats.","why_important":"Makes 3D Gaussian Splatting editable for the first time in a browser — huge for accessibility of this technology to non-engineers.","learnings":"WebGPU rendering pipeline for 3DGS; AI inpainting integration for scene modification; browser-based 3D editing architecture.","worth_bookmarking":True,"credibility_score":8,"creative_workflow_value":8},
        {"domain":"ui_ux_design","title":"The real cost of AI-generated UI: what breaks when you skip the design thinking","author_role":"Design Director","keywords":["AI-UI","design-thinking","critique"],"workflow_stage":"concept / ideation","tools_mentioned":["v0","Figma AI","Cursor"],"has_demo_or_repo":False,"summary":"Critical analysis of AI-generated interfaces from a design leadership perspective. Shows specific examples where AI output looked polished but failed usability testing, and proposes a hybrid QA framework.","why_important":"Counter-narrative to 'AI replaces designers' — provides the quality framework for when and how to use AI generation responsibly.","learnings":"Usability testing framework for AI-generated UI; specific failure patterns to watch for; hybrid human-AI design review process.","worth_bookmarking":True,"credibility_score":9,"creative_workflow_value":7},
    ]

    enriched = []
    for i, post in enumerate(posts[:10]):
        post = post.copy()
        post["ai"] = mock_ai[i] if i < len(mock_ai) else mock_ai[0]
        enriched.append(post)
    return enriched
