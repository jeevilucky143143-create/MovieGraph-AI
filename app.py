"""MovieGraph AI - Modern Cinematic Discovery & Graph-RAG Assistant.

A realistic, production-grade Web Application powered by:
- TMDb 5000 / Neo4j Knowledge Graph (4,800+ films, 63,800+ people, 135,000+ edges)
- Strict Anti-Hallucination Retrieval-Augmented Generation (RAG)
- Interactive Prompt Studio with 4 AI Personas (Scholar, Buddy, Critic, Producer)
- Six Degrees of Film (Breadth-First Search shortest pathfinder)
- Embedded Interactive Force-Directed Physics Graph (Vis.js Canvas)
- Movie Head-to-Head Comparative Graph Analytics
- Stitch Pastel Design System
"""

import time
import streamlit as st
from config import Config
from database.neo4j_client import Neo4jClient
from rag.rag_pipeline import RAGPipeline
from recommendation.recommender import MovieRecommender
from recommendation.graph_analytics import GraphAnalytics
from data.movies_data import get_all_movie_titles, get_all_person_names, MOVIES, PERSONS
from ui.stitch_theme import get_stitch_css
from ui.components import (
    render_navbar,
    render_hero_header,
    render_answer_card,
    render_recommendation_card,
    render_graph_explorer_view,
    render_interactive_network_graph,
    render_connection_path,
    render_movie_comparison,
    render_pipeline_architecture,
)

