# Academic Viva Voce – Questions & Answers

**Project:** MovieGraph RAG – Explainable Movie Discovery and Recommendation Assistant  
**Subject Areas:** Knowledge Graphs, Neo4j, Cypher, Natural Language Processing, RAG, Web Applications  

---

### Q1: What is Neo4j?
**Answer:** Neo4j is an open-source, highly scalable graph database management system. Unlike relational databases that store records in tables with rows and columns, Neo4j natively stores data as a network of nodes, relationships, and properties.

---

### Q2: What is a Knowledge Graph?
**Answer:** A Knowledge Graph is a structured representation of real-world facts. Entities (such as people, places, or concepts) are represented as **nodes**, and the relationships connecting them are represented as directed, labeled **edges**. It allows systems to reason about connections rather than isolated data points.

---

### Q3: Why use Neo4j instead of a traditional SQL database?
**Answer:** In traditional SQL databases, connecting multiple entities (like finding all movies connected through common actors and directors) requires multiple, expensive table `JOIN` operations. In Neo4j, data uses **index-free adjacency**, meaning nodes store physical direct pointers to adjacent nodes. Graph traversals occur in constant $O(1)$ time per hop, making multi-hop discovery significantly faster.

---

### Q4: What is Cypher?
**Answer:** Cypher is Neo4j's declarative graph query language. It uses ASCII-art syntax to represent visual graph patterns. For example, `(m:Movie)<-[:ACTED_IN]-(p:Person)` clearly describes an actor connected to a movie.

---

### Q5: What is RAG (Retrieval-Augmented Generation)?
**Answer:** RAG is an AI architecture that combines an information retrieval system with a generative Large Language Model. Instead of asking an LLM to answer purely from memory, RAG first retrieves relevant factual documents or database records, injects them into the prompt as context, and instructs the LLM to formulate its answer based strictly on that retrieved data.

---

### Q6: Why use RAG instead of just prompting a Large Language Model?
**Answer:** Standalone LLMs suffer from **hallucinations** (generating false or unverifiable facts), lack access to private or proprietary data, and can have outdated knowledge. RAG grounds the model in real-time, verified database records, making the answers accurate and explainable.

---

### Q7: What is an LLM (Large Language Model)?
**Answer:** An LLM is a deep neural network (typically based on the Transformer architecture) trained on vast amounts of text to understand, summarize, and generate human-like natural language. Examples include Google Gemini and OpenAI GPT-4.

---

### Q8: Why combine Neo4j with an LLM?
**Answer:** LLMs excel at language fluency, conversational nuance, and flexible interaction, but are poor at deterministic factual reasoning. Neo4j excels at strict, verified, relational data storage and path traversal. Combining them allows the LLM to act as the conversational interface while Neo4j acts as the factual source of truth.

---

### Q9: How does the Question-to-Cypher workflow operate in your project?
**Answer:** When a user asks a question, our `QueryClassifier` determines the intent (e.g., `movie_director`) and extracts entity names (e.g., `"The Matrix"`). It then maps this intent to a predefined, parameterized Cypher template (e.g., `MATCH (m:Movie {title: $title})<-[:DIRECTED]-(p:Person)...`) and safely binds the parameters, eliminating injection risks.

---

### Q10: How does MovieGraph AI eliminate hallucinations?
**Answer:** We enforce two strict guardrails:
1. **Prompt Constraints:** The LLM is explicitly instructed to answer *only* using the retrieved Neo4j context and never invent external facts.
2. **Sentinel Detection:** If Neo4j returns zero records, the pipeline injects `NO_DATA_FOUND` and immediately returns: *"I couldn't find that information in the movie knowledge graph,"* preventing the LLM from fabricating an answer.

---

### Q11: What is a Node in Neo4j?
**Answer:** A node represents a discrete entity or object in the graph. In our dataset, there are two primary node labels: `:Movie` (representing films) and `:Person` (representing actors, directors, screenwriters, and producers).

