"""Shared constants and utility functions for the RAG system."""

from enum import Enum
from typing import List, Dict

# Model Constants
class ModelType(Enum):
    """Supported model types."""
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    EMBEDDING_ADA = "text-embedding-3-small"
    CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-12-v2"


# Intent Classifications
class IntentType(Enum):
    """User intent types."""
    SEARCH = "search"
    CODING = "coding"
    EXPLANATION = "explanation"
    DEBUG = "debug"
    OPTIMIZATION = "optimization"
    ARCHITECTURE = "architecture"
    GENERAL = "general"


# Document Categories
class DocumentCategory(Enum):
    """Document categories."""
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    CODE_EXAMPLE = "code_example"
    REFERENCE = "reference"
    BEST_PRACTICE = "best_practice"
    ISSUE = "issue"
    SOLUTION = "solution"


# API Response Codes
class ResponseStatus(Enum):
    """Response status codes."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


# Utility Constants
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 5
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000

# Common Prompts
SYSTEM_PROMPTS = {
    "expert_coder": """You are an expert software engineer with deep knowledge of:
- Software architecture and design patterns
- Multiple programming languages and frameworks
- Best practices and industry standards
- Debugging and optimization techniques
- Code security and performance

Provide detailed, expert-level responses with:
- Code examples when applicable
- Explanations of concepts
- Trade-offs and considerations
- References to best practices""",

    "code_debugger": """You are an expert debugger specializing in:
- Identifying root causes of issues
- Analyzing error messages and stack traces
- Suggesting fixes with explanations
- Preventing similar issues in the future

Provide step-by-step debugging guidance with:
- Problem analysis
- Hypothesis testing
- Solution verification
- Prevention strategies""",

    "architect": """You are a software architect with expertise in:
- System design and scalability
- Microservices and distributed systems
- Database design and optimization
- API design and standards
- Infrastructure and DevOps

Provide architectural guidance with:
- Design patterns and trade-offs
- Scalability considerations
- Performance optimization
- Security implications"""
}

# Error Messages
ERROR_MESSAGES = {
    "query_blocked": "Your query was blocked by safety guardrails.",
    "response_blocked": "The response was filtered by safety guardrails.",
    "retrieval_failed": "Failed to retrieve relevant documents.",
    "generation_failed": "Failed to generate response.",
    "invalid_query": "Query is invalid or too short.",
    "api_error": "API error occurred. Please try again.",
    "timeout": "Request timed out. Please try again.",
    "rate_limit": "Rate limit exceeded. Please wait before trying again."
}

# Success Messages
SUCCESS_MESSAGES = {
    "query_accepted": "Query accepted and processing...",
    "documents_ingested": "Documents successfully ingested.",
    "session_created": "New session created.",
    "settings_saved": "Settings saved successfully."
}

# Helper Functions
def format_error_message(error_key: str, details: str = "") -> str:
    """Format error message with optional details.

    Args:
        error_key: Key in ERROR_MESSAGES
        details: Additional details

    Returns:
        Formatted message
    """
    base = ERROR_MESSAGES.get(error_key, "An error occurred.")
    if details:
        return f"{base} {details}"
    return base


def format_context(documents: List) -> str:
    """Format documents into context string.

    Args:
        documents: List of documents

    Returns:
        Formatted context
    """
    context_parts = []
    for i, doc in enumerate(documents, 1):
        content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        
        context_parts.append(f"[Source {i}] {content}")
        if metadata:
            source = metadata.get('source', 'unknown')
            context_parts.append(f"Source: {source}")

    return "\n\n".join(context_parts)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def parse_query(query: str) -> Dict:
    """Parse user query for intent and keywords.

    Args:
        query: User query

    Returns:
        Parsed query info
    """
    import re
    
    intent = IntentType.GENERAL
    
    # Detect intent
    if any(word in query.lower() for word in ["debug", "error", "fix", "bug"]):
        intent = IntentType.DEBUG
    elif any(word in query.lower() for word in ["optimize", "performance", "fast"]):
        intent = IntentType.OPTIMIZATION
    elif any(word in query.lower() for word in ["architecture", "design", "pattern"]):
        intent = IntentType.ARCHITECTURE
    elif any(word in query.lower() for word in ["code", "implement", "write"]):
        intent = IntentType.CODING
    elif any(word in query.lower() for word in ["what", "how", "why", "explain"]):
        intent = IntentType.EXPLANATION

    # Extract keywords
    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [w for w in words if len(w) > 3]

    return {
        "intent": intent.value,
        "keywords": keywords,
        "length": len(query),
        "query": query
    }


def calculate_relevance_score(query: str, document: str, base_score: float = 0.0) -> float:
    """Calculate relevance score between query and document.

    Args:
        query: User query
        document: Document content
        base_score: Base score from ranker (0-1)

    Returns:
        Relevance score (0-1)
    """
    query_words = set(query.lower().split())
    doc_words = set(document.lower().split())
    
    # Calculate overlap
    overlap = len(query_words & doc_words) / len(query_words) if query_words else 0
    
    # Combine with base score
    final_score = (base_score * 0.7) + (overlap * 0.3)
    return min(final_score, 1.0)
