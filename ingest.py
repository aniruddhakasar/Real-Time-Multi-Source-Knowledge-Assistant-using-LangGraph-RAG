from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from src.vectorstore import get_vectorstore
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
from langchain_openai import OpenAIEmbeddings
import os

def ingest_documents(data_dir="data"):
    vectorstore = get_vectorstore()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    
    # Adaptive chunking
    semantic_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    
    documents = []
    
    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_dir, file))
            docs = loader.load()
            documents.extend(docs)
        elif file.endswith(".md") or file.endswith(".txt"):
            loader = TextLoader(os.path.join(data_dir, file))
            docs = loader.load()
            documents.extend(docs)
    
    # For web, assume URLs in a file
    if os.path.exists("urls.txt"):
        with open("urls.txt") as f:
            urls = f.read().splitlines()
        for url in urls:
            loader = WebBaseLoader(url)
            docs = loader.load()
            documents.extend(docs)
    
    # Chunk
    chunks = []
    for doc in documents:
        # Use semantic or recursive
        if len(doc.page_content) > 2000:
            chunks.extend(semantic_splitter.split_documents([doc]))
        else:
            chunks.extend(recursive_splitter.split_documents([doc]))
    
    vectorstore.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks")

if __name__ == "__main__":
    ingest_documents()