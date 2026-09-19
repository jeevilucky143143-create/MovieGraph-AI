"""Unit tests for Cypher query templates and safety validation."""

import pytest
from rag.cypher_templates import CYPHER_TEMPLATES, get_cypher_template
from database.neo4j_client import Neo4jClient, Neo4jSecurityError


def test_cypher_templates_exist():
    """Verify all 10 required query templates exist."""
    required_keys = [
        "movie_director",
        "movie_actors",
        "movie_release",
        "actor_movies",
        "director_movies",
        "movies_with_shared_actor",
        "movies_with_shared_director",
        "movie_recommendation",
        "actor_collaboration",
        "general_movie_information",
    ]
    for key in required_keys:
        template = get_cypher_template(key)
        assert template is not None, f"Missing required template: {key}"
        assert "query" in template
        assert "parameters" in template
        assert len(template["parameters"]) > 0


def test_cypher_safety_read_only():
    """Ensure that only read queries pass and mutation keywords are blocked."""
    client = Neo4jClient()

    # Valid read queries
    safe_query = "MATCH (m:Movie {title: $title}) RETURN m"
    client.validate_query_safety(safe_query)  # Should not raise

    # Prohibited mutations
    forbidden_queries = [
        "CREATE (m:Movie {title: 'Fake Movie'})",
        "MATCH (m:Movie) DELETE m",
        "MATCH (m:Movie) DETACH DELETE m",
        "MATCH (m:Movie) SET m.rating = 10",
        "MERGE (p:Person {name: 'Attacker'})",
        "DROP INDEX ON :Movie(title)",
    ]

    for bad_query in forbidden_queries:
        with pytest.raises(Neo4jSecurityError):
            client.validate_query_safety(bad_query)
