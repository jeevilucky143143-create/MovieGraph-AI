"""Retriever Module for MovieGraph RAG.

Executes parameterized Cypher query templates against Neo4j and formats
raw records with retrieval metrics and provenance metadata.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from database.neo4j_client import Neo4jClient
from rag.cypher_templates import CYPHER_TEMPLATES, get_cypher_template
from rag.query_classifier import QueryIntent


@dataclass
class RetrievalResult:
    """Encapsulates the output of a knowledge graph retrieval operation."""
    query_type: str
    template_name: str
    cypher_query: str
    parameters: Dict[str, Any]
    records: List[Dict[str, Any]]
    record_count: int
    execution_time_ms: float
    is_live_database: bool
    status: str
    error: Optional[str] = None


class GraphRetriever:
    """Executes safe Cypher graph queries and captures structured knowledge records."""

    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        self.client = neo4j_client or Neo4jClient()

    def retrieve(self, intent: QueryIntent) -> RetrievalResult:
        """Executes the Cypher template corresponding to the given QueryIntent.

        Args:
            intent: The QueryIntent produced by QueryClassifier.

        Returns:
            RetrievalResult containing retrieved records and execution metadata.
        """
        template = get_cypher_template(intent.query_type)
        if not template:
            # Fallback to general movie info
            template = CYPHER_TEMPLATES["general_movie_information"]

        cypher_query = template["query"]
        params = intent.parameters

        start_time = time.perf_counter()
        try:
            records = self.client.execute_read_query(cypher_query, params)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return RetrievalResult(
                query_type=intent.query_type,
                template_name=template["name"],
                cypher_query=cypher_query,
                parameters=params,
                records=records,
                record_count=len(records),
                execution_time_ms=elapsed_ms,
                is_live_database=self.client.is_live,
                status="SUCCESS" if records else "EMPTY_RESULT",
                error=None,
            )
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return RetrievalResult(
                query_type=intent.query_type,
                template_name=template["name"],
                cypher_query=cypher_query,
                parameters=params,
                records=[],
                record_count=0,
                execution_time_ms=elapsed_ms,
                is_live_database=self.client.is_live,
                status="ERROR",
                error=str(e),
            )
