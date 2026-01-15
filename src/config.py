"""Configuration management for Expert RAG Chatbot System.

Handles environment variables, model configurations, and system settings
for production-scale deployment.
"""

import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation and defaults."""

    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    tavily_api_key: Optional[str] = Field(None, env="TAVILY_API_KEY")

    # LLM Configuration
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_timeout: int = 60
    llm_max_retries: int = 3

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    embedding_batch_size: int = 100

    # Cross-Encoder Configuration
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranking_threshold: float = 0.5
    top_k_results: int = 5

    # Vector Database
    vector_db_type: str = "faiss"
    pinecone_index_name: str = "expert-rag-index"
    pinecone_environment: str = "us-east-1"
    pinecone_metric: str = "cosine"

    # Chunking Strategy
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunk_strategy: str = "semantic"

    # System Settings
    max_context_length: int = 4096
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_monitoring: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Legacy exports for backward compatibility
OPENAI_API_KEY = settings.openai_api_key
PINECONE_API_KEY = settings.pinecone_api_key
TAVILY_API_KEY = settings.tavily_api_key
LLM_MODEL = settings.llm_model
EMBEDDING_MODEL = settings.embedding_model
CROSS_ENCODER_MODEL = settings.cross_encoder_model
VECTOR_DB = settings.vector_db_type
PINECONE_INDEX_NAME = settings.pinecone_index_name
PINECONE_ENVIRONMENT = settings.pinecone_environment
CHUNK_SIZE = settings.chunk_size
CHUNK_OVERLAP = settings.chunk_overlap

logger.info(f"Configuration loaded: LLM={LLM_MODEL}, Embedding={EMBEDDING_MODEL}")