# Page configuration
st.set_page_config(
    page_title="MovieGraph AI – Cinematic Knowledge Graph & Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply Stitch Pastel Design System CSS
st.html(get_stitch_css())


@st.cache_resource
def get_system_services():
    """Initializes and caches singleton graph services."""
    client = Neo4jClient()
    pipeline = RAGPipeline(neo4j_client=client)
    recommender = MovieRecommender(neo4j_client=client)
    analytics = GraphAnalytics()
    return client, pipeline, recommender, analytics


# Initialize services
client, pipeline, recommender, analytics = get_system_services()
db_status = client.verify_connectivity()

# Render Top Navigation & Live Ticker
render_navbar(db_status)

# Session state initialization
if "search_input_text" not in st.session_state:
    st.session_state.search_input_text = ""
if "active_answer" not in st.session_state:
    st.session_state.active_answer = None
if "execute_query" not in st.session_state:
    st.session_state.execute_query = None
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = "Cinematic Scholar"
if "selected_output_style" not in st.session_state:
    st.session_state.selected_output_style = "Concise Narrative"
if "query_history" not in st.session_state:
    st.session_state.query_history = []

movie_list = get_all_movie_titles()

# Main Navigation Tabs
tab_ask, tab_discover, tab_graph, tab_degrees, tab_compare, tab_about = st.tabs([
    "💬 Prompt Studio & AI",
    "✨ Recommendations",
    "🌐 Interactive Graph Explorer",
    "🔗 Six Degrees of Film",
    "⚖️ Movie Comparison",
    "📖 System Architecture",
])

# -----------------------------------------------------------------------------
# TAB 1: PROMPT STUDIO & AI ASSISTANT
# -----------------------------------------------------------------------------
with tab_ask:
    render_hero_header()

    # Prompt Studio Control Panel (Persona & Formatting Controls)
    with st.container():
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #E8E5DF; border-radius: 18px; padding: 14px 20px; margin-bottom: 20px; box-shadow: var(--shadow-subtle);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #53457A; text-transform: uppercase; letter-spacing: 0.06em; display: flex; align-items: center; gap: 6px;">
                    <span>🎛️</span> Prompt Studio & AI Persona Configurator
                </div>
                <div style="font-size: 0.78rem; color: #6E7282;">
                    Customize AI voice and intelligence structure while strictly preserving graph truth.
                </div>
            </div>
        </div>
        """)

        ctrl_col1, ctrl_col2 = st.columns([3, 2])
        with ctrl_col1:
            persona_choice = st.selectbox(
                "Select AI Persona Tone",
                options=[
                    "Cinematic Scholar",
                    "Casual Movie Buddy",
                    "Cannes Film Critic",
                    "Studio Producer",
                ],
                index=0,
                key="persona_select",
                help="Adapts the AI response tone while preserving strict factual grounding.",
            )

        with ctrl_col2:
            format_choice = st.selectbox(
                "Output Structure",
                options=[
                    "Concise Narrative",
                    "Bulleted Intelligence Brief",
                    "Detailed Analysis",
                ],
                index=0,
                key="format_select",
                help="Chooses between conversational narrative or structured bullet points.",
            )

        # Reactive adaptation: If an answer is currently displayed and the user changes
        # the persona or output format dropdown, immediately re-style the answer in real time!
        if st.session_state.get("active_answer"):
            curr_ans = st.session_state.active_answer
            if curr_ans.persona != persona_choice or curr_ans.output_style != format_choice:
                with st.spinner(f"Re-styling answer to {persona_choice} ({format_choice})..."):
                    st.session_state.active_answer = pipeline.run(
                        question=curr_ans.question,
                        persona=persona_choice,
                        output_style=format_choice,
                    )

    # Natural Language Search Input Form
    with st.form("ask_form", border=False):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input_val = st.text_input(
                "Search Input",
                value=st.session_state.get("search_input_text", ""),
                placeholder="Ask about any movie, actor, or director... (e.g. Who directed Avatar? or Who acted in Inception?)",
                label_visibility="collapsed",
                key="query_text_widget",
            )
        with col_btn:
            submit_btn = st.form_submit_button("Ask Graph AI", type="primary", use_container_width=True)

    # Inspiring Prompt Inspiration Library (Categorized Chips)
    st.html("""
    <div style="margin: 8px 0 12px 0;">
        <span style="font-size: 0.82rem; font-weight: 700; color: #6E7282; text-transform: uppercase; letter-spacing: 0.05em;">
            💡 Curated Prompt Inspiration Library
        </span>
    </div>
    """)

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        st.markdown("**🔍 Factual Trivia**")
        if st.button("Who directed Avatar?", key="p_fact_1", use_container_width=True):
            st.session_state.execute_query = "Who directed Avatar?"
            st.session_state.search_input_text = "Who directed Avatar?"
            st.rerun()
        if st.button("Who directed Inception?", key="p_fact_2", use_container_width=True):
            st.session_state.execute_query = "Who directed Inception?"
            st.session_state.search_input_text = "Who directed Inception?"
            st.rerun()

    with p_col2:
        st.markdown("**👥 Cast & Ensembles**")
        if st.button("Who acted in The Dark Knight?", key="p_cast_1", use_container_width=True):
            st.session_state.execute_query = "Who acted in The Dark Knight?"
            st.session_state.search_input_text = "Who acted in The Dark Knight?"
            st.rerun()
        if st.button("Who acted in The Matrix?", key="p_cast_2", use_container_width=True):
            st.session_state.execute_query = "Who acted in The Matrix?"
            st.session_state.search_input_text = "Who acted in The Matrix?"
            st.rerun()

    with p_col3:
        st.markdown("**🎬 Directorial Works**")
        if st.button("What movies did Christopher Nolan direct?", key="p_dir_1", use_container_width=True):
            st.session_state.execute_query = "What movies did Christopher Nolan direct?"
            st.session_state.search_input_text = "What movies did Christopher Nolan direct?"
            st.rerun()
        if st.button("What movies did Quentin Tarantino direct?", key="p_dir_2", use_container_width=True):
            st.session_state.execute_query = "What movies did Quentin Tarantino direct?"
            st.session_state.search_input_text = "What movies did Quentin Tarantino direct?"
            st.rerun()

    with p_col4:
        st.markdown("**💡 Recommendations**")
        if st.button("Recommend movies similar to Titanic", key="p_rec_1", use_container_width=True):
            st.session_state.execute_query = "Recommend movies similar to Titanic"
            st.session_state.search_input_text = "Recommend movies similar to Titanic"
            st.rerun()
        if st.button("Who directed The Quantum Paradox of 3025?", key="p_test_1", use_container_width=True):
            st.session_state.execute_query = "Who directed The Quantum Paradox of 3025?"
            st.session_state.search_input_text = "Who directed The Quantum Paradox of 3025?"
            st.rerun()

    # Determine query to execute
    query_to_run = None
    if submit_btn and user_input_val.strip():
        query_to_run = user_input_val.strip()
        st.session_state.search_input_text = query_to_run
    elif "execute_query" in st.session_state and st.session_state.execute_query:
        query_to_run = st.session_state.execute_query
        st.session_state.execute_query = None

    # Execute query when triggered
    if query_to_run:
        with st.spinner("Executing Cypher retrieval across knowledge graph..."):
            answer_response = pipeline.run(
                question=query_to_run,
                persona=persona_choice,
                output_style=format_choice,
            )
            st.session_state.active_answer = answer_response

            # Append to history
            if query_to_run not in [h["question"] for h in st.session_state.query_history]:
                st.session_state.query_history.insert(
                    0,
                    {
                        "question": query_to_run,
                        "persona": persona_choice,
                        "style": format_choice,
                        "time": time.strftime("%H:%M:%S"),
                        "records": answer_response.record_count,
                    },
                )
                if len(st.session_state.query_history) > 8:
                    st.session_state.query_history.pop()

    # Display Answer or Empty State
    if st.session_state.get("active_answer"):
        render_answer_card(st.session_state.active_answer)
    else:
        st.html("""
        <div style="text-align: center; padding: 48px 20px; background: #FFFFFF; border-radius: 20px; border: 1.5px dashed #E8E5DF; margin-top: 24px;">
            <div style="font-size: 2.8rem; margin-bottom: 12px;">🎬 ✨ 🕸️</div>
            <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.35rem; font-weight: 700; color: #2D3142; margin-bottom: 6px;">
                Ready to explore the movie graph.
            </h3>
            <p style="color: #6E7282; font-size: 0.98rem; max-width: 520px; margin: 0 auto;">
                Type any natural language inquiry above or click a prompt chip to experience grounded, hallucination-free knowledge retrieval.
            </p>
        </div>
        """)

    # Recent Query History
    if st.session_state.query_history:
        with st.expander("🕒 Recent Prompt History in this Session"):
            for h in st.session_state.query_history:
                col_h1, col_h2 = st.columns([5, 1])
                with col_h1:
                    st.markdown(f"**\"{h['question']}\"**  *(Persona: {h['persona']} • {h['records']} records • {h['time']})*")
                with col_h2:
                    if st.button("Re-run", key=f"rerun_{h['question']}_{h['time']}"):
                        st.session_state.execute_query = h["question"]
                        st.session_state.search_input_text = h["question"]
                        st.rerun()

# -----------------------------------------------------------------------------
# TAB 2: DISCOVER RECOMMENDATIONS
# -----------------------------------------------------------------------------
with tab_discover:
    st.html("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">
            Explainable Graph Recommendations
        </h2>
        <p style="color: #6E7282; font-size: 1.05rem;">
            Discover films connected through shared actors, common filmmakers, and verified multi-hop graph connectivity.
        </p>
    </div>
    """)

    rec_col1, rec_col2, rec_col3 = st.columns([3, 2, 1])
    with rec_col1:
        default_matrix_idx = movie_list.index("The Matrix") if "The Matrix" in movie_list else 0
        selected_movie = st.selectbox(
            "Select Base Movie",
            options=movie_list,
            index=default_matrix_idx,
            key="rec_movie_select",
        )
    with rec_col2:
        selected_mode = st.selectbox(
            "Recommendation Strategy",
            options=["Graph-based Discovery", "Shared Actors", "Same Director", "Connected Movies"],
            key="rec_mode_select",
        )
    with rec_col3:
        rec_limit = st.slider("Max Results", min_value=2, max_value=12, value=4, key="rec_limit_slider")

    # Persist recommendation results in session_state
    if "rec_results" not in st.session_state:
        st.session_state.rec_results = recommender.recommend(
            movie_title=selected_movie,
            mode=selected_mode,
            limit=rec_limit,
        )
        st.session_state.rec_base_movie = selected_movie

    if st.button("Generate Explainable Recommendations", type="primary", use_container_width=True):
        with st.spinner("Analyzing graph connection paths..."):
            st.session_state.rec_results = recommender.recommend(
                movie_title=selected_movie,
                mode=selected_mode,
                limit=rec_limit,
            )
            st.session_state.rec_base_movie = selected_movie

    current_recs = st.session_state.get("rec_results", [])
    current_movie = st.session_state.get("rec_base_movie", selected_movie)

    if current_recs:
        st.html(f"""
        <div style="margin: 28px 0 16px 0;">
            <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.35rem; font-weight: 800; color: #2D3142; margin: 0;">
                Found {len(current_recs)} Graph Recommendations for <span style="color: #53457A; font-style: italic;">{current_movie}</span>:
            </h3>
        </div>
        """)
        for rec in current_recs:
            render_recommendation_card(rec)
    else:
        st.info(f"No direct connections found for '{current_movie}' with mode '{selected_mode}'. Try 'Graph-based Discovery'.")

