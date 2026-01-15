# 🚀 Expert RAG Chatbot - Production-Grade Knowledge Assistant | v2.0

© 2026 Aniruddha Kasar | All Rights Reserved

A professional-grade Retrieval-Augmented Generation (RAG) system designed for expert-level code assistance and complex technical problem-solving using advanced AI architectures.

## 🎯 Overview

This is a **production-ready RAG chatbot** that combines:
- **LangGraph-based agentic workflows** for intelligent routing
- **Multi-source document ingestion** (PDFs, web, APIs, databases)
- **Advanced vector retrieval** with cross-encoder re-ranking
- **Professional-grade guardrails** for safe, responsible AI
- **Enterprise logging** and performance monitoring
- **Persistent session management** with analytics
- **Expert specialization** for different coding domains

Perfect for:
- 🖥️ Complex software engineering tasks
- 🐛 Advanced debugging and problem-solving
- 🏗️ Architecture and system design
- 📚 Code documentation and learning
- ⚡ Performance optimization guidance

## ✨ Key Features

### Intelligence & Expertise
- **Expert Chatbot Class**: Specialized responses for coding, debugging, architecture
- **Intent Classification**: Automatically detects query type (search, coding, explanation, debug)
- **Cross-Encoder Re-ranking**: Top-K document re-ranking for maximum relevance
- **Conversation Memory**: Maintains context across multi-turn interactions
- **Confidence Scoring**: Returns relevance metrics with each response

### Safety & Responsibility  
- **Advanced Guardrails**: Content filtering similar to ChatGPT
- **Query Validation**: Blocks harmful queries before processing
- **Response Validation**: Ensures responses meet safety standards
- **Audit Logging**: Complete audit trail of all interactions
- **Configurable Policies**: Customize safety rules per organization

### Production Quality
- **Comprehensive Logging**: Structured logging for debugging and monitoring
- **Performance Tracking**: Response time and accuracy metrics
- **Error Handling**: Graceful error recovery and user feedback
- **Caching**: Optimized performance with `@lru_cache` decorators
- **Configuration Management**: Pydantic-based settings with validation
- **Type Hints**: Full type annotations for IDE support

### Enterprise Features
- **Multi-tab Analytics Dashboard**: Real-time system metrics
- **Session Persistence**: JSON-based session storage with recovery
- **Batch Document Ingestion**: Process multiple sources efficiently
- **RAGAS Evaluation**: Built-in evaluation metrics (Faithfulness, Relevance, Precision)
- **Configurable Models**: Switch between GPT-4, GPT-4-Turbo, GPT-3.5
- **Cost Tracking**: Monitor API usage and costs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)                 │
│        Chat | Analytics | Safety | Settings             │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│         RAG Pipeline (src/rag.py)                        │
│  ┌─────────────┬─────────────┬──────────┬──────────┐    │
│  │ Intent      │ Vector RAG  │ Re-ranker│ Answer   │    │
│  │ Classifier  │ Retrieval   │ (Cross)  │ Generator│    │
│  └─────┬───────┴─────────────┴──────────┴──────────┘    │
│        │  ┌─────────────┐                               │
│        └──▶ Guardrails  │ (Content Safety)              │
│           └─────────────┘                               │
└──────────────────┬──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬─────────────┐
    │              │              │             │
┌───▼──┐   ┌──────▼──┐  ┌────────▼──┐  ┌──────▼──┐
│Expert│   │Vector   │  │Document   │  │Session  │
│Chat  │   │Store    │  │Processor  │  │Manager  │
│Model │   │(FAISS)  │  │(ingest)   │  │(JSON)   │
│      │   │         │  │           │  │         │
└──────┘   └─────────┘  └───────────┘  └─────────┘

