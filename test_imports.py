#!/usr/bin/env python3
"""Test script for RAG module imports."""

import sys
sys.path.insert(0, '.')

print('Testing module imports...\n')

modules = [
    ('config', 'from src.config import settings'),
    ('chatbot', 'from src.chatbot import get_chat_model'),
    ('vectorstore', 'from src.vectorstore import get_vectorstore'),
    ('rag', 'from src.rag import RAGPipeline'),
    ('guardrails', 'from src.guardrails import get_safety_guidelines'),
    ('ingest', 'from src.ingest import DocumentProcessor'),
    ('logger', 'from src.logger import logger'),
    ('utils', 'from src.utils import parse_query')
]

for name, import_stmt in modules:
    try:
        exec(import_stmt)
        print(f'✅ {name}.py loaded')
    except Exception as e:
        print(f'❌ {name}.py: {str(e)[:100]}')

print('\n✨ All modules tested!')
