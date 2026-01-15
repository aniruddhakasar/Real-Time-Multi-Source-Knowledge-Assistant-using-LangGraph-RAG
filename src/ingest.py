"""Document ingestion and processing pipeline for RAG system.

Handles loading documents from various sources, chunking, and vectorization:
- Multiple file formats (PDF, TXT, MD, JSON)
- Smart chunking with overlap
- Metadata extraction
- Batch processing
- Progress tracking
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, DirectoryLoader, JSONLoader, PyPDFLoader
)
from langchain_core.documents import Document
from src.config import settings
from src.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Professional document ingestion and processing."""

    def __init__(self):
        """Initialize document processor."""
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vectorstore = get_vectorstore()
        logger.info("DocumentProcessor initialized")

    def load_txt(self, file_path: str) -> List[Document]:
        """Load text file.

        Args:
            file_path: Path to text file

        Returns:
            List of documents
        """
        try:
            loader = TextLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded text file: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
            return []

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            List of documents
        """
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded PDF file: {file_path} ({len(docs)} pages)")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDF file {file_path}: {e}")
            return []

    def load_json(self, file_path: str, jq_schema: Optional[str] = None) -> List[Document]:
        """Load JSON file.

        Args:
            file_path: Path to JSON file
            jq_schema: Optional JQ schema for extraction

        Returns:
            List of documents
        """
        try:
            loader = JSONLoader(
                file_path=file_path,
                jq_schema=jq_schema or ".[] | @json"
            )
            docs = loader.load()
            logger.info(f"Loaded JSON file: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return []

    def load_directory(self, directory: str, pattern: str = "*.txt") -> List[Document]:
        """Load all files from directory.

        Args:
            directory: Directory path
            pattern: File pattern to match

        Returns:
            List of documents
        """
        try:
            loader = DirectoryLoader(
                directory,
                glob=pattern,
                loader_cls=TextLoader
            )
            docs = loader.load()
            logger.info(f"Loaded {len(docs)} files from {directory}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load directory {directory}: {e}")
            return []

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks.

        Args:
            documents: List of documents

        Returns:
            List of chunked documents
        """
        try:
            chunked = self.splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} docs into {len(chunked)} chunks")
            return chunked
        except Exception as e:
            logger.error(f"Failed to chunk documents: {e}")
            return []

    def add_metadata(
        self,
        documents: List[Document],
        source: str = "unknown",
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> List[Document]:
        """Add metadata to documents.

        Args:
            documents: List of documents
            source: Data source
            category: Document category
            tags: Custom tags

        Returns:
            Documents with metadata
        """
        for doc in documents:
            doc.metadata.update({
                "source": source,
                "category": category,
                "ingestion_date": datetime.now().isoformat(),
                "tags": tags or []
            })
        logger.info(f"Added metadata to {len(documents)} documents")
        return documents

    def ingest_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Ingest documents into vector store.

        Args:
            documents: List of documents to ingest
            batch_size: Batch size for processing

        Returns:
            Ingestion report
        """
        try:
            total = len(documents)
            added = 0

            # Process in batches
            for i in range(0, total, batch_size):
                batch = documents[i:i+batch_size]
                self.vectorstore.add_documents(batch)
                added += len(batch)
                progress = (added / total) * 100
                logger.info(f"Ingested {added}/{total} documents ({progress:.1f}%)")

            return {
                "status": "success",
                "documents_ingested": added,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def ingest_file(
    file_path: str,
    source: str = "file",
    category: str = "general"
) -> Dict[str, Any]:
    """Ingest a single file into the RAG system.

    Args:
        file_path: Path to file
        source: Data source label
        category: Document category

    Returns:
        Ingestion report
    """
    processor = DocumentProcessor()
    path = Path(file_path)

    # Load based on file type
    if path.suffix == ".txt":
        docs = processor.load_txt(file_path)
    elif path.suffix == ".pdf":
        docs = processor.load_pdf(file_path)
    elif path.suffix == ".json":
        docs = processor.load_json(file_path)
    else:
        logger.warning(f"Unsupported file type: {path.suffix}")
        return {"status": "error", "error": "Unsupported file type"}

    if not docs:
        return {"status": "error", "error": "Failed to load document"}

    # Process documents
    chunked = processor.chunk_documents(docs)
    with_metadata = processor.add_metadata(chunked, source=source, category=category)
    
    # Ingest
    result = processor.ingest_documents(with_metadata)
    return result


def ingest_directory(
    directory: str,
    pattern: str = "*.txt",
    source: str = "directory",
    category: str = "general"
) -> Dict[str, Any]:
    """Ingest all files from a directory.

    Args:
        directory: Directory path
        pattern: File pattern to match
        source: Data source label
        category: Document category

    Returns:
        Ingestion report
    """
    processor = DocumentProcessor()
    docs = processor.load_directory(directory, pattern)

    if not docs:
        return {"status": "error", "error": "No documents found"}

    # Process documents
    chunked = processor.chunk_documents(docs)
    with_metadata = processor.add_metadata(chunked, source=source, category=category)
    
    # Ingest
    result = processor.ingest_documents(with_metadata)
    return result


# Example usage and batch ingestion
def batch_ingest(
    sources: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """Ingest multiple sources in batch.

    Args:
        sources: List of source configs with 'path', 'type', 'source', 'category'

    Returns:
        List of ingestion reports
    """
    results = []
    for source_config in sources:
        path = source_config.get("path")
        source_type = source_config.get("type", "file")
        source = source_config.get("source", "batch")
        category = source_config.get("category", "general")

        try:
            if source_type == "file":
                result = ingest_file(path, source=source, category=category)
            elif source_type == "directory":
                pattern = source_config.get("pattern", "*.txt")
                result = ingest_directory(path, pattern, source=source, category=category)
            else:
                result = {"status": "error", "error": f"Unknown type: {source_type}"}
            
            results.append(result)
        except Exception as e:
            logger.error(f"Batch ingestion failed for {path}: {e}")
            results.append({"status": "error", "error": str(e)})

    logger.info(f"Batch ingestion completed: {len(results)} sources processed")
    return results
