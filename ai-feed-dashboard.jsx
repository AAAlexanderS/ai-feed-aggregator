import { useState, useEffect } from "react";

const C = {
  bg: "#f5f4f0", card: "#ffffff", text: "#1a1a20", sub: "#6e717c",
  dim: "#a0a3ad",
  pink: "#b91c6a", pinkBg: "#b91c6a08",
  blue: "#1d4ed8", blueBg: "#1d4ed808",
  amber: "#b45309", amberBg: "#b4530908",
  violet: "#7c3aed", violetBg: "#7c3aed08",
};

const DOMAINS = {
  ui_ux_design: { label: "UI/UX Design", emoji: "🎨", color: C.pink, bg: C.pinkBg },
  "3d_rendering": { label: "3D & Rendering", emoji: "🧊", color: C.blue, bg: C.blueBg },
  film_video: { label: "Film & Video", emoji: "🎬", color: C.amber, bg: C.amberBg },
  motion_design: { label: "Motion Design", emoji: "✨", color: C.violet, bg: C.violetBg },
};

const SRC = {
  x_twitter: { icon: "𝕏", bg: "#1a1a20" },
  linkedin: { icon: "in", bg: "#0a66c2" },
  github: { icon: "GH", bg: "#24292f" },
};

const MOCK_DAYS = [
  { date: "2026-04-02", posts: [
    { source:"x_twitter",url:"#",author:{name:"Jake Parker"},ai:{domain:"film_video",title:"I built a full short film pipeline with Runway + DaVinci Resolve + Claude for scripting — here's every step",author_role:"Filmmaker / Creative Technologist",keywords:["Runway","DaVinci","short-film"],workflow_stage:"rendering / export",tools_mentioned:["Runway Gen-3","DaVinci Resolve","Claude"],has_demo_or_repo:true,summary:"Complete breakdown of a 3-minute AI short film production pipeline. Covers prompt iteration for shot consistency, temporal coherence tricks, and Claude-assisted shot lists and color grading notes.",why_important:"One of the first detailed process breakdowns showing AI video gen integrated into a real post-production pipeline.",learnings:"Shot consistency via seed locking + style reference frames; Claude-assisted color script generation.",worth_bookmarking:true,credibility_score:9,creative_workflow_value:10}},
    { source:"x_twitter",url:"#",author:{name:"Maya 3D"},ai:{domain:"3d_rendering",title:"ComfyUI + 3DGS: my workflow for turning phone scans into stylized game assets in under 10 minutes",author_role:"3D Artist / Technical Artist",keywords:["ComfyUI","3DGS","game-assets"],workflow_stage:"asset creation",tools_mentioned:["ComfyUI","3D Gaussian Splatting","Blender"],has_demo_or_repo:true,summary:"Node-by-node ComfyUI workflow for processing phone LiDAR scans through 3DGS, then applying style transfer for game-ready assets. Includes downloadable workflow JSON.",why_important:"Bridges casual 3D capture and production-ready game assets using an entirely open-source pipeline.",learnings:"ComfyUI node chain for 3DGS post-processing; style transfer that preserves geometric detail.",worth_bookmarking:true,credibility_score:9,creative_workflow_value:9}},
    { source:"linkedin",url:"#",author:{name:"Anna Wei"},ai:{domain:"ui_ux_design",title:"How I use Figma AI + Claude to go from user research notes to interactive prototype in one afternoon",author_role:"Senior Product Designer",keywords:["Figma-AI","Claude","prototyping"],workflow_stage:"layout / composition",tools_mentioned:["Figma AI","Claude","v0"],has_demo_or_repo:false,summary:"Step-by-step: research synthesis with Claude → information architecture → Figma AI layout → v0 interactive prototype. Shows real before/after at each stage.",why_important:"Complete AI-augmented design workflow that maintains design judgment while reducing mechanical work.",learnings:"Prompt structure for Claude research synthesis; Figma AI layout generation best practices.",worth_bookmarking:true,credibility_score:8,creative_workflow_value:9}},
    { source:"x_twitter",url:"#",author:{name:"Motion Lab"},ai:{domain:"motion_design",title:"After Effects + Runway + Rive: building a hybrid motion system for product launches",author_role:"Motion Designer / Art Director",keywords:["After-Effects","Runway","Rive"],workflow_stage:"animation / motion",tools_mentioned:["After Effects","Runway","Rive","Lottie"],has_demo_or_repo:true,summary:"Combining traditional AE animation with AI-generated backgrounds from Runway, then exporting interactive components via Rive. Includes project file breakdown.",why_important:"Practical hybrid workflow that augments rather than replaces traditional motion design.",learnings:"Compositing AI elements with hand-animated motion; Rive export optimization; timeline sync technique.",worth_bookmarking:true,credibility_score:8,creative_workflow_value:9}},
    { source:"linkedin",url:"#",author:{name:"Tom Rivera"},ai:{domain:"3d_rendering",title:"text-to-3D is finally usable: my honest assessment after testing every major tool on real client projects",author_role:"Freelance 3D Artist",keywords:["text-to-3D","Meshy","Tripo"],workflow_stage:"asset creation",tools_mentioned:["Meshy","Tripo","Blender","Substance Painter"],has_demo_or_repo:false,summary:"Comparative review of text-to-3D tools on actual client briefs. Covers mesh quality, texture fidelity, and required manual cleanup. Brutally honest about limitations.",why_important:"Goes beyond hype to show exactly where text-to-3D fits in a professional pipeline.",learnings:"Best tool per asset type; manual cleanup workflow for AI meshes; client communication for AI-assisted work.",worth_bookmarking:true,credibility_score:9,creative_workflow_value:8}},
    { source:"x_twitter",url:"#",author:{name:"VFX Breakdown"},ai:{domain:"film_video",title:"Shot consistency in AI video: the techniques that actually work after 200+ generation tests",author_role:"VFX Supervisor / AI Researcher",keywords:["shot-consistency","Kling","Sora"],workflow_stage:"iteration / refinement",tools_mentioned:["Kling","Sora","Runway","ComfyUI"],has_demo_or_repo:true,summary:"Systematic comparison of consistency techniques across AI video platforms. Tests character locking, style reference, seed manipulation, and LoRA training with quantified success rates.",why_important:"Shot consistency is the #1 blocker for professional AI video. This is the most rigorous comparison available.",learnings:"Seed + reference frame technique for Kling; LoRA pipeline for character consistency.",worth_bookmarking:true,credibility_score:9,creative_workflow_value:9}},
    { source:"github",url:"#",author:{name:"tokenflow"},ai:{domain:"ui_ux_design",title:"design-tokens-ai — CLI that extracts design tokens from Figma and generates Tailwind, CSS vars, or Swift/Kotlin themes",author_role:"Design Engineer",keywords:["design-tokens","Figma","open-source"],workflow_stage:"handoff / production",tools_mentioned:["Figma API","Tailwind","CSS Variables"],has_demo_or_repo:true,summary:"Open-source CLI: reads Figma file → extracts all design tokens → generates code for multiple platforms. 1.8K stars.",why_important:"Solves the design-to-dev token handoff problem. Production-ready.",learnings:"Figma API token extraction; multi-platform code generation architecture.",worth_bookmarking:true,credibility_score:8,creative_workflow_value:8}},
    { source:"linkedin",url:"#",author:{name:"Chris Park"},ai:{domain:"motion_design",title:"I replaced 60% of my After Effects work with Rive + AI — here's what I gained and what I lost",author_role:"Senior Motion Designer",keywords:["Rive","After-Effects","workflow-shift"],workflow_stage:"animation / motion",tools_mentioned:["Rive","After Effects","Midjourney"],has_demo_or_repo:false,summary:"Honest account of migrating from AE to Rive for UI animation, using Midjourney for assets. Covers what types of motion work in each tool.",why_important:"Rare honest assessment of tool migration costs from someone with 8+ years of AE.",learnings:"Decision framework for AE vs Rive; Midjourney prompts for motion-ready assets.",worth_bookmarking:true,credibility_score:8,creative_workflow_value:8}},
    { source:"github",url:"#",author:{name:"splat-editor"},ai:{domain:"3d_rendering",title:"gaussian-splatting-editor — web viewer and editor for 3DGS scenes with AI inpainting",author_role:"Graphics Engineer",keywords:["3DGS","WebGPU","editor"],workflow_stage:"iteration / refinement",tools_mentioned:["Three.js","3DGS","WebGPU"],has_demo_or_repo:true,summary:"Browser-based 3DGS scene editor with WebGPU rendering. Supports direct manipulation, AI inpainting, and export to standard formats. 2.4K stars.",why_important:"Makes 3DGS editable in a browser for the first time — huge for accessibility.",learnings:"WebGPU pipeline for 3DGS; AI inpainting for scene editing.",worth_bookmarking:true,credibility_score:8,creative_workflow_value:8}},
    { source:"x_twitter",url:"#",author:{name:"Design Crits"},ai:{domain:"ui_ux_design",title:"The real cost of AI-generated UI: what breaks when you skip the design thinking",author_role:"Design Director",keywords:["AI-UI","design-thinking","critique"],workflow_stage:"concept / ideation",tools_mentioned:["v0","Figma AI","Cursor"],has_demo_or_repo:false,summary:"Critical analysis of AI-generated interfaces. Shows examples that looked polished but failed usability testing. Proposes a hybrid QA framework.",why_important:"Counter-narrative with a quality framework for responsible AI generation in design.",learnings:"Usability testing framework for AI-generated UI; specific failure patterns; hybrid review process.",worth_bookmarking:true,credibility_score:9,creative_workflow_value:7}},
  ]}
];

