# Real-Time Multi-Source Knowledge Assistant using LangGraph RAG

A real-time RAG system using LangChain + LangGraph for agentic workflows, enabling grounded question answering over multi-source knowledge bases.

## Features

- **Multi-Source Ingestion**: PDFs, web pages, markdown, APIs
- **Adaptive Chunking**: Semantic and recursive chunking
- **Hybrid Retrieval**: Dense embeddings with re-ranking
- **Agentic Routing**: LangGraph for conditional query routing
- **Memory**: Conversation history
- **Evaluation**: RAGAS metrics

## Tech Stack

- **Framework**: LangChain + LangGraph
- **LLM**: GPT-4 (OpenAI)
- **Embeddings**: SentenceTransformers
- **Vector DB**: FAISS / Chroma
- **Backend**: FastAPI
- **UI**: Streamlit
- **Evaluation**: RAGAS

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up API keys in `.env`:
   - OPENAI_API_KEY: Your OpenAI API key
   - TAVILY_API_KEY: Optional for web search

3. Ingest documents:
   Place files in `data/` directory, URLs in `urls.txt`, then run:
   ```
   python ingest.py
   ```

4. Run the assistant:
   ```
   streamlit run app.py
   ```

## Architecture

```
User Query
   ↓
Intent Classifier Node
   ↓
Router (LangGraph Conditional Edge)
   ├── Vector RAG Node
   ├── Web Search Node
   └── Follow-up Question Node
   ↓
Re-ranker Node
   ↓
Answer Generator Node
   ↓
Memory Update Node
```

## Project Structure

- `src/`: Source code
  - `config.py`: Configuration
  - `vectorstore.py`: Vector database setup
  - `chatbot.py`: LLM setup
  - `rag.py`: LangGraph RAG pipeline
- `data/`: Documents for ingestion
- `app.py`: Streamlit UI
- `ingest.py`: Ingestion script
- `requirements.txt`: Dependencies