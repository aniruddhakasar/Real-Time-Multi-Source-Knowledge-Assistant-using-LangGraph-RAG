from langchain_openai import ChatOpenAI
from src.config import LLM_MODEL

def get_chat_model():
    llm = ChatOpenAI(model=LLM_MODEL)
    return llm