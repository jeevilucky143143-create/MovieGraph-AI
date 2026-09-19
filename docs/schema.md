# Neo4j Movies Knowledge Graph Schema

This document details the graph schema, node properties, relationship types, constraints, and representative Cypher queries used in **MovieGraph AI**.

---

## 1. Graph Data Model Overview

The Neo4j Movies Knowledge Graph represents entities as **Nodes** and connections as directed **Relationships**.

```mermaid
graph LR
    P[Person] -->|:ACTED_IN {roles: []}| M[Movie]
    P -->|:DIRECTED| M
    P -->|:PRODUCED| M
    P -->|:WROTE| M
```

---

## 2. Node Definitions

### 2.1 Movie Node (`:Movie`)
Represents a feature film in the database.

| Property | Data Type | Description | Example |
|---|---|---|---|
| `title` | STRING (Indexed / Unique) | Official film title | `"The Matrix"` |
| `released` | INTEGER | Year the film premiered | `1999` |
| `tagline` | STRING | Promotional tagline | `"Welcome to the Real World"` |

### 2.2 Person Node (`:Person`)
Represents an individual who worked in the film industry (actor, director, writer, producer).

| Property | Data Type | Description | Example |
|---|---|---|---|
| `name` | STRING (Indexed / Unique) | Full legal or stage name | `"Keanu Reeves"` |
| `born` | INTEGER (Optional) | Year of birth | `1964` |

---

## 3. Relationship Definitions

### 3.1 `:ACTED_IN`
Connects an actor (`:Person`) to a film (`:Movie`) in which they performed.

- **Direction:** `(Person)-[:ACTED_IN]->(Movie)`
- **Properties:**
  - `roles`: `LIST<STRING>` – Character name(s) portrayed by the actor (e.g., `['Neo']`).

### 3.2 `:DIRECTED`
Connects a director (`:Person`) to a film (`:Movie`) they helmed.

- **Direction:** `(Person)-[:DIRECTED]->(Movie)`
- **Properties:** None.

### 3.3 `:PRODUCED`
Connects an executive or film producer (`:Person`) to a film (`:Movie`).

- **Direction:** `(Person)-[:PRODUCED]->(Movie)`
- **Properties:** None.

### 3.4 `:WROTE`
Connects a screenwriter (`:Person`) to a film (`:Movie`).

- **Direction:** `(Person)-[:WROTE]->(Movie)`
- **Properties:** None.

---

## 4. Recommended Database Constraints & Indexes

To ensure optimal traversal performance and enforce data integrity in Neo4j, the following Cypher statements should be executed:

```cypher
// Ensure unique movie titles
CREATE CONSTRAINT movie_title_unique IF NOT EXISTS
FOR (m:Movie) REQUIRE m.title IS UNIQUE;

// Ensure unique person names
CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE;

// Index on release year for sorting
CREATE INDEX movie_released_idx IF NOT EXISTS
FOR (m:Movie) ON (m.released);
```

---

## 5. Representative Cypher Queries

### 5.1 Verification Queries
```cypher
// Verify total movie count
MATCH (m:Movie) RETURN count(m) AS movie_count;

// Verify total person count
MATCH (p:Person) RETURN count(p) AS person_count;

// Verify relationship distribution
MATCH ()-[r]->() RETURN type(r) AS relationship_type, count(r) AS total
ORDER BY total DESC;
```

### 5.2 Find Movie Directors
```cypher
MATCH (m:Movie {title: 'The Matrix'})<-[:DIRECTED]-(p:Person)
RETURN p.name AS director, p.born AS born_year;
```

### 5.3 Find Cast and Roles
```cypher
MATCH (m:Movie {title: 'The Matrix'})<-[r:ACTED_IN]-(p:Person)
RETURN p.name AS actor, r.roles AS character_roles
ORDER BY actor;
```

### 5.4 Multi-hop Recommendation (Shared Actors)
```cypher
MATCH (m1:Movie {title: 'The Matrix'})<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(m2:Movie)
WHERE m1 <> m2
RETURN m2.title AS recommendation, m2.released AS year, collect(a.name) AS shared_actors
ORDER BY size(shared_actors) DESC, year DESC
LIMIT 5;
```

### 5.5 Co-Star Collaborations
```cypher
MATCH (p1:Person {name: 'Tom Hanks'})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person)
RETURN p2.name AS co_star, count(m) AS shared_movie_count, collect(m.title) AS films
ORDER BY shared_movie_count DESC
LIMIT 5;
```
