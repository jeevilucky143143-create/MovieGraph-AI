# MovieGraph RAG – Explainable Movie Discovery and Recommendation Assistant

> **A modern, explainable AI assistant that answers movie questions and discovers recommendations grounded in the Neo4j Movies Knowledge Graph.**

---

## 1. Project Overview
- **Project Title:** MovieGraph RAG – Explainable Movie Discovery and Recommendation Assistant
- **Domain:** Artificial Intelligence, Knowledge Graphs, Graph Databases, Retrieval-Augmented Generation (RAG)
- **Frontend Design System:** STITCH Pastel Visual System (Warm Ivory `#FAF8F5`, Soft Charcoal `#2D3142`, Dusty Lavender `#B4A7D6`, Muted Sage `#A3B899`)

---

## 2. Problem Statement
Users searching for movies or asking AI about cinematic trivia frequently encounter two major issues:
1. **Opaque Recommendations:** Recommenders provide suggestions without explaining *why* films are related.
2. **AI Hallucinations:** Large Language Models (LLMs) frequently generate incorrect facts (e.g., wrong release years, non-existent directors, or fabricated cast members) because they rely on statistical language generation rather than verified knowledge bases.

---

## 3. Objective
To build an explainable, production-ready Graph RAG application that:
- Uses the **Neo4j Movies Knowledge Graph** as an immutable source of factual truth.
- Converts natural-language user questions into safe, parameterized Cypher queries.
- Grounds LLM responses strictly in retrieved graph data, eliminating hallucination.
- Provides multi-hop, graph-backed movie recommendations with clear, factual explanations.
- Delivers a unique, modern pastel user interface created in STITCH and implemented in Streamlit.

---

## 4. Real-World Use Case
- **Streaming Platforms:** Providing transparent "Because you liked X" recommendations grounded in shared actors, directors, or producers.
- **Cinematic Knowledge Portals:** Allowing film scholars and movie lovers to query actor-director networks intuitively using natural language.
- **Academic Research:** Demonstrating Graph RAG architecture and explainable AI in computer science curricula.

---

## 5. Core Features
- **Movie Question Answering:** Ask natural-language questions like *"Who directed The Matrix?"*, *"Who acted in The Matrix?"*, or *"When was The Matrix released?"*.
- **Actor & Director Discovery:** Explore filmographies, e.g., *"What movies did Tom Hanks act in?"*.
- **Explainable Recommendations:** Discovers movies via shared actors, same director, or multi-factor graph connectivity with exact reasons.
- **Graph Explorer:** Visualizes relationships ($Movie \rightarrow Director \rightarrow Actors \rightarrow Connected Movies$) using pastel node pills.
- **Zero Hallucination Guardrails:** If the knowledge graph lacks data for an unknown movie, the system refuses to invent facts.
- **Complete Provenance:** Every answer includes an expandable drawer showing the exact Cypher query, execution time, and raw records retrieved from Neo4j.
- **Resilient Architecture:** Runs against live Neo4j Desktop / Neo4j AuraDB, and includes an offline canonical graph fallback so the app never crashes during evaluations.

---

## 6. Technology Stack
- **Backend:** Python 3.9+
- **Graph Database:** Neo4j (Neo4j Desktop or AuraDB)
- **Database Driver:** Official Neo4j Python Driver (`neo4j` 5.x)
- **Frontend Framework:** Streamlit (customized with Stitch CSS)
- **UI Design System:** STITCH by Google
- **LLM Integrations:** Google Gemini API (`google-genai` / `google-generativeai`), OpenAI SDK
- **Testing Framework:** `pytest`
- **Environment Management:** `python-dotenv`

---

