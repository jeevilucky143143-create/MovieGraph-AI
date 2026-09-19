"""Unit tests for Grounding and Anti-Hallucination Guardrails."""

import pytest
from llm.llm_service import LLMService
from rag.rag_pipeline import RAGPipeline


def test_empty_graph_prevents_hallucination():
    """Verify that when the graph has no data, the system strictly refuses to invent facts."""
    llm = LLMService()

    # Case 1: Explicit NO_DATA_FOUND context
    result = llm.generate_grounded_answer(
        question="Who directed Inception?",
        graph_context="NO_DATA_FOUND: The Neo4j Knowledge Graph returned 0 records for this query.",
    )
    assert result["grounded"] is True
    assert "couldn't find that information" in result["answer"].lower()
    # Ensure it did NOT hallucinate Christopher Nolan
    assert "nolan" not in result["answer"].lower()


def test_rag_pipeline_unknown_movie_grounding():
    """Test full pipeline behavior on a movie absent from the Neo4j Movies dataset."""
    pipeline = RAGPipeline()
    response = pipeline.run("Who directed The Quantum Paradox of 3025?")

    assert response.record_count == 0
    assert "couldn't find that information" in response.answer.lower()


def test_factual_grounding_interstellar():
    """Verify factual question answering for TMDB movie Interstellar."""
    pipeline = RAGPipeline()
    response = pipeline.run("Who directed Interstellar?")

    assert response.record_count > 0
    assert response.grounded is True
    assert "Nolan" in response.answer


def test_factual_grounding_the_matrix():
    """Verify factual question answering is correctly grounded in verified graph data."""
    pipeline = RAGPipeline()
    response = pipeline.run("Who directed The Matrix?")

    assert response.record_count > 0
    assert response.grounded is True
    assert "Wachowski" in response.answer


def test_persona_and_output_structure_variations():
    """Verify that all persona tones and output structures apply distinct styles."""
    pipeline = RAGPipeline()

    # Test Bulleted Intelligence Brief
    res_bullet = pipeline.run(
        "Who directed Inception?",
        persona="Casual Movie Buddy",
        output_style="Bulleted Intelligence Brief",
    )
    assert "•" in res_bullet.answer
    assert "Inception" in res_bullet.answer
    assert "Christopher Nolan" in res_bullet.answer

    # Test Detailed Analysis
    res_detailed = pipeline.run(
        "Who directed Inception?",
        persona="Cannes Film Critic",
        output_style="Detailed Analysis",
    )
    assert "Cinematic Overview" in res_detailed.answer
    assert "Archival Relationship Breakdown" in res_detailed.answer
    assert "Christopher Nolan" in res_detailed.answer

    # Test Concise Narrative with Studio Producer
    res_concise = pipeline.run(
        "Who directed Inception?",
        persona="Studio Producer",
        output_style="Concise Narrative",
    )
    assert "marquee" in res_concise.answer.lower() or "packaged" in res_concise.answer.lower()
    assert "Christopher Nolan" in res_concise.answer
