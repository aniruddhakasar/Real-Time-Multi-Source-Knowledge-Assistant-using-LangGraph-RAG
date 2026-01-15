"""Vector store management for scalable RAG systems.

Supports FAISS with caching, efficient retrieval, and production error handling.
"""

import logging
from typing import List, Optional
from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector storage and retrieval with caching."""

    def __init__(self):
        """Initialize vector store manager."""
        self._vectorstore = None
        self._embeddings = None
        logger.info(f"Initializing VectorStoreManager")

    @property
    def embeddings(self):
        """Get embeddings model."""
        if self._embeddings is None:
            try:
                self._embeddings = OpenAIEmbeddings(
                    model=settings.embedding_model,
                    api_key=settings.openai_api_key,
                    request_timeout=60
                )
                logger.info(f"Embeddings initialized: {settings.embedding_model}")
            except Exception as e:
                logger.error(f"Failed to initialize embeddings: {e}")
                raise
        return self._embeddings

    def get_vectorstore(self):
        """Get or create FAISS vector store.

        Returns:
            Vector store instance
        """
        if self._vectorstore is not None:
            return self._vectorstore

        try:
            try:
                vectorstore = FAISS.load_local(
                    "faiss_index",
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing FAISS index")
            except Exception as e:
                logger.info(f"Creating new FAISS index")
                vectorstore = FAISS.from_texts(
                    ["Expert RAG System - Ready for complex coding"],
                    self.embeddings,
                    metadatas=[{"source": "system"}]
                )
                vectorstore.save_local("faiss_index")
                logger.info("Created and saved new FAISS index")

            self._vectorstore = vectorstore
            return self._vectorstore
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")
            raise

    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Add documents to vector store.

        Args:
            texts: List of text documents
            metadatas: Optional metadata for each document
        """
        try:
            vs = self.get_vectorstore()
            vs.add_texts(texts, metadatas=metadatas)
            logger.info(f"Added {len(texts)} documents")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def get_retriever(self, k: int = 5, **kwargs):
        """Get retriever for RAG pipeline.

        Args:
            k: Number of results to return

        Returns:
            Retriever instance
        """
        try:
            vs = self.get_vectorstore()
            return vs.as_retriever(search_kwargs={"k": k})
        except Exception as e:
            logger.error(f"Failed to get retriever: {e}")
            raise


@lru_cache(maxsize=1)
def get_vectorstore_manager() -> VectorStoreManager:
    """Get cached vector store manager.

    Returns:
        VectorStoreManager instance
    """
    return VectorStoreManager()


def get_vectorstore():
    """Get vector store instance.

    Returns:
        Vector store
    """
    manager = get_vectorstore_manager()
    return manager.get_vectorstore()