import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Models
LLM_MODEL = "gpt-4"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Vector DB
VECTOR_DB = "faiss"  # or "chroma"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200