# -----------------------------------------------------------------------------
# TAB 3: INTERACTIVE GRAPH EXPLORER (DUAL VIEW: CANVAS + HIERARCHICAL)
# -----------------------------------------------------------------------------
with tab_graph:
    st.html("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">
            Interactive Knowledge Graph Neighborhood
        </h2>
        <p style="color: #6E7282; font-size: 1.05rem;">
            Explore node neighborhoods with real-time physics simulation or structured hierarchical pills.
        </p>
    </div>
    """)

    explorer_col1, explorer_col2 = st.columns([3, 2])
    with explorer_col1:
        target_explore_movie = st.selectbox(
            "Select Film to Inspect",
            options=movie_list,
            index=movie_list.index("Inception") if "Inception" in movie_list else 0,
            key="explorer_select",
        )
    with explorer_col2:
        view_type = st.radio(
            "Graph View Mode",
            options=["🔮 Physics Force-Directed Network", "📋 Pastel Relationship Cards"],
            horizontal=True,
            key="graph_view_toggle",
        )

    if target_explore_movie in MOVIES:
        m_info = MOVIES[target_explore_movie]

        if "Physics" in view_type:
            # Interactive D3/Vis.js Canvas
            net_data = analytics.generate_vis_network_data(target_explore_movie, max_actors=18)
            render_interactive_network_graph(target_explore_movie, net_data)
        else:
            # Pastel Hierarchical Card View
            render_graph_explorer_view(target_explore_movie, m_info)

        # Tabular Details
        with st.expander("📊 View Node & Relationship Table"):
            year_val = m_info['released'] if m_info.get('released') else 'N/A'
            tag_val = m_info.get('tagline') if m_info.get('tagline') else 'N/A'
            st.markdown(f"**Movie Properties:** Title: `{m_info['title']}`, Year: `{year_val}`, Tagline: `{tag_val}`")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("**[:DIRECTED] Relationships:**")
                st.table([{"Director": d} for d in m_info.get("directors", [])])
            with col_t2:
                st.markdown("**[:ACTED_IN] Relationships:**")
                st.table([{"Actor": a["name"], "Roles": ", ".join(a["roles"])} for a in m_info.get("actors", [])[:20]])

# -----------------------------------------------------------------------------
# TAB 4: SIX DEGREES OF FILM (BACON NUMBER PATH FINDER)
# -----------------------------------------------------------------------------
with tab_degrees:
    st.html("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">
            Six Degrees of Film (Pathfinder)
        </h2>
        <p style="color: #6E7282; font-size: 1.05rem;">
            Trace the shortest graph path connecting any two actors or directors across 135,000+ relationships.
        </p>
    </div>
    """)

    # Top credited actors/directors for quick selection
    popular_people = [
        "Keanu Reeves",
        "Leonardo DiCaprio",
        "Tom Hanks",
        "Christopher Nolan",
        "Quentin Tarantino",
        "Steven Spielberg",
        "Brad Pitt",
        "Scarlett Johansson",
        "Morgan Freeman",
        "Robert De Niro",
        "Al Pacino",
        "Matt Damon",
        "Christian Bale",
        "Samuel L. Jackson",
        "James Cameron",
        "Kate Winslet",
        "Johnny Depp",
        "Tom Cruise",
    ]

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        p1_mode = st.radio("Person A Selection", ["Popular Star", "Custom Name"], horizontal=True, key="p1_mode")
        if p1_mode == "Popular Star":
            p1_val = st.selectbox("Starting Person", options=popular_people, index=0, key="p1_select")
        else:
            p1_val = st.text_input("Enter Starting Person Name", value="Keanu Reeves", key="p1_custom")

    with p_col2:
        p2_mode = st.radio("Person B Selection", ["Popular Star", "Custom Name"], horizontal=True, key="p2_mode")
        if p2_mode == "Popular Star":
            p2_val = st.selectbox("Target Person", options=popular_people, index=1, key="p2_select")
        else:
            p2_val = st.text_input("Enter Target Person Name", value="Leonardo DiCaprio", key="p2_custom")

    if st.button("Trace Graph Connection Path", type="primary", use_container_width=True):
        with st.spinner(f"Computing shortest BFS path between {p1_val} and {p2_val}..."):
            path, dur_ms = analytics.find_shortest_path(p1_val, p2_val)
            render_connection_path(path, dur_ms)

