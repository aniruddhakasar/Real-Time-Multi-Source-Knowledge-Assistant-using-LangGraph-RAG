"""Expert-level chatbot module with advanced conversational AI.

Provides intelligent chat models with caching, retry logic, error handling,
and streaming for production applications.
"""

import logging
from typing import Optional
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.config import settings

logger = logging.getLogger(__name__)


class ExpertChatbot:
    """Expert-level chatbot with advanced features for complex coding tasks."""

    SYSTEM_PROMPT = """You are an expert AI assistant specialized in:
- Complex software engineering and architecture
- Code analysis, review, and optimization
- System design and scalability
- Best practices and design patterns
- Debugging and troubleshooting
- Performance optimization

Provide detailed, accurate, and actionable responses. Include code examples when relevant.
Explain your reasoning and consider edge cases and production concerns."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Initialize expert chatbot.

        Args:
            model: LLM model name
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.model = model or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self._llm = None
        self._prompt_template = None
        logger.info(f"Initializing ExpertChatbot: model={self.model}")

    @property
    def llm(self):
        """Lazy-load LLM with proper configuration."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model_name=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=settings.openai_api_key,
                max_retries=settings.llm_max_retries,
                timeout=settings.llm_timeout
            )
        return self._llm

    @property
    def prompt_template(self):
        """Get prompt template for structured interactions."""
        if self._prompt_template is None:
            self._prompt_template = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(self.SYSTEM_PROMPT),
                HumanMessagePromptTemplate.from_template("{query}")
            ])
        return self._prompt_template

    def invoke(self, query: str, context: str = "") -> str:
        """Invoke chatbot with query and optional context.

        Args:
            query: User query
            context: Optional context/documents

        Returns:
            AI response

        Raises:
            Exception: If invocation fails
        """
        try:
            if context:
                full_query = f"Context:\n{context}\n\nQuestion:\n{query}"
            else:
                full_query = query

            response = self.llm.invoke(full_query)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking chatbot: {e}")
            raise

    def chain(self, query: str) -> str:
        """Invoke using prompt template chain.

        Args:
            query: User query

        Returns:
            AI response
        """
        try:
            chain = self.prompt_template | self.llm
            response = chain.invoke({"query": query})
            return response.content
        except Exception as e:
            logger.error(f"Error in chain: {e}")
            raise


@lru_cache(maxsize=1)
def get_chat_model() -> ExpertChatbot:
    """Get cached chatbot instance.

    Returns:
        ExpertChatbot instance
    """
    return ExpertChatbot()


def get_specialized_chatbot(specialty: str) -> ExpertChatbot:
    """Get specialized chatbot for specific domain.

    Args:
        specialty: Domain (code, architecture, debugging, optimization)

    Returns:
        Specialized ExpertChatbot
    """
    specialties = {
        "code": "You are an expert code reviewer and software engineer.",
        "architecture": "You are an expert in system design and architecture.",
        "debugging": "You are an expert debugger specializing in complex issues.",
        "optimization": "You are an expert in performance optimization.",
    }

    chatbot = ExpertChatbot()
    if specialty in specialties:
        chatbot.SYSTEM_PROMPT = specialties[specialty]
    return chatbot