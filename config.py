"""Configuration module for MovieGraph RAG Assistant.

Handles loading of environment variables from .env file and provides
centralized access to database and LLM credentials.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class Config:
    """Central configuration class for MovieGraph RAG."""

    # Neo4j Settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Application Settings
    APP_NAME: str = "MovieGraph AI"
    APP_TAGLINE: str = "Discover the stories behind the stories. Explore movies through their hidden connections."
    DATASET_NAME: str = "TMDb 5000 Movies Knowledge Graph"
    EXPECTED_NODE_COUNT: int = 68627

    @classmethod
    def is_neo4j_configured(cls) -> bool:
        """Check if Neo4j connection details are present."""
        return bool(cls.NEO4J_URI and cls.NEO4J_USERNAME and cls.NEO4J_PASSWORD)

    @classmethod
    def has_llm_key(cls) -> bool:
        """Check if at least one LLM API key is available."""
        if cls.LLM_PROVIDER == "gemini" and cls.GEMINI_API_KEY:
            return True
        if cls.LLM_PROVIDER == "openai" and cls.OPENAI_API_KEY:
            return True
        return bool(cls.GEMINI_API_KEY or cls.OPENAI_API_KEY)

    @classmethod
    def get_active_provider(cls) -> str:
        """Returns the active LLM provider name or 'deterministic_engine' if no keys are set."""
        if cls.GEMINI_API_KEY and (cls.LLM_PROVIDER == "gemini" or not cls.OPENAI_API_KEY):
            return "gemini"
        elif cls.OPENAI_API_KEY:
            return "openai"
        return "deterministic_grounded"
