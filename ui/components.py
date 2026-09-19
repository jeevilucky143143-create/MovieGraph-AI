"""Reusable UI Components for MovieGraph AI.

Generates HTML/CSS components adhering to the Stitch Pastel Design System.
Includes realistic web components:
- Top Navigation Bar with Live Knowledge Graph Ticker
- Interactive Answer Cards with AI Persona Badges & Provenance
- Six Degrees Connection Chain Visualizer (Bacon Number)
- Movie Head-to-Head Comparison Panels
- Embedded Interactive Force-Directed Physics Graph (Vis.js)
"""

import json
import re
import textwrap
from typing import Dict, List, Any, Optional
import streamlit as st
import streamlit.components.v1 as components
from rag.rag_pipeline import RAGResponse
from recommendation.recommender import MovieRecommendation


def render_navbar(db_status: Dict[str, Any]) -> None:
    """Renders the top navigation bar with live status and dataset metrics."""
    is_live = db_status.get("is_connected", False)
    total_nodes = db_status.get("total_nodes", 68627)
    movie_count = db_status.get("movies_count", 4807)
    person_count = db_status.get("persons_count", 63820)

    status_badge_text = "Live Neo4j Instance" if is_live else "TMDb 5000 Graph Active"
    status_dot_cls = "status-dot-green"

    navbar_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 0 24px 0; border-bottom: 1.5px solid #E8E5DF; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; border-radius: 14px; background: linear-gradient(135deg, #B4A7D6 0%, #A3B899 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(180, 167, 214, 0.35);">
                <span style="font-size: 22px;">🎬</span>
            </div>
            <div>
                <div style="font-family: 'Manrope', sans-serif; font-size: 1.5rem; font-weight: 800; color: #2D3142; letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px;">
                    MovieGraph <span style="background: linear-gradient(135deg, #53457A, #A3B899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI</span>
                    <span style="font-size: 0.72rem; font-weight: 700; background: #EFEAF7; color: #53457A; padding: 2px 8px; border-radius: 9999px; border: 1px solid #B4A7D6;">PRO</span>
                </div>
                <div style="font-family: 'Manrope', sans-serif; font-size: 0.82rem; font-weight: 500; color: #6E7282;">
                    Explainable Knowledge Graph Discovery & Grounded RAG Assistant
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="status-pill" title="{db_status.get('status_message', '')}">
                <span class="{status_dot_cls}"></span>
                <span style="color: #2D3142; font-size: 0.82rem; font-weight: 700;">{status_badge_text}</span>
            </div>
            <div style="display: flex; gap: 6px; font-size: 0.78rem; font-weight: 600; color: #6E7282; background: #FFFFFF; padding: 6px 12px; border-radius: 9999px; border: 1px solid #E8E5DF; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                <span>🎬 {movie_count:,} Films</span>
                <span>•</span>
                <span>👤 {person_count:,} People</span>
            </div>
        </div>
    </div>
    """
    st.html(textwrap.dedent(navbar_html))


def render_hero_header() -> None:
    """Renders the discovery hero header section."""
    hero_html = """
    <div style="text-align: center; max-width: 860px; margin: 0 auto 24px auto;">
        <div style="display: inline-flex; align-items: center; gap: 6px; background: #EFEAF7; color: #53457A; padding: 4px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; border: 1px solid #B4A7D6; margin-bottom: 12px;">
            <span>✨</span> Powered by Neo4j Knowledge Graph & TMDb 5000
        </div>
        <h1 style="font-family: 'Manrope', sans-serif; font-size: 2.7rem; font-weight: 800; color: #2D3142; letter-spacing: -0.03em; margin-bottom: 12px; line-height: 1.2;">
            Ask anything about movies. Grounded in graph truth.
        </h1>
        <p style="font-family: 'Manrope', sans-serif; font-size: 1.1rem; color: #6E7282; line-height: 1.6; margin: 0 auto;">
            Explore over 4,800 movies, 63,000+ cast and crew, and 135,000+ relationships. Zero hallucinations guaranteed.
        </p>
    </div>
    """
    st.html(textwrap.dedent(hero_html))


def format_answer_html(raw_answer: str) -> str:
    """Formats markdown-styled response text into structured, elegant HTML."""
    paragraphs = raw_answer.strip().split("\n\n")
    html_paragraphs = []

    for p in paragraphs:
        lines = [line.strip() for line in p.split("\n") if line.strip()]
        if not lines:
            continue

        # Check if this block is a bulleted list (must all be bullets and not headers)
        if all((line.startswith(("•", "- ", "* ")) and not line.startswith("**")) for line in lines):
            items_html = []
            for line in lines:
                clean_line = re.sub(r"^[•\-\*]\s*", "", line)
                clean_line = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color: #2D3142; font-weight: 700;'>\1</strong>", clean_line)
                clean_line = re.sub(r"\*(.+?)\*", r"<em style='color: #53457A;'>\1</em>", clean_line)
                clean_line = re.sub(r"`(.+?)`", r"<code style='background: #EFEAF7; color: #53457A; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; font-family: monospace;'>\1</code>", clean_line)
                items_html.append(
                    f"""<li style="margin-bottom: 7px; line-height: 1.55; color: #2D3142; font-size: 1.02rem;">
                        {clean_line}
                    </li>"""
                )
            html_paragraphs.append(
                f"""<ul style="margin: 8px 0 14px 20px; padding-left: 2px; list-style-type: '• '; color: #53457A;">{''.join(items_html)}</ul>"""
            )
        else:
            block_html = []
            for line in lines:
                header_match = re.match(r"^\*\*(.+?)\*\*:?$", line)
                if header_match:
                    hdr = header_match.group(1)
                    block_html.append(
                        f"""<div style="font-family: 'Manrope', sans-serif; font-size: 0.98rem; font-weight: 800; color: #53457A; margin-top: 14px; margin-bottom: 4px; letter-spacing: 0.02em;">
                            📌 {hdr}
                        </div>"""
                    )
                else:
                    clean_line = re.sub(r"\*\*(.+?)\*\*", r"<strong style='color: #2D3142; font-weight: 700;'>\1</strong>", line)
                    clean_line = re.sub(r"\*(.+?)\*", r"<em style='color: #53457A;'>\1</em>", clean_line)
                    clean_line = re.sub(r"`(.+?)`", r"<code style='background: #EFEAF7; color: #53457A; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; font-family: monospace;'>\1</code>", clean_line)
                    block_html.append(
                        f"""<p style="margin: 0 0 10px 0; line-height: 1.65; color: #2D3142; font-size: 1.06rem;">{clean_line}</p>"""
                    )
            html_paragraphs.append("".join(block_html))

    return "".join(html_paragraphs)


def render_answer_card(res: RAGResponse) -> None:
    """Renders the grounded answer experience card with persona badge, output style badge, and provenance."""
    persona_icons = {
        "Cinematic Scholar": "🎓",
        "Casual Movie Buddy": "🍿",
        "Cannes Film Critic": "🖋️",
        "Studio Producer": "💼",
    }
    persona_icon = persona_icons.get(res.persona, "🎬")

    style_icons = {
        "Concise Narrative": "💬",
        "Bulleted Intelligence Brief": "📋",
        "Detailed Analysis": "📑",
    }
    style_icon = style_icons.get(res.output_style, "✨")

    # Build badges HTML
    badges_html = ""
    for b in res.entity_badges:
        b_type = b.get("type", "")
        b_label = b.get("label", "")
        badge_cls = "badge-sage" if b_type == "movie" else "badge-lavender" if b_type in ["person", "actor"] else "badge-peach"
        icon = "🎬" if b_type == "movie" else "👤" if b_type in ["person", "actor"] else "🔗"
        badges_html += f'<span class="badge-pill {badge_cls}"><span style="font-size:0.75rem;">{icon}</span>{b_label}</span>'

    if not badges_html:
        badges_html = '<span style="font-size: 0.85rem; color: #6E7282;">No specific entities found.</span>'

    formatted_answer = format_answer_html(res.answer)

    answer_card_html = f"""
    <div class="stitch-card" style="border-top: 4px solid #B4A7D6; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
            <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; color: #6E7282; text-transform: uppercase;">
                Your Question
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <div style="display: inline-flex; align-items: center; gap: 5px; background: #EFEAF7; color: #53457A; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; border: 1px solid #B4A7D6;">
                    <span>{persona_icon}</span> {res.persona}
                </div>
                <div style="display: inline-flex; align-items: center; gap: 5px; background: #FAF2EC; color: #8C4724; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; border: 1px solid #F7D1BA;">
                    <span>{style_icon}</span> {res.output_style}
                </div>
            </div>
        </div>

        <div style="font-family: 'Manrope', sans-serif; font-size: 1.35rem; font-weight: 700; color: #2D3142; margin-bottom: 18px;">
            "{res.question}"
        </div>

        <div style="background-color: #FAF8F5; border-radius: 16px; padding: 22px 24px; border: 1px solid #E8E5DF; margin-bottom: 20px; box-shadow: inset 0 2px 6px rgba(0,0,0,0.01);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; color: #53457A; text-transform: uppercase;">
                    Grounded Answer ({res.provider})
                </div>
                <div style="font-size: 0.75rem; font-weight: 600; color: #38522E; background: #EBF2E8; padding: 2px 8px; border-radius: 9999px;">
                    ✓ Zero Hallucination Guardrail Active
                </div>
            </div>
            <div style="font-family: 'Manrope', sans-serif; color: #2D3142; font-weight: 500;">
                {formatted_answer}
            </div>
        </div>

        <div style="margin-bottom: 18px;">
            <div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; color: #6E7282; text-transform: uppercase; margin-bottom: 10px;">
                Knowledge Entities Identified in Graph
            </div>
            <div>
                {badges_html}
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 14px; border-top: 1px solid #E8E5DF; font-size: 0.85rem; color: #6E7282;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span>⚡</span>
                <span>Provenance: <strong>TMDb 5000 Knowledge Graph</strong></span>
                <span style="background: #EBF2E8; color: #38522E; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">Verified Grounding</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">
                Retrieved in {res.execution_time_ms} ms | {res.record_count} records
            </div>
        </div>
    </div>
    """
    st.html(textwrap.dedent(answer_card_html))

    # Expandable Technical Grounding Details
    with st.expander("🔍 Inspect Full Cypher Execution & Graph Trace"):
        st.markdown(f"**Query Intent:** `{res.query_type}` ({res.template_name})")
        st.markdown(f"**Intent Detection:** {res.intent_explanation}")
        st.markdown("**Parameterized Cypher Query:**")
        st.code(res.cypher_query, language="cypher")
        st.markdown(f"**Query Parameters:** `{res.parameters}`")
        st.markdown(f"**Retrieved Records ({res.record_count} total):**")
        st.json(res.records[:10])


def render_connection_path(path: List[Dict[str, str]], exec_ms: float) -> None:
    """Renders the step-by-step visual chain for Six Degrees of Separation."""
    if not path:
        st.warning("No connection path found within 6 degrees of separation in the knowledge graph.")
        return

    # Count degrees
    person_nodes = [step for step in path if step["type"] == "person"]
    movie_nodes = [step for step in path if step["type"] == "movie"]
    degrees = len(movie_nodes)

    header_html = f"""
    <div style="margin: 20px 0 12px 0; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.3rem; font-weight: 800; color: #2D3142; margin: 0;">
            Found Connection in <span style="color: #53457A;">{degrees} Degrees of Separation</span>
        </h3>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #6E7282;">
            Traversed in {exec_ms:.2f} ms
        </div>
    </div>
    """
    st.html(textwrap.dedent(header_html))

    steps_html = []
    for idx, step in enumerate(path):
        if step["type"] == "person":
            p_name = step["name"]
            steps_html.append(f"""
            <div class="path-step-person">
                <span>👤</span> <strong>{p_name}</strong>
            </div>
            """)
        elif step["type"] == "movie":
            m_name = step["name"]
            rel_from = step.get("rel_from", "LINKED")
            rel_to = step.get("rel_to", "LINKED")
            steps_html.append(f"""
            <div class="path-arrow">➔</div>
            <div class="path-step-movie" title="Connected via {rel_from} and {rel_to}">
                <span>🎬</span> <strong>{m_name}</strong>
            </div>
            <div class="path-arrow">➔</div>
            """)

    chain_content = "".join(steps_html)
    container_html = f"""
    <div class="path-chain-container">
        {chain_content}
    </div>
    """
    st.html(textwrap.dedent(container_html))


def render_movie_comparison(comp: Dict[str, Any]) -> None:
    """Renders head-to-head graph comparison between two movies."""
    m1 = comp["movie_a"]
    m2 = comp["movie_b"]

    score = comp["affinity_score"]
    pct = comp["similarity_pct"]
    shared_act = comp["shared_actors"]
    shared_dirs = comp["shared_directors"]

    banner_html = f"""
    <div class="compare-score-banner">
        <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; color: #53457A; text-transform: uppercase; margin-bottom: 6px;">
            Graph Affinity Score
        </div>
        <div style="font-size: 2.6rem; font-weight: 800; color: #2D3142; line-height: 1;">
            +{score} <span style="font-size: 1.1rem; color: #6E7282; font-weight: 500;">({pct}% Graph Overlap)</span>
        </div>
        <div style="font-size: 0.9rem; color: #6E7282; margin-top: 6px;">
            {f"Connected via {len(shared_act)} shared actors and {len(shared_dirs)} shared directors" if (shared_act or shared_dirs) else "No direct cast or director overlap found in the knowledge graph."}
        </div>
    </div>
    """
    st.html(textwrap.dedent(banner_html))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🎬 {m1['title']}")
        st.markdown(f"**Year:** `{m1.get('released', 'N/A')}` | **Tagline:** *'{m1.get('tagline', 'N/A')}'*")
        st.markdown(f"**Directors:** {', '.join(m1.get('directors', [])) or 'N/A'}")
        st.markdown(f"**Cast Count in Graph:** {len(m1.get('actors', []))} actors")
        with st.expander(f"View Full Cast of {m1['title']}"):
            st.table([{"Actor": a["name"]} for a in m1.get("actors", [])[:15]])

    with col2:
        st.markdown(f"### 🎬 {m2['title']}")
        st.markdown(f"**Year:** `{m2.get('released', 'N/A')}` | **Tagline:** *'{m2.get('tagline', 'N/A')}'*")
        st.markdown(f"**Directors:** {', '.join(m2.get('directors', [])) or 'N/A'}")
        st.markdown(f"**Cast Count in Graph:** {len(m2.get('actors', []))} actors")
        with st.expander(f"View Full Cast of {m2['title']}"):
            st.table([{"Actor": a["name"]} for a in m2.get("actors", [])[:15]])

    if shared_act or shared_dirs:
        st.markdown("---")
        st.markdown("#### 🔗 Shared Connections in Knowledge Graph")
        if shared_dirs:
            st.markdown(f"**Same Director(s):** {', '.join(shared_dirs)}")
        if shared_act:
            st.markdown(f"**Shared Cast Members ({len(shared_act)}):** {', '.join(shared_act)}")


def render_interactive_network_graph(movie_title: str, graph_data: Dict[str, Any]) -> None:
    """Embeds an interactive physics force-directed graph canvas using Vis.js, centered in viewport."""
    nodes_json = json.dumps(graph_data["nodes"])
    edges_json = json.dumps(graph_data["edges"])

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
      <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .canvas-card {{
            position: relative;
            width: 100%;
            height: 600px;
            background: linear-gradient(135deg, #FFFFFF 0%, #FAF8F5 100%);
            border: 1px solid #E8E5DF;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(45, 49, 66, 0.04);
            overflow: hidden;
        }}
        #network {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .legend {{
            position: absolute;
            top: 14px;
            left: 16px;
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 7px 14px;
            border-radius: 10px;
            border: 1px solid #E8E5DF;
            font-size: 12px;
            color: #2D3142;
            display: flex;
            align-items: center;
            gap: 14px;
            z-index: 10;
            font-weight: 600;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            pointer-events: auto;
        }}
        .controls-toolbar {{
            position: absolute;
            top: 14px;
            right: 16px;
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 6px 10px;
            border-radius: 10px;
            border: 1px solid #E8E5DF;
            display: flex;
            align-items: center;
            gap: 6px;
            z-index: 10;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            pointer-events: auto;
        }}
        .ctrl-btn {{
            background: #F5F2FA;
            color: #53457A;
            border: 1px solid #D6CEE8;
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
            user-select: none;
        }}
        .ctrl-btn:hover {{
            background: #53457A;
            color: #FFFFFF;
            border-color: #53457A;
            transform: translateY(-1px);
        }}
        .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 4px;
            vertical-align: middle;
        }}
      </style>
    </head>
    <body>
      <div class="canvas-card">
        <div class="legend">
          <span><span class="dot" style="background:#53457A;"></span>Movie</span>
          <span><span class="dot" style="background:#B4A7D6;"></span>Director</span>
          <span><span class="dot" style="background:#A3B899;"></span>Actor</span>
          <span style="color:#6E7282; font-weight:normal; font-size:11px;">(Drag nodes, scroll to zoom)</span>
        </div>
        <div class="controls-toolbar">
          <button class="ctrl-btn" onclick="fitCenter()" title="Fit and center graph view">🎯 Center Graph</button>
          <button class="ctrl-btn" onclick="zoomIn()" title="Zoom In">➕</button>
          <button class="ctrl-btn" onclick="zoomOut()" title="Zoom Out">➖</button>
          <button class="ctrl-btn" onclick="resetGraph()" title="Re-simulate & Center">🔄 Reset</button>
        </div>
        <div id="network"></div>
      </div>

      <script type="text/javascript">
        let network = null;

        function fitCenter() {{
            if (network) {{
                network.fit({{
                    animation: {{
                        duration: 500,
                        easingFunction: 'easeInOutQuad'
                    }}
                }});
            }}
        }}

        function zoomIn() {{
            if (network) {{
                const scale = network.getScale();
                network.moveTo({{ scale: Math.min(scale * 1.3, 2.5), animation: {{ duration: 250 }} }});
            }}
        }}

        function zoomOut() {{
            if (network) {{
                const scale = network.getScale();
                network.moveTo({{ scale: Math.max(scale * 0.75, 0.25), animation: {{ duration: 250 }} }});
            }}
        }}

        function resetGraph() {{
            if (network) {{
                network.stabilize(80);
                setTimeout(fitCenter, 300);
            }}
        }}

        try {{
            const nodes = new vis.DataSet({nodes_json});
            const edges = new vis.DataSet({edges_json});
            const container = document.getElementById('network');
            const data = {{ nodes: nodes, edges: edges }};

            const options = {{
              autoResize: true,
              physics: {{
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                  gravitationalConstant: -40,
                  centralGravity: 0.04,
                  springLength: 130,
                  springConstant: 0.06,
                  damping: 0.5,
                  avoidOverlap: 0.35
                }},
                stabilization: {{
                  enabled: true,
                  iterations: 90,
                  updateInterval: 25
                }}
              }},
              interaction: {{
                hover: true,
                tooltipDelay: 100,
                zoomView: true,
                dragView: true
              }}
            }};

            network = new vis.Network(container, data, options);

            // Center and fit on stabilization
            network.once('stabilizationIterationsDone', function() {{
                network.fit({{ animation: false }});
            }});

            network.once('stabilized', function() {{
                fitCenter();
            }});

            // Fallback timers to ensure centered alignment after browser layout
            setTimeout(function() {{
                if (network) network.fit({{ animation: false }});
            }}, 120);

            setTimeout(function() {{
                if (network) fitCenter();
            }}, 500);

            window.addEventListener('resize', function() {{
                if (network) network.fit({{ animation: false }});
            }});

        }} catch(e) {{
            document.getElementById('network').innerHTML = '<div style="padding:40px;text-align:center;color:#6E7282;">Interactive graph rendering (requires network connection to Vis.js CDN).</div>';
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=620, scrolling=False)


def render_recommendation_card(rec: MovieRecommendation) -> None:
    """Renders a single pastel recommendation card."""
    palette_styles = {
        "lavender": {"bg": "#F5F2FA", "border": "#B4A7D6", "text": "#53457A"},
        "sage": {"bg": "#F2F6F0", "border": "#A3B899", "text": "#38522E"},
        "peach": {"bg": "#FAF2EC", "border": "#F7D1BA", "text": "#8C4724"},
        "powder_blue": {"bg": "#F0F6FA", "border": "#B8D8E8", "text": "#245472"},
    }
    style = palette_styles.get(rec.palette_tone, palette_styles["lavender"])

    reasons_html = ""
    for r in rec.reasons:
        reasons_html += f'<li style="margin-bottom: 4px; font-size: 0.9rem; color: #2D3142;">{r}</li>'

    card_html = f"""
    <div style="background-color: {style['bg']}; border: 1.5px solid {style['border']}; border-radius: 18px; padding: 20px; margin-bottom: 18px; box-shadow: 0 4px 14px rgba(45, 49, 66, 0.04); transition: transform 0.2s ease;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
                <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.3rem; font-weight: 700; color: #2D3142; margin: 0;">
                    {rec.title}
                </h3>
                <div style="font-size: 0.85rem; color: #6E7282; font-weight: 500;">
                    {f"Released: {rec.released} • " if rec.released else ""}{f"<em>'{rec.tagline}'</em>" if rec.tagline else "TMDB Verified Connection"}
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.8); border: 1px solid {style['border']}; padding: 4px 12px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700; color: {style['text']};">
                Graph Score: +{rec.score}
            </div>
        </div>

        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(0, 0, 0, 0.06);">
            <div style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; color: {style['text']}; text-transform: uppercase; margin-bottom: 6px;">
                Why Recommended (Graph Grounding)
            </div>
            <ul style="margin: 0; padding-left: 18px;">
                {reasons_html}
            </ul>
        </div>
    </div>
    """
    st.html(textwrap.dedent(card_html))


def render_graph_explorer_view(movie_title: str, movie_data: Dict[str, Any]) -> None:
    """Renders a relationship map showing Movie -> Directors -> Actors -> Connections."""
    directors = movie_data.get("directors", [])
    actors = [a["name"] for a in movie_data.get("actors", [])]
    rel_year = movie_data.get("released", "")
    rel_text = f"Released: {rel_year} • " if rel_year else ""
    tag_text = f'Tagline: "{movie_data.get("tagline", "")}"' if movie_data.get("tagline") else "TMDB 5000 Movie Node"

    # Director nodes
    dir_nodes_html = "".join([
        f'<div class="badge-pill badge-lavender" style="font-size: 0.9rem; padding: 8px 16px;">🎬 Director: <strong>{d}</strong></div>'
        for d in directors
    ])

    # Display up to 24 actors cleanly
    displayed_actors = actors[:24]
    actor_pills = [
        f'<div class="badge-pill badge-sage" style="font-size: 0.9rem; padding: 8px 16px;">👤 Actor: <strong>{a}</strong></div>'
        for a in displayed_actors
    ]
    if len(actors) > 24:
        actor_pills.append(
            f'<div class="badge-pill badge-sage" style="font-size: 0.9rem; padding: 8px 16px; opacity: 0.85;">👤 <em>+ {len(actors) - 24} more cast members in graph</em></div>'
        )
    actor_nodes_html = "".join(actor_pills)

    diagram_html = f"""
    <div class="stitch-card" style="padding: 30px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="display: inline-block; background: #FAF8F5; border: 2px solid #B4A7D6; border-radius: 24px; padding: 16px 32px; box-shadow: var(--shadow-pastel);">
                <div style="font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; color: #635882; text-transform: uppercase;">Central Movie Node</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #2D3142;">{movie_title}</div>
                <div style="font-size: 0.85rem; color: #6E7282;">{rel_text}{tag_text}</div>
            </div>
        </div>

        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="width: 2px; height: 30px; background: #B4A7D6;"></div>
        </div>

        <div style="background: #FDF3ED; border: 1px solid #F7D1BA; border-radius: 16px; padding: 18px; margin-bottom: 24px;">
            <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; color: #8C4724; text-transform: uppercase; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                <span>[:DIRECTED]</span> Relationship (Filmmakers)
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {dir_nodes_html if dir_nodes_html else '<span style="color: #6E7282;">No directors recorded.</span>'}
            </div>
        </div>

        <div style="background: #EEF7FC; border: 1px solid #B8D8E8; border-radius: 16px; padding: 18px;">
            <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; color: #245472; text-transform: uppercase; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                <span>[:ACTED_IN]</span> Relationship (Cast Members - {len(actors)} total)
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {actor_nodes_html if actor_nodes_html else '<span style="color: #6E7282;">No actors recorded.</span>'}
            </div>
        </div>
    </div>
    """
    st.html(textwrap.dedent(diagram_html))


def render_pipeline_architecture() -> None:
    """Renders the step-by-step visual RAG pipeline cards for the About tab."""
    steps = [
        ("1", "User Question", "Natural language inquiry from user", "💬"),
        ("2", "Query Classifier", "Identifies intent & extracts movie/actor entities", "🧠"),
        ("3", "Cypher Engine", "Generates safe, parameterized read-only graph queries", "🛡️"),
        ("4", "Neo4j Retrieval", "Pulls factual subgraphs & relational connections", "🕸️"),
        ("5", "Context Builder", "Structures retrieved facts into strict prompt payload", "📋"),
        ("6", "LLM Grounding", "Generates natural language strictly bound to graph facts", "✨"),
    ]

    cards_html = ""
    for num, title, desc, icon in steps:
        cards_html += f"""
        <div style="background: #FFFFFF; border: 1px solid #E8E5DF; border-radius: 16px; padding: 16px; min-width: 150px; flex: 1; box-shadow: var(--shadow-subtle);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <span style="font-size: 0.75rem; font-weight: 800; color: #53457A; background: #EFEAF7; padding: 2px 8px; border-radius: 9999px;">Step {num}</span>
            </div>
            <div style="font-weight: 700; font-size: 0.95rem; color: #2D3142; margin-bottom: 4px;">{title}</div>
            <div style="font-size: 0.8rem; color: #6E7282; line-height: 1.4;">{desc}</div>
        </div>
        """

    pipeline_html = f"""
    <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 28px;">
        {cards_html}
    </div>
    """
    st.html(textwrap.dedent(pipeline_html))