---

### Q12: What is a Relationship in Neo4j?
**Answer:** A relationship connects two nodes and must have a name, a direction, and a start/end node. Relationships can also hold properties (like character role names in `:ACTED_IN`).

---

### Q13: What does the `:ACTED_IN` relationship represent?
**Answer:** It links a `:Person` node to a `:Movie` node indicating acting performance, storing an array of character roles played (e.g., `roles: ['Neo']`).

---

### Q14: What does the `:DIRECTED` relationship represent?
**Answer:** It connects a `:Person` node to a `:Movie` node, indicating that the individual directed the film.

---

### Q15: How does your graph-based recommendation algorithm work?
**Answer:** Recommendations are generated by traversing paths between movies in Neo4j. If two movies share actors (`:ACTED_IN`), each shared actor adds +2 points. If they share a director (`:DIRECTED`), it adds +3 points. The candidate movies are ranked by total graph score.

---

### Q16: Why are your recommendations considered "explainable"?
**Answer:** Unlike collaborative filtering or deep learning embeddings that produce opaque numbers, our system directly explains the graph path: *"Recommended because it shares 2 actors with The Matrix (Keanu Reeves, Laurence Fishburne)."*

---

### Q17: What happens when an unknown movie is queried?
**Answer:** If the user asks about a movie not present in the graph (e.g., *"Who directed Interstellar?"*), the retriever returns zero records. The system cleanly reports that the film is absent from the knowledge graph without crashing or hallucinating.

---

### Q18: What security measures protect your database queries?
**Answer:** We reject Cypher string concatenation. All user inputs are passed through parameterized variables (`$title`, `$name`). Additionally, `Neo4jClient` validates every query against a regex blacklist of mutation keywords (`CREATE`, `DELETE`, `DROP`, `SET`, `MERGE`), ensuring purely read-only operations.

---

### Q19: Why was Streamlit chosen for the frontend?
**Answer:** Streamlit allows rapid, Python-native interactive web development without requiring heavy Node.js or React build pipelines. We extensively customized Streamlit using custom CSS to implement the Stitch pastel visual system.

---

### Q20: What are the primary limitations of the current implementation?
**Answer:** The current system uses the standard Neo4j Movies dataset (~171 nodes and relationships), which focuses on iconic classic films. It does not yet contain the entire global IMDb catalog.

---

### Q21: How could the system be enhanced in the future?
**Answer:** 
1. Integrating vector embeddings to support semantic hybrid graph retrieval.
2. Ingesting millions of titles from the full TMDb/IMDb datasets.
3. Adding voice input and user rating personalization.

---

### Q22: What is the purpose of the fallback canonical graph in your project?
**Answer:** To ensure that the project is 100% stable and demonstrable even before Neo4j is started or if external credentials fail, our `Neo4jClient` automatically falls back to an in-memory representation of the exact same canonical Movies graph, ensuring zero crashes.

---

### Q23: How do you verify database connectivity?
**Answer:** The application runs `driver.verify_connectivity()` and checks node counts using `MATCH (m:Movie) RETURN count(m)`. This status is dynamically presented in the top navigation bar.

---

### Q24: What is the difference between Graph RAG and Vector RAG?
**Answer:** Vector RAG converts text chunks into high-dimensional vectors and retrieves documents via cosine similarity, which can miss structured relationship links. Graph RAG traverses explicit entity-relationship connections, providing deterministic precision for relational questions.

---

### Q25: Explain the complete end-to-end user query flow.
**Answer:** 
1. User enters natural language question.
2. `QueryClassifier` detects intent and extracts movie/person entities.
3. `GraphRetriever` selects a parameterized Cypher template and queries Neo4j.
4. `ContextBuilder` structures the returned records into factual text blocks.
5. `LLMService` prompts the LLM with strict grounding constraints.
6. Streamlit renders the natural-language answer, knowledge badges, database status, and Cypher trace.