// ── Components ──

function Src({ source }) {
  const s = SRC[source];
  return <span style={{display:"inline-flex",alignItems:"center",justifyContent:"center",width:20,height:20,borderRadius:5,flexShrink:0,background:s.bg,color:"#fff",fontSize:8,fontWeight:700,fontFamily:"'Space Grotesk',sans-serif",letterSpacing:source==="x_twitter"?-0.8:0}}>{s.icon}</span>;
}

function Domain({ id }) {
  const d = DOMAINS[id] || DOMAINS.ui_ux_design;
  return <span style={{padding:"2px 7px",borderRadius:5,fontSize:10,fontWeight:600,fontFamily:"'Space Grotesk',sans-serif",color:d.color,background:d.bg}}>{d.emoji} {d.label}</span>;
}

function Score({ value, max=10 }) {
  const pct = (value/max)*100;
  const color = value >= 9 ? "#dc2626" : value >= 7 ? "#b45309" : "#6e717c";
  return (
    <div style={{display:"flex",alignItems:"center",gap:4}}>
      <div style={{width:32,height:3,borderRadius:2,background:"#e8e7e3",overflow:"hidden"}}>
        <div style={{width:`${pct}%`,height:"100%",borderRadius:2,background:color,transition:"width 0.4s ease"}}/>
      </div>
      <span style={{fontSize:10,fontWeight:600,color,fontFamily:"'Space Grotesk',sans-serif"}}>{value}</span>
    </div>
  );
}

