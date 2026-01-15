"""Advanced RAG Pipeline with LangGraph for expert-level code assistance.

Implements a production-grade retrieval-augmented generation system with:
- Intelligent routing and intent classification
- Vector search with re-ranking
- Conversation memory management
- Safety guardrails
- Comprehensive error handling and logging
"""

import logging
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from src.vectorstore import get_vectorstore
from src.chatbot import get_chat_model
from src.config import settings
from src.guardrails import check_query, check_response
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class GraphState(Dict):
    """LangGraph state management for RAG pipeline."""

    def __init__(self):
        super().__init__()
        self.update({
            "query": "",
            "intent": "",
            "vector_results": [],
            "web_results": [],
            "reranked_results": [],
            "answer": "",
            "memory": [],
            "confidence": 0.0,
            "error": None
        })


class RAGPipeline:
    """Production-grade RAG pipeline for expert code assistance."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.graph = None
        self.llm = get_chat_model()
        self.vectorstore = get_vectorstore()
        self.cross_encoder = CrossEncoder(settings.cross_encoder_model)
        logger.info("RAGPipeline initialized")

    def intent_classifier(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user intent.

        Args:
            state: Current graph state

        Returns:
            Updated state with intent classification
        """
        query = state.get("query", "")
        
        if any(word in query.lower() for word in ["search", "find", "look for"]):
            intent = "search"
        elif any(word in query.lower() for word in ["code", "debug", "fix", "implement"]):
            intent = "coding"
        elif any(word in query.lower() for word in ["explain", "help", "how", "why"]):
            intent = "explanation"
        else:
            intent = "general"

        state["intent"] = intent
        logger.info(f"Classified intent: {intent}")
        return state

    def vector_rag_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant documents from vector store.

        Args:
            state: Current graph state

        Returns:
            Updated state with retrieved documents
        """
        try:
            query = state.get("query", "")
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": settings.top_k_results})
            docs = retriever.get_relevant_documents(query)
            state["vector_results"] = docs
            logger.info(f"Retrieved {len(docs)} documents")
            return state
        except Exception as e:
            logger.error(f"Vector RAG failed: {e}")
            state["error"] = str(e)
            return state

    def reranker_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Re-rank retrieved documents by relevance.

        Args:
            state: Current graph state

        Returns:
            Updated state with re-ranked documents
        """
        try:
            results = state.get("vector_results", [])
            query = state.get("query", "")

            if not results:
                state["reranked_results"] = []
                return state

            # Prepare documents for scoring
            doc_pairs = [
                (query, doc.page_content if hasattr(doc, 'page_content') else str(doc))
                for doc in results
            ]

            # Score with cross-encoder
            scores = self.cross_encoder.predict(doc_pairs)
            
            # Sort by score
            ranked = sorted(
                zip(results, scores),
                key=lambda x: x[1],
                reverse=True
            )

            # Filter by threshold
            reranked = [
                doc for doc, score in ranked
                if score >= settings.reranking_threshold
            ][:settings.top_k_results]

            state["reranked_results"] = reranked
            state["confidence"] = float(scores[0]) if scores else 0.0
            logger.info(f"Re-ranked to {len(reranked)} documents")
            return state
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            state["error"] = str(e)
            return state

    def answer_generator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate answer using LLM with context.

        Args:
            state: Current graph state

        Returns:
            Updated state with generated answer
        """
        try:
            query = state.get("query", "")
            docs = state.get("reranked_results", [])

            # Build context from documents
            context = "\n".join([
                doc.page_content if hasattr(doc, 'page_content') else str(doc)
                for doc in docs
            ])

            # Generate answer
            if context:
                prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Provide a detailed, expert-level response with code examples if applicable."""
            else:
                prompt = f"""Answer this question about software engineering and coding:

Question: {query}

Provide a comprehensive, expert-level response."""

            answer = self.llm.invoke(prompt)
            state["answer"] = answer if isinstance(answer, str) else answer.content
            logger.info("Answer generated successfully")
            return state
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            state["answer"] = f"Error generating answer: {str(e)}"
            state["error"] = str(e)
            return state

    def memory_update_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update conversation memory.

        Args:
            state: Current graph state

        Returns:
            Updated state with conversation memory
        """
        memory = state.get("memory", [])
        exchange = {
            "query": state.get("query", ""),
            "answer": state.get("answer", ""),
            "intent": state.get("intent", ""),
            "confidence": state.get("confidence", 0.0)
        }
        memory.append(exchange)
        state["memory"] = memory[-20:]  # Keep last 20 exchanges
        logger.info("Memory updated")
        return state

    def create_graph(self) -> StateGraph:
        """Create and compile LangGraph workflow.

        Returns:
            Compiled graph
        """
        graph = StateGraph(dict)

        # Add nodes
        graph.add_node("intent_classifier", self.intent_classifier)
        graph.add_node("vector_rag", self.vector_rag_node)
        graph.add_node("reranker", self.reranker_node)
        graph.add_node("answer_generator", self.answer_generator_node)
        graph.add_node("memory_update", self.memory_update_node)

        # Set entry point
        graph.set_entry_point("intent_classifier")

        # Add edges
        graph.add_edge("intent_classifier", "vector_rag")
        graph.add_edge("vector_rag", "reranker")
        graph.add_edge("reranker", "answer_generator")
        graph.add_edge("answer_generator", "memory_update")
        graph.add_edge("memory_update", END)

        self.graph = graph.compile()
        logger.info("Graph compiled successfully")
        return self.graph

    def invoke(self, query: str, conversation_history: Optional[List] = None) -> tuple[str, List]:
        """Invoke the RAG pipeline.

        Args:
            query: User query
            conversation_history: Previous conversation messages

        Returns:
            Tuple of (answer, sources)
        """
        # Check query safety
        is_safe, reason, _ = check_query(query)
        if not is_safe:
            logger.warning(f"Query blocked by guardrails: {reason}")
            return f"I cannot assist with this request. {reason}", []

        try:
            # Build initial state
            state = {
                "query": query,
                "memory": conversation_history or [],
                "vector_results": [],
                "reranked_results": [],
                "answer": "",
                "intent": "",
                "confidence": 0.0,
                "error": None
            }

            # Create and invoke graph
            if self.graph is None:
                self.create_graph()

            result = self.graph.invoke(state)

            # Check response safety
            answer = result.get("answer", "")
            response_safe, response_reason, _ = check_response(answer, query)
            if not response_safe:
                logger.warning(f"Response blocked by guardrails: {response_reason}")
                answer = f"I need to be careful here. {response_reason}"

            sources = result.get("reranked_results", [])
            logger.info(f"Pipeline invocation successful")
            return answer, sources

        except Exception as e:
            logger.error(f"Pipeline invocation failed: {e}")
            raise


# Global pipeline instance
_pipeline_instance = None


def get_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance.

    Returns:
        RAGPipeline instance
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance


def ask_question(query: str, conversation_history: Optional[List] = None) -> tuple[str, List]:
    """Ask a question using the RAG pipeline.

    Args:
        query: User query
        conversation_history: Previous conversation messages

    Returns:
        Tuple of (answer, sources)
    """
    pipeline = get_pipeline()
    return pipeline.invoke(query, conversation_history)