## 7. System Architecture
```
[User Question]
      │
      ▼
[Streamlit Web UI (Stitch Pastel Design)]
      │
      ▼
[Question Understanding & Query Classifier]
  ├── Intent Detection (10 Cypher query types)
  └── Entity Extraction (Movie titles, Actor/Director names)
      │
      ▼
[Safe Cypher Template Engine]
  └── Parameterized Read-Only Statements ($title, $name)
      │
      ▼
[Neo4j Knowledge Graph Client]
  ├── Live Neo4j Database (Desktop / AuraDB)
  └── Canonical In-Memory Movies Graph (Offline Fallback)
      │
      ▼
[Retrieved Knowledge Records]
      │
      ▼
[Context Builder]
  ├── Assembles Structured Factual Context
  └── Generates UI Entity Badges
      │
      ▼
[LLM Grounding Service (Gemini / OpenAI / Deterministic Engine)]
  └── Strict System Prompt: Answer ONLY from context; zero hallucination
      │
      ▼
[Grounded Answer + Cypher Provenance + Recommendation Cards]
```

---

## 8. Neo4j Movie Graph Schema
- **Nodes:**
  - `:Movie` (`title`, `released`, `tagline`)
  - `:Person` (`name`, `born`)
- **Relationships:**
  - `(:Person)-[:ACTED_IN {roles: []}]->(:Movie)`
  - `(:Person)-[:DIRECTED]->(:Movie)`
  - `(:Person)-[:PRODUCED]->(:Movie)`
  - `(:Person)-[:WROTE]->(:Movie)`

---

## 9. Project Directory Structure
```
moviegraph-rag/
│
├── app.py                      # Main Streamlit web application
├── config.py                   # Centralized configuration & environment loader
├── run.sh                      # Executable one-command run script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .env                        # Active environment configuration
├── .gitignore                  # Git ignore rules
│
├── database/
│   ├── __init__.py
│   └── neo4j_client.py         # Thread-safe Neo4j client with fallback resolver
│
├── data/
│   ├── movies_dataset.cypher   # Full Cypher import script for Neo4j
│   ├── load_data.py            # CLI script to load dataset into Neo4j
│   └── movies_data.py          # Structured in-memory graph representation
│
├── rag/
│   ├── __init__.py
│   ├── cypher_templates.py     # 10 safe read-only Cypher query templates
│   ├── query_classifier.py     # Intent classification & entity extraction
│   ├── retriever.py            # Executes Cypher & formats retrieval metrics
│   ├── context_builder.py      # Transforms graph records into LLM context
│   └── rag_pipeline.py         # End-to-end RAG workflow coordinator
│
├── llm/
│   ├── __init__.py
│   └── llm_service.py          # Grounded LLM service (Gemini, OpenAI, Fallback)
│
├── recommendation/
│   ├── __init__.py
│   └── recommender.py          # Explainable graph-based recommendation engine
│
├── ui/
│   ├── __init__.py
│   ├── stitch_theme.py         # STITCH pastel CSS styling tokens
│   └── components.py           # Reusable HTML/CSS components (cards, badges, SVG)
│
├── tests/
│   ├── __init__.py
│   ├── test_queries.py         # Tests Cypher templates & security injection blocking
│   ├── test_classifier.py      # Tests query classification & entity extraction
│   ├── test_retriever.py       # Tests graph retrieval & context building
│   ├── test_recommendations.py # Tests recommendation scoring & reason generation
│   └── test_grounding.py       # Verifies zero-hallucination guardrails
│
└── docs/
    ├── report.md               # 25-section academic project report
    ├── architecture.md         # System architecture & Mermaid sequence diagrams
    ├── schema.md               # Knowledge graph schema documentation
    └── viva_questions.md       # 25 viva questions and answers for evaluations
```

---

## 10. Installation Guide

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Optional: Neo4j Desktop or Neo4j AuraDB (app runs out-of-the-box with built-in graph fallback)

### Step 1: Clone or Navigate to Directory
```bash
cd /Users/jeevithal/Desktop/movie
```

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

---

## 11. Neo4j Setup (Optional for Live Database)