Core Modules:
- config.py: Pydantic settings with validation
- chatbot.py: ExpertChatbot class with specializations
- vectorstore.py: VectorStoreManager abstraction layer
- rag.py: RAGPipeline with LangGraph workflows
- guardrails.py: ContentGuardrails for safety
- ingest.py: DocumentProcessor for multi-format ingestion
- logger.py: Centralized logging with performance tracking
- utils.py: Shared utilities and constants
```

## 📋 File Structure

```
RAG/
├── app.py                    # Streamlit web interface (refactored)
├── requirements.txt          # Dependencies with pinned versions
├── .env                      # API keys and configuration
├── .gitignore               # Git ignore patterns
├── README.md                # This file
├── data/                    # Documents for ingestion
│   ├── code_examples/
│   ├── documentation/
│   └── tutorials/
├── chat_sessions/           # Persistent session storage
│   ├── session_1.json
│   ├── session_2.json
│   └── counter.json
├── logs/                    # Application logs
│   ├── rag_system.log
│   └── error.log
└── src/
    ├── __init__.py
    ├── config.py            # Pydantic Settings (UPGRADED)
    ├── chatbot.py           # ExpertChatbot class (UPGRADED)
    ├── vectorstore.py       # VectorStoreManager (UPGRADED)
    ├── rag.py               # RAGPipeline with LangGraph (UPGRADED)
    ├── guardrails.py        # ContentGuardrails system
    ├── ingest.py            # DocumentProcessor (NEW)
    ├── logger.py            # Logging utilities (NEW)
    └── utils.py             # Shared constants and helpers (NEW)
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | OpenAI GPT-4-Turbo | Expert-level responses |
| **Embeddings** | text-embedding-ada-002 | Dense vector representations |
| **Re-ranking** | Cross-Encoder (MiniLM-L-12-v2) | Relevance optimization |
| **Vector DB** | FAISS (primary), Pinecone (fallback) | Efficient similarity search |
| **Framework** | LangChain + LangGraph | Agentic workflows |
| **UI** | Streamlit | Web interface |
| **Backend** | FastAPI | REST API (optional) |
| **Config** | Pydantic | Type-safe settings |
| **Logging** | Python logging | Structured logs |
| **Storage** | JSON + FAISS | Sessions + vectors |

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repo>
cd RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
TAVILY_API_KEY=optional_for_web_search
PINECONE_API_KEY=optional_for_pinecone
```

### 3. Document Ingestion

```python
from src.ingest import ingest_directory, batch_ingest

# Ingest from directory
result = ingest_directory("data/", pattern="*.txt")

# Or batch ingest multiple sources
sources = [
    {"path": "data/docs.pdf", "type": "file", "source": "docs", "category": "documentation"},
    {"path": "data/code/", "type": "directory", "pattern": "*.py", "source": "code"}
]
results = batch_ingest(sources)
```

### 4. Launch Application

```bash
streamlit run app.py
```

Access at: http://localhost:8501

## 💻 Usage Examples

### Interactive Chat
```
User: "How do I optimize a Python for loop with numpy?"
Assistant: [Expert response with code examples and performance tips]
```

### Testing Guardrails
Go to **🛡️ Safety & Guidelines** tab → **Test Guardrails** → Enter query

### Viewing Analytics
Go to **📊 Analytics** tab to see:
- System uptime and health
- Query distribution by type
- Response time trends
- User engagement metrics

### Managing Sessions
- **Create new** via "➕ New Chat" button
- **Switch** by clicking session in sidebar
- **Delete** old sessions via 🗑️ button
- Auto-saves every message

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
TAVILY_API_KEY=tvly-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=production
PINECONE_NAMESPACE=main

# Model Selection
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-ada-002
CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2

# RAG Parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
RERANKING_THRESHOLD=0.5

# System
LOG_LEVEL=INFO
DEBUG_MODE=false
```

### Pydantic Settings (`src/config.py`)
```python
from src.config import settings

print(settings.llm_model)
print(settings.chunk_size)
print(settings.top_k_results)
```

## 🛡️ Safety & Guardrails

### How Guardrails Work

