from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from src.vectorstore import get_vectorstore
from src.chatbot import get_chat_model
from src.config import CROSS_ENCODER_MODEL
from sentence_transformers import CrossEncoder
import requests

# State
class GraphState:
    query: str
    intent: str
    vector_results: list = []
    web_results: list = []
    follow_up: str = ""
    reranked_results: list = []
    answer: str = ""
    memory: list = []

# Nodes
def intent_classifier(state):
    query = state["query"]
    # Simple classification
    if "search" in query.lower() or "web" in query.lower():
        intent = "web_search"
    elif "follow" in query.lower():
        intent = "follow_up"
    else:
        intent = "vector_rag"
    return {"intent": intent}

def vector_rag_node(state):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(state["query"])
    return {"vector_results": docs}

def web_search_node(state):
    # Simple web search using requests, or use tavily
    # Placeholder
    results = ["Web result 1", "Web result 2"]
    return {"web_results": results}

def follow_up_node(state):
    # Ask follow-up
    follow_up = "Can you provide more details?"
    return {"follow_up": follow_up}

def reranker_node(state):
    results = state["vector_results"] + state["web_results"]
    if results:
        encoder = CrossEncoder(CROSS_ENCODER_MODEL)
        scores = encoder.predict([(state["query"], doc.page_content if hasattr(doc, 'page_content') else doc) for doc in results])
        reranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
        return {"reranked_results": [doc for doc, _ in reranked[:5]]}
    return {"reranked_results": results}

def answer_generator_node(state):
    llm = get_chat_model()
    context = "\n".join([doc.page_content if hasattr(doc, 'page_content') else doc for doc in state["reranked_results"]])
    prompt = f"Answer the question based on the context: {context}\nQuestion: {state['query']}"
    answer = llm.invoke(prompt).content
    return {"answer": answer}

def memory_update_node(state):
    state["memory"].append({"query": state["query"], "answer": state["answer"]})
    return state

# Graph
def create_graph():
    graph = StateGraph(GraphState)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("vector_rag", vector_rag_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("follow_up", follow_up_node)
    graph.add_node("reranker", reranker_node)
    graph.add_node("answer_generator", answer_generator_node)
    graph.add_node("memory_update", memory_update_node)

    graph.set_entry_point("intent_classifier")

    graph.add_conditional_edges(
        "intent_classifier",
        lambda state: state["intent"],
        {
            "vector_rag": "vector_rag",
            "web_search": "web_search",
            "follow_up": "follow_up"
        }
    )

    graph.add_edge("vector_rag", "reranker")
    graph.add_edge("web_search", "reranker")
    graph.add_edge("follow_up", "reranker")
    graph.add_edge("reranker", "answer_generator")
    graph.add_edge("answer_generator", "memory_update")
    graph.add_edge("memory_update", END)

    return graph.compile()

def ask_question(query):
    graph = create_graph()
    result = graph.invoke({"query": query})
    return result["answer"], result["reranked_results"]