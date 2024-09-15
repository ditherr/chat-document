## All functional helper
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Chaining Document
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Model Embedding
from langchain_huggingface import HuggingFaceEmbeddings

# Split Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks.base import BaseCallbackHandler

## ------------------------------------- ##

def configure_retriever(uploaded_files):
    docs = []
    temp_dir = tempfile.TemporaryDirectory() ## create a temporary directory
    for file in uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.name) ## create a temporary file
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
            
        loader = PyPDFLoader(temp_filepath) ## Load the file
        docs = loader.load()
        docs.extend(docs)
    
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Create embeddings and store in vectordb
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # by using HF it will take time to embed the documents
    vectordb = Chroma.from_documents(documents=splits, embedding=embeddings)

    # Define retriever
    retriever = vectordb.as_retriever()
    # retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 1, "fetch_k": 4})
    
    return retriever



## A callback handler for printing retrieval results.
class PrintRetrievalHandler(BaseCallbackHandler):
    def __init__(self, container):
        ## Initializes the handler with a container for displaying status updates.
        self.status = container.status("**Context Retrieval**")

    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        ## Called when the retriever starts. Writes the query to the status container.
        self.status.write(f"**Question:** {query}")
        self.status.update(label=f"**Context Retrieval:** {query}")

    def on_retriever_end(self, documents, **kwargs):
        ## Called when the retriever ends. Writes the retrieved documents to the status container.
        for idx, doc in enumerate(documents):
            source = os.path.basename(doc.metadata["source"])
            self.status.write(f"**Document {idx} from {source}**")
            self.status.markdown(doc.page_content)
        self.status.update(state="complete")


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.delta_generator.DeltaGenerator, initial_text: str = ""):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # Workaround to prevent showing the rephrased question as output
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # Handle the new token generated by the LLM
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.text += token
        self.container.markdown(self.text)