1. **Query Validation**: Checks user input against restricted categories
2. **Content Filtering**: Blocks queries about violence, illegal activities, etc.
3. **Response Validation**: Ensures LLM response is safe before returning
4. **Logging**: Audit trail of blocked/modified content
5. **Educational Exception**: Allows safe educational discussions

### Testing Guardrails

```python
from src.guardrails import check_query, check_response

# Test a query
is_safe, reason, metadata = check_query("How do I write secure Python code?")
# Output: (True, "Query is safe", {...})

# Test a response
is_safe, reason, metadata = check_response(response_text, original_query)
```

### Restricted Categories

- ❌ Violence and terrorism
- ❌ Illegal activities and hacking
- ❌ Child exploitation
- ❌ Hate speech and discrimination
- ❌ Controlled substance manufacturing
- ❌ Privacy violations

### Allowed Contexts

- ✅ Software engineering education
- ✅ Code optimization and best practices
- ✅ Architectural guidance
- ✅ Debugging and troubleshooting
- ✅ Historical and academic discussions

## 📊 Analytics & Monitoring

### Dashboard Metrics
- System availability and uptime
- Query count and types
- Average response time
- Data source distribution
- User engagement trends

### Performance Tracking
```python
from src.logger import tracker

tracker.start("my_operation")
# ... do work ...
elapsed = tracker.end("my_operation")  # Logs timing
```

### Logging Example
```python
from src.logger import logger

logger.info("Processing user query")
logger.warning("Slow response time: 2.5s")
logger.error("Vector store connection failed")
```

## 🧪 Testing & Evaluation

### RAGAS Evaluation
```python
from ragas import evaluate
from ragas.metrics import faithfulness, relevance, precision

result = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, relevance, precision]
)
print(result)
```

## 📈 Production Deployment

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Scaling Considerations
- Use Pinecone or other cloud vector DB for distributed retrieval
- Deploy FastAPI backend separately for API access
- Implement caching for frequently asked questions
- Use Redis for session caching
- Monitor with OpenTelemetry or DataDog

## 🔐 Security Best Practices

1. **API Keys**: Store in `.env`, never commit
2. **Sessions**: Encrypted JSON storage
3. **Logging**: No sensitive data in logs
4. **HTTPS**: Use in production
5. **Rate Limiting**: Implement to prevent abuse
6. **Input Validation**: All user inputs validated
7. **Output Sanitization**: Responses escaped for HTML

## 🤝 Contributing

Contributions welcome! Please:
1. Follow code style (Black formatting, type hints)
2. Add tests for new features
3. Update documentation
4. Create detailed PR descriptions

## 📝 License

© 2026 Aniruddha Kasar | All Rights Reserved

## 🙏 Acknowledgments

- Built with LangChain, LangGraph, and OpenAI
- UI by Streamlit
- Icons from Emoji & Unicode
- Community support and feedback

---

**For support, issues, or feature requests**: [GitHub Issues]

### 💬 Chat Features
- **Session Management**: Create, switch, and delete chat sessions
- **Persistent Storage**: Conversations survive app restarts
- **Multi-Source RAG**: Combines vector search with web results
- **Memory Integration**: Context-aware responses using conversation history

## Architecture

```
User Query
   ↓
🛡️ Safety Check (Guardrails)
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
🛡️ Response Safety Check
   ↓
Memory Update Node
```

## Project Structure

- `src/`: Source code
  - `config.py`: Configuration settings
  - `vectorstore.py`: Vector database setup (Pinecone/FAISS)
  - `chatbot.py`: LLM setup and chat models
  - `rag.py`: LangGraph RAG pipeline with guardrails integration
  - `guardrails.py`: High-level safety and content guidelines
- `data/`: Documents for ingestion
- `chat_sessions/`: Persistent chat session storage (JSON files)
- `app.py`: Streamlit web interface with safety tab
- `ingest.py`: Document ingestion script
- `requirements.txt`: Python dependencies