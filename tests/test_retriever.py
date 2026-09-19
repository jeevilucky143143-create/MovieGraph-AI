"""Unit tests for Graph Retriever and Context Builder."""

import pytest
from database.neo4j_client import Neo4jClient
from rag.query_classifier import QueryIntent
from rag.retriever import GraphRetriever
from rag.context_builder import ContextBuilder


@pytest.fixture
def retriever():
    client = Neo4jClient()
    return GraphRetriever(client)


def test_retriever_movie_director(retriever):
    intent = QueryIntent(
        query_type="movie_director",
        template_name="Find Movie Director",
        confidence=1.0,
        parameters={"title": "The Matrix"},
        detected_entity="The Matrix",
        detected_entity_type="movie",
        explanation="Test",
    )
    result = retriever.retrieve(intent)
    assert result.status == "SUCCESS"
    assert result.record_count > 0
    directors = [r["director"] for r in result.records]
    assert "Lana Wachowski" in directors
    assert "Lilly Wachowski" in directors


def test_retriever_movie_actors(retriever):
    intent = QueryIntent(
        query_type="movie_actors",
        template_name="Find Movie Cast / Actors",
        confidence=1.0,
        parameters={"title": "The Matrix"},
        detected_entity="The Matrix",
        detected_entity_type="movie",
        explanation="Test",
    )
    result = retriever.retrieve(intent)
    assert result.status == "SUCCESS"
    assert result.record_count >= 4
    actors = [r["actor"] for r in result.records]
    assert "Keanu Reeves" in actors
    assert "Carrie-Anne Moss" in actors


def test_context_builder(retriever):
    intent = QueryIntent(
        query_type="movie_director",
        template_name="Find Movie Director",
        confidence=1.0,
        parameters={"title": "The Matrix"},
        detected_entity="The Matrix",
        detected_entity_type="movie",
        explanation="Test",
    )
    result = retriever.retrieve(intent)
    context_str, badges = ContextBuilder.build_context(result)
    assert "The Matrix" in context_str
    assert "Lana Wachowski" in context_str
    assert len(badges) >= 2
