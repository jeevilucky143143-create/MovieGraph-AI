"""RAG Pipeline Orchestrator for MovieGraph AI.

Coordinates the end-to-end question answering pipeline:
Question -> Understanding -> Cypher Generation -> Neo4j Retrieval -> Context Building -> LLM Grounding -> Explainable Response.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from database.neo4j_client import Neo4jClient
from rag.query_classifier import QueryClassifier, QueryIntent
from rag.retriever import GraphRetriever, RetrievalResult
from rag.context_builder import ContextBuilder
from llm.llm_service import LLMService


@dataclass
class RAGResponse:
    """Encapsulates the complete result of an end-to-end RAG workflow."""
    question: str
    answer: str
    query_type: str
    template_name: str
    cypher_query: str
    parameters: Dict[str, Any]
    records: List[Dict[str, Any]]
    record_count: int
    entity_badges: List[Dict[str, str]]
    execution_time_ms: float
    is_live_database: bool
    provider: str
    grounded: bool
    intent_explanation: str
    persona: str = "Cinematic Scholar"
    output_style: str = "Concise Narrative"


class RAGPipeline:
    """Executes the complete Graph RAG pipeline with full explainability."""

    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        self.client = neo4j_client or Neo4jClient()
        self.classifier = QueryClassifier()
        self.retriever = GraphRetriever(self.client)
        self.context_builder = ContextBuilder()
        self.llm_service = LLMService()

    def run(
        self,
        question: str,
        persona: str = "Cinematic Scholar",
        output_style: str = "Concise Narrative",
    ) -> RAGResponse:
        """Runs the complete RAG pipeline on a user's question.

        Args:
            question: Raw natural-language question.
            persona: Selected AI Persona.
            output_style: Selected output presentation style.

        Returns:
            RAGResponse dataclass containing the answer, knowledge found, and Cypher trace.
        """
        # Step 1: Question Understanding & Query Classification
        intent = self.classifier.classify(question)

        # Step 2: Safe Cypher Query Execution & Graph Retrieval
        retrieval = self.retriever.retrieve(intent)

        # Step 3: Context Building
        context_str, badges = self.context_builder.build_context(retrieval)

        # Step 4: LLM Grounding & Natural Language Generation
        llm_out = self.llm_service.generate_grounded_answer(
            question=question,
            graph_context=context_str,
            query_type=intent.query_type,
            persona=persona,
            output_format=output_style,
        )

        return RAGResponse(
            question=question,
            answer=llm_out["answer"],
            query_type=intent.query_type,
            template_name=retrieval.template_name,
            cypher_query=retrieval.cypher_query,
            parameters=retrieval.parameters,
            records=retrieval.records,
            record_count=retrieval.record_count,
            entity_badges=badges,
            execution_time_ms=retrieval.execution_time_ms,
            is_live_database=retrieval.is_live_database,
            provider=llm_out["provider"],
            grounded=llm_out["grounded"],
            intent_explanation=intent.explanation,
            persona=persona,
            output_style=output_style,
        )
