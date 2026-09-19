"""Cypher Query Templates for MovieGraph RAG.

Contains predefined, parameterized, read-only Cypher query templates designed
to run against the standard Neo4j Movies dataset. All queries strictly use parameters
($title, $name, etc.) to eliminate Cypher injection risks.
"""

from typing import Dict, Any, Optional

CYPHER_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # 1. Movie Director
    "movie_director": {
        "name": "Find Movie Director",
        "description": "Retrieves the director(s) of a given movie.",
        "parameters": ["title"],
        "query": (
            "MATCH (m:Movie {title: $title})<-[:DIRECTED]-(p:Person)\n"
            "RETURN m.title AS movie, p.name AS director, p.born AS born, m.released AS released"
        ),
    },

    # 2. Movie Actors
    "movie_actors": {
        "name": "Find Movie Cast / Actors",
        "description": "Retrieves all actors and their roles in a specific movie.",
        "parameters": ["title"],
        "query": (
            "MATCH (m:Movie {title: $title})<-[r:ACTED_IN]-(p:Person)\n"
            "RETURN m.title AS movie, p.name AS actor, r.roles AS roles, p.born AS born, m.released AS released\n"
            "ORDER BY p.name"
        ),
    },

    # 3. Movie Release & Details
    "movie_release": {
        "name": "Find Movie Release & Tagline",
        "description": "Retrieves the release year, tagline, and overview of a movie.",
        "parameters": ["title"],
        "query": (
            "MATCH (m:Movie {title: $title})\n"
            "OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)\n"
            "RETURN m.title AS title, m.released AS released, m.tagline AS tagline, "
            "collect(d.name) AS directors"
        ),
    },

    # 4. Actor Movies
    "actor_movies": {
        "name": "Find Movies Acted in by Person",
        "description": "Retrieves all movies starring a specific actor along with roles and release years.",
        "parameters": ["name"],
        "query": (
            "MATCH (p:Person {name: $name})-[r:ACTED_IN]->(m:Movie)\n"
            "RETURN p.name AS actor, m.title AS movie, m.released AS released, "
            "r.roles AS roles, m.tagline AS tagline\n"
            "ORDER BY m.released DESC"
        ),
    },

    # 5. Director Movies
    "director_movies": {
        "name": "Find Movies Directed by Person",
        "description": "Retrieves all movies directed by a specific person.",
        "parameters": ["name"],
        "query": (
            "MATCH (p:Person {name: $name})-[:DIRECTED]->(m:Movie)\n"
            "RETURN p.name AS director, m.title AS movie, m.released AS released, m.tagline AS tagline\n"
            "ORDER BY m.released DESC"
        ),
    },

    # 6. Movies with Shared Actor
    "movies_with_shared_actor": {
        "name": "Movies Sharing Actors",
        "description": "Finds other movies that share at least one actor with a given movie.",
        "parameters": ["title"],
        "query": (
            "MATCH (m1:Movie {title: $title})<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(m2:Movie)\n"
            "WHERE m1 <> m2\n"
            "RETURN m2.title AS recommended_movie, m2.released AS released, m2.tagline AS tagline, "
            "collect(DISTINCT a.name) AS shared_actors, count(DISTINCT a) AS shared_actor_count\n"
            "ORDER BY shared_actor_count DESC, m2.released DESC\n"
            "LIMIT 5"
        ),
    },

    # 7. Movies with Shared Director
    "movies_with_shared_director": {
        "name": "Movies by Same Director",
        "description": "Finds other movies directed by the director of the given movie.",
        "parameters": ["title"],
        "query": (
            "MATCH (m1:Movie {title: $title})<-[:DIRECTED]-(d:Person)-[:DIRECTED]->(m2:Movie)\n"
            "WHERE m1 <> m2\n"
            "RETURN m2.title AS recommended_movie, m2.released AS released, m2.tagline AS tagline, "
            "d.name AS director\n"
            "ORDER BY m2.released DESC\n"
            "LIMIT 5"
        ),
    },

    # 8. Movie Recommendation (Multi-hop Graph Connections)
    "movie_recommendation": {
        "name": "Graph-based Movie Recommendation",
        "description": "Recommends movies connected via shared actors or common directors with explainability.",
        "parameters": ["title"],
        "query": (
            "MATCH (m1:Movie {title: $title})\n"
            "OPTIONAL MATCH (m1)<-[:ACTED_IN]-(a:Person)-[:ACTED_IN]->(m2:Movie)\n"
            "WHERE m1 <> m2\n"
            "WITH m1, m2, collect(DISTINCT a.name) AS shared_actors, count(DISTINCT a) AS shared_actor_count\n"
            "OPTIONAL MATCH (m1)<-[:DIRECTED]-(d:Person)-[:DIRECTED]->(m2)\n"
            "WHERE m2 IS NOT NULL\n"
            "WITH m2, shared_actors, shared_actor_count, collect(DISTINCT d.name) AS same_directors\n"
            "WHERE m2 IS NOT NULL AND (shared_actor_count > 0 OR size(same_directors) > 0)\n"
            "RETURN m2.title AS recommended_movie, m2.released AS released, m2.tagline AS tagline, "
            "shared_actors, shared_actor_count, same_directors, "
            "(shared_actor_count * 2 + size(same_directors) * 3) AS recommendation_score\n"
            "ORDER BY recommendation_score DESC, m2.released DESC\n"
            "LIMIT 6"
        ),
    },

    # 9. Actor Collaboration
    "actor_collaboration": {
        "name": "Co-Star Collaboration",
        "description": "Finds other actors who frequently worked with a given person.",
        "parameters": ["name"],
        "query": (
            "MATCH (p1:Person {name: $name})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person)\n"
            "WHERE p1 <> p2\n"
            "RETURN p2.name AS co_actor, count(m) AS co_appearances, collect(m.title) AS shared_movies\n"
            "ORDER BY co_appearances DESC\n"
            "LIMIT 5"
        ),
    },

    # 10. General Movie Information (Complete Graph Neighborhood)
    "general_movie_information": {
        "name": "Full Movie Overview",
        "description": "Retrieves the full graph neighborhood of a movie including directors, cast, and writers.",
        "parameters": ["title"],
        "query": (
            "MATCH (m:Movie {title: $title})\n"
            "OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)\n"
            "OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)\n"
            "OPTIONAL MATCH (m)<-[:PRODUCED]-(pr:Person)\n"
            "OPTIONAL MATCH (m)<-[:WROTE]-(w:Person)\n"
            "RETURN m.title AS title, m.released AS released, m.tagline AS tagline, "
            "collect(DISTINCT d.name) AS directors, "
            "collect(DISTINCT a.name)[..8] AS cast, "
            "collect(DISTINCT pr.name) AS producers, "
            "collect(DISTINCT w.name) AS writers"
        ),
    },
}


def get_cypher_template(query_type: str) -> Optional[Dict[str, Any]]:
    """Retrieves a Cypher template dictionary by query type identifier."""
    return CYPHER_TEMPLATES.get(query_type)
