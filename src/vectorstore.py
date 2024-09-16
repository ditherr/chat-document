from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def config_retriever(documents):
    # Create embeddings and store in vectordb
    model_embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(documents=documents, embedding=model_embed)
    retriever = vectordb.as_retriever()
    
    return retriever