If you have Neo4j Desktop or Neo4j AuraDB:
1. Start your database instance.
2. In Neo4j Browser or via our automated importer, run:
   ```bash
   python3 data/load_data.py
   ```
3. Verify that 171 nodes are created:
   ```cypher
   MATCH (n) RETURN count(n);
   ```

*Note: If Neo4j is not running, the application automatically uses the canonical in-memory Movies dataset, so you can test and demonstrate immediately without waiting for a database server.*

---

## 12. Environment Variables Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```ini
# Neo4j Settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# LLM Settings (optional: Gemini or OpenAI)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 13. Running the Application

### Option A: Using the Runner Script
```bash
chmod +x run.sh
./run.sh
```

### Option B: Running via Streamlit Directly
```bash
streamlit run app.py
```
Open your browser at: **`http://localhost:8501`**

---

## 14. Demo Walkthrough Scenario (3-Minute Presentation)

1. **Step 1: Open Application**
   - Observe the Stitch pastel aesthetic (Warm Ivory `#FAF8F5`, Soft Charcoal, Dusty Lavender, Muted Sage).
   - Check the top navbar status pill: `● Neo4j Connected` or `● Knowledge Graph Active`.
2. **Step 2: Ask a Direct Question**
   - Click the suggestion chip: **"Who directed The Matrix?"**
   - Observe the answer: *"The Matrix was directed by Lana Wachowski and Lilly Wachowski."*
   - Note the **Knowledge Found** badges: `The Matrix (1999)`, `Director: Lana Wachowski`, `Director: Lilly Wachowski`.
   - Expand **"See how MovieGraph found this"** to show the live Cypher query and execution latency.
3. **Step 3: Ask Cast Trivia**
   - Click: **"Who acted in The Matrix?"**
   - See the cast list (Keanu Reeves, Carrie-Anne Moss, Laurence Fishburne, Hugo Weaving) with roles.
4. **Step 4: Filmography Query**
   - Type or click: **"What movies did Tom Hanks act in?"**
   - View Tom Hanks' filmography retrieved from Neo4j.
5. **Step 5: Explainable Recommendations**
   - Navigate to the **"Discover Recommendations"** tab.
   - Select movie: `The Matrix`.
   - Mode: `Graph-based Discovery`.
   - Click **Generate Explainable Recommendations**.
   - Notice recommendations like *The Matrix Reloaded* and *The Devil's Advocate* with explicit graph reasons: *"Shares actor Keanu Reeves"*.
6. **Step 6: Graph Explorer**
   - Navigate to **"Graph Explorer"**.
   - Inspect the interactive node relationship diagram connecting the Movie node to Directors and Cast.
7. **Step 7: About Tab & Viva Prep**
   - Review the step-by-step visual RAG pipeline cards and viva questions.

---

## 15. Running the Test Suite
Execute the automated test suite with `pytest`:
```bash
python3 -m pytest tests/ -v
```
All 17 tests validate Cypher template safety, intent classification, entity extraction, recommendation scoring, and anti-hallucination guardrails.

---

## 16. Academic Project Compliance
- [x] Canonical Neo4j Movies dataset supported (171 nodes/relationships).
- [x] 10 safe read-only Cypher query templates.
- [x] End-to-end RAG architecture with LLM grounding.
- [x] Zero-hallucination protection when graph context is empty.
- [x] Multi-factor explainable recommendation algorithm.
- [x] Stitch-designed modern pastel UI in Streamlit.
- [x] Complete college project report (`docs/report.md`).
- [x] System architecture document (`docs/architecture.md`).
- [x] Graph schema document (`docs/schema.md`).
- [x] 25 viva voce questions and answers (`docs/viva_questions.md`).

---

## 17. Conclusion
MovieGraph RAG successfully integrates Graph Databases and Large Language Models, solving the real-world problem of opaque recommendations and generative AI hallucinations through deterministic, verifiable knowledge graph grounding.