# -----------------------------------------------------------------------------
# TAB 5: MOVIE HEAD-TO-HEAD COMPARISON
# -----------------------------------------------------------------------------
with tab_compare:
    st.html("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">
            Movie Head-to-Head Comparison
        </h2>
        <p style="color: #6E7282; font-size: 1.05rem;">
            Compare two movies across shared cast, common directors, and graph affinity score.
        </p>
    </div>
    """)

    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        movie_a = st.selectbox("First Movie", options=movie_list, index=movie_list.index("The Matrix") if "The Matrix" in movie_list else 0, key="cmp_m1")
    with cmp_col2:
        default_m2_idx = movie_list.index("Inception") if "Inception" in movie_list else 1
        movie_b = st.selectbox("Second Movie", options=movie_list, index=default_m2_idx, key="cmp_m2")

    if st.button("Run Deep Graph Comparison", type="primary", use_container_width=True):
        with st.spinner("Analyzing graph overlap..."):
            comp_res = analytics.compare_movies(movie_a, movie_b)
            if comp_res:
                render_movie_comparison(comp_res)
            else:
                st.warning("Could not compare selected titles.")

# -----------------------------------------------------------------------------
# TAB 6: SYSTEM ARCHITECTURE & DESIGN
# -----------------------------------------------------------------------------
with tab_about:
    st.html("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">
            System Architecture & Technical Specifications
        </h2>
        <p style="color: #6E7282; font-size: 1.05rem;">
            Enterprise Graph-RAG pipeline architecture, relationship semantics, and explainable AI proofs.
        </p>
    </div>
    """)

    # Visual Flowchart
    render_pipeline_architecture()

    # System Highlights
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("""
        ### 🕸️ Why Knowledge Graph over SQL?
        Traditional relational databases (SQL) require multi-table `JOIN` operations across `actors`, `castings`, and `directors` tables that scale exponentially with traversal depth ($O(N^k)$).
        
        In the **Neo4j Knowledge Graph**, relationships are stored as direct memory pointers. Traversing from *Movie* to *Actors* to *Connected Films* executes in $O(1)$ constant time per hop, enabling instant real-time multi-hop recommendations.
        """)

    with col_a2:
        st.markdown("""
        ### 🛡️ Why Graph RAG over Naive LLM?
        Generic LLMs generate text by predicting statistical next tokens. When queried about specialized cinematic trivia, release years, or cast lists, they frequently **hallucinate** facts.
        
        **MovieGraph RAG** retrieves the ground-truth subgraph via parameterized read-only Cypher queries and injects it into prompt context. If zero records exist, the system strictly refuses to invent facts.
        """)

    st.markdown("---")
    st.markdown("### ⚙️ Engine Specifications & System Benchmarks")

    spec_col1, spec_col2, spec_col3 = st.columns(3)
    with spec_col1:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #E8E5DF; border-radius: 14px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="font-size: 0.8rem; font-weight: 800; color: #53457A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                Storage & Retrieval
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">Neo4j 5.x / Hybrid Cache</div>
            <div style="font-size: 0.88rem; color: #6E7282; line-height: 1.45;">
                Index-free adjacency graph storage with automatic sub-millisecond memory fallback during offline demonstrations.
            </div>
        </div>
        """)
    with spec_col2:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #E8E5DF; border-radius: 14px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="font-size: 0.8rem; font-weight: 800; color: #53457A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                Traversal Engine
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">Bidirectional BFS</div>
            <div style="font-size: 0.88rem; color: #6E7282; line-height: 1.45;">
                Shortest pathfinder guaranteeing exact minimum degrees of separation across 135,000+ edge connections.
            </div>
        </div>
        """)
    with spec_col3:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #E8E5DF; border-radius: 14px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="font-size: 0.8rem; font-weight: 800; color: #53457A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                Safety & Integrity
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #2D3142; margin-bottom: 6px;">Strict Read-Only</div>
            <div style="font-size: 0.88rem; color: #6E7282; line-height: 1.45;">
                Parameterized Cypher execution blocking destructive write operations (<code>CREATE</code>, <code>DELETE</code>, <code>MERGE</code>).
            </div>
        </div>
        """)
