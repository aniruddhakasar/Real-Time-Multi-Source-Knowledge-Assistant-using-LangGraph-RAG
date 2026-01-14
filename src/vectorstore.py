from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings
from src.config import EMBEDDING_MODEL, VECTOR_DB

def get_vectorstore():
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    if VECTOR_DB == "faiss":
        # Assuming index exists or create new
        try:
            vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        except:
            vectorstore = FAISS.from_texts([""], embeddings)  # Placeholder
    elif VECTOR_DB == "chroma":
        vectorstore = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")
    return vectorstore
    return vectorstore