function Tag({ children }) {
  return <span style={{fontSize:10,color:C.dim,fontWeight:500,fontFamily:"'Space Grotesk',sans-serif"}}>#{children}</span>;
}

function ToolPill({ name }) {
  return <span style={{padding:"1px 6px",borderRadius:4,fontSize:10,fontWeight:500,color:C.sub,background:"#e8e7e3",fontFamily:"'Space Grotesk',sans-serif"}}>{name}</span>;
}

function PostCard({ post, rank }) {
  const [open, setOpen] = useState(false);
  const [hover, setHover] = useState(false);
  const ai = post.ai || {};

  return (
    <div
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      onClick={() => setOpen(!open)}
      style={{
        padding: "14px 16px", borderRadius: 12, cursor: "pointer",
        background: hover || open ? C.card : "transparent",
        boxShadow: hover || open ? "0 2px 12px rgba(0,0,0,0.035)" : "none",
        transition: "all 0.2s ease",
      }}
    >
      {/* Main row */}
      <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
        <span style={{fontSize:12,fontWeight:600,color:C.dim,fontFamily:"'Space Grotesk',sans-serif",minWidth:18,textAlign:"right",paddingTop:2}}>{rank}</span>
        <Src source={post.source} />
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Title */}
          <div style={{fontSize:13.5,fontWeight:600,color:C.text,lineHeight:1.45,letterSpacing:"-0.01em"}}>
            {ai.title}
          </div>

          {/* Meta line */}
          <div style={{display:"flex",flexWrap:"wrap",alignItems:"center",gap:6,marginTop:7}}>
            <Domain id={ai.domain} />
            <span style={{fontSize:10,color:C.dim,fontFamily:"'Space Grotesk'"}}>
              {ai.workflow_stage}
            </span>
            {ai.has_demo_or_repo && (
              <span style={{fontSize:9,fontWeight:700,color:"#0f7b55",background:"#0f7b550f",padding:"1px 6px",borderRadius:4,fontFamily:"'Space Grotesk'",letterSpacing:"0.03em"}}>
                DEMO
              </span>
            )}
            <span style={{marginLeft:"auto",fontSize:10.5,color:C.dim}}>— {post.author?.name}</span>
          </div>

          {/* Keywords */}
          <div style={{display:"flex",flexWrap:"wrap",gap:4,marginTop:6}}>
            {(ai.keywords||[]).map((k,i)=><Tag key={i}>{k}</Tag>)}
          </div>

          {/* Expanded detail */}
          {open && (
            <div style={{marginTop:14,display:"flex",flexDirection:"column",gap:12}}>
              {/* Summary */}
              <p style={{margin:0,fontSize:12.5,lineHeight:1.65,color:C.sub}}>{ai.summary}</p>

              {/* Why important */}
              {ai.why_important && (
                <div style={{padding:"10px 14px",borderRadius:8,background:"#b453090a",borderLeft:"3px solid #b45309"}}>
                  <div style={{fontSize:9,fontWeight:700,color:"#b45309",fontFamily:"'Space Grotesk'",letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:3}}>Why it matters</div>
                  <p style={{margin:0,fontSize:12,lineHeight:1.55,color:C.sub}}>{ai.why_important}</p>
                </div>
              )}

              {/* Learnings */}
              {ai.learnings && (
                <div style={{padding:"10px 14px",borderRadius:8,background:"#1d4ed808",borderLeft:"3px solid #1d4ed8"}}>
                  <div style={{fontSize:9,fontWeight:700,color:"#1d4ed8",fontFamily:"'Space Grotesk'",letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:3}}>Key learnings</div>
                  <p style={{margin:0,fontSize:12,lineHeight:1.55,color:C.sub}}>{ai.learnings}</p>
                </div>
              )}

              {/* Tools + Scores */}
              <div style={{display:"flex",flexWrap:"wrap",alignItems:"center",gap:6}}>
                {(ai.tools_mentioned||[]).map((t,i)=><ToolPill key={i} name={t}/>)}
                <div style={{marginLeft:"auto",display:"flex",gap:12,alignItems:"center"}}>
                  <div style={{display:"flex",alignItems:"center",gap:4}}>
                    <span style={{fontSize:10,color:C.dim,fontFamily:"'Space Grotesk'"}}>Credibility</span>
                    <Score value={ai.credibility_score}/>
                  </div>
                  <div style={{display:"flex",alignItems:"center",gap:4}}>
                    <span style={{fontSize:10,color:C.dim,fontFamily:"'Space Grotesk'"}}>Workflow Value</span>
                    <Score value={ai.creative_workflow_value}/>
                  </div>
                </div>
              </div>

              {/* Author + bookmark */}
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                <span style={{fontSize:11,color:C.dim}}>
                  {post.author?.name}{ai.author_role ? ` · ${ai.author_role}` : ""}
                </span>
                <div style={{display:"flex",gap:8,alignItems:"center"}}>
                  {ai.worth_bookmarking && <span style={{fontSize:10,color:"#b45309",fontWeight:600,fontFamily:"'Space Grotesk'"}}>⭐ Worth saving</span>}
                  <a href={post.url} target="_blank" rel="noopener noreferrer" onClick={e=>e.stopPropagation()}
                    style={{fontSize:11,fontWeight:600,color:C.pink,textDecoration:"none",fontFamily:"'Space Grotesk'"}}>
                    Open →
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DayGroup({ day, isFirst }) {
  const [collapsed, setCollapsed] = useState(!isFirst);
  const weekday = new Date(day.date+"T00:00:00Z").toLocaleDateString("en-US",{weekday:"short"});
  const dc = {};
  day.posts.forEach(p=>{const d=p.ai?.domain;if(d) dc[d]=(dc[d]||0)+1;});

  return (
    <div style={{marginBottom:6}}>
      <button onClick={()=>setCollapsed(!collapsed)} style={{display:"flex",alignItems:"center",gap:10,width:"100%",padding:"12px 16px",border:"none",cursor:"pointer",background:"transparent",textAlign:"left"}}>
        <span style={{fontSize:18,fontWeight:700,color:C.text,fontFamily:"'Space Grotesk',sans-serif",letterSpacing:"-0.03em"}}>{day.date}</span>
        <span style={{fontSize:11,fontWeight:500,color:C.dim,fontFamily:"'Space Grotesk',sans-serif",textTransform:"uppercase",letterSpacing:"0.06em"}}>{weekday}</span>
        <div style={{display:"flex",gap:4,marginLeft:"auto"}}>
          {Object.entries(dc).map(([d,n])=>{const dm=DOMAINS[d]||DOMAINS.ui_ux_design;return <span key={d} style={{padding:"1px 6px",borderRadius:4,fontSize:10,fontWeight:600,color:dm.color,background:dm.bg,fontFamily:"'Space Grotesk'"}}>{dm.emoji}{n}</span>;})}
        </div>
        <span style={{fontSize:14,color:C.dim,transform:collapsed?"rotate(-90deg)":"rotate(0deg)",transition:"transform 0.2s ease",display:"inline-block"}}>▾</span>
      </button>
      {!collapsed && (
        <div style={{display:"flex",flexDirection:"column",gap:2,paddingBottom:8}}>
          {day.posts.map((p,i)=><PostCard key={`${day.date}-${i}`} post={p} rank={i+1}/>)}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [filter, setFilter] = useState("all");
  useEffect(()=>{setTimeout(()=>setLoaded(true),60);},[]);

  const days = MOCK_DAYS.map(d=>{
    if(filter==="all") return d;
    return {...d, posts:d.posts.filter(p=>p.ai?.domain===filter)};
  }).filter(d=>d.posts.length>0);

  return (
    <div style={{fontFamily:"'Inter','Noto Sans SC',system-ui,sans-serif",background:C.bg,color:C.text,minHeight:"100vh"}}>
      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600&display=swap" rel="stylesheet"/>
      <div style={{maxWidth:720,margin:"0 auto",padding:"0 20px"}}>

        <header style={{position:"sticky",top:0,zIndex:10,background:`${C.bg}EE`,backdropFilter:"blur(20px)",WebkitBackdropFilter:"blur(20px)",padding:"24px 0 12px"}}>
          <div style={{display:"flex",alignItems:"baseline",justifyContent:"space-between"}}>
            <h1 style={{margin:0,fontFamily:"'Space Grotesk',sans-serif",fontSize:"1.4rem",fontWeight:700,letterSpacing:"-0.04em"}}>
              AI × Creative Production
            </h1>
            <span style={{fontSize:10,color:C.dim,fontFamily:"'Space Grotesk'",fontWeight:500,letterSpacing:"0.04em"}}>10/day · 𝕏 · LinkedIn · GitHub</span>
          </div>
          <div style={{display:"flex",gap:5,marginTop:12,overflowX:"auto"}}>
            {[{k:"all",l:"All"},...Object.entries(DOMAINS).map(([k,v])=>({k,l:`${v.emoji} ${v.label}`}))].map(f=>(
              <button key={f.k} onClick={()=>setFilter(f.k)} style={{
                padding:"5px 12px",border:"none",borderRadius:7,cursor:"pointer",whiteSpace:"nowrap",
                fontFamily:"'Space Grotesk',sans-serif",fontSize:11,fontWeight:600,
                background:filter===f.k?C.text:"transparent",
                color:filter===f.k?C.bg:C.sub,transition:"all 0.15s ease",
              }}>{f.l}</button>
            ))}
          </div>
        </header>

        <main style={{paddingTop:8,paddingBottom:60,opacity:loaded?1:0,transform:loaded?"none":"translateY(10px)",transition:"opacity 0.4s,transform 0.4s"}}>
          {days.map((d,i)=><DayGroup key={d.date} day={d} isFirst={i===0}/>)}
          {days.length===0&&<div style={{padding:"60px 0",textAlign:"center",color:C.dim,fontSize:13}}>No posts in this category</div>}
        </main>

        <footer style={{padding:"0 0 32px",textAlign:"center"}}>
          <p style={{margin:0,fontSize:10,color:C.dim,fontFamily:"'Space Grotesk'",letterSpacing:"0.04em"}}>AI × Creative Production Intelligence Agent</p>
        </footer>
      </div>
    </div>
  );
}
