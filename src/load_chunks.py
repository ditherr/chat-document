## All functional helper
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def loadfile(uploaded_files):
    docs = []
    temp_dir = tempfile.TemporaryDirectory() ## create a temporary directory
    for file in uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.name) ## create a temporary file
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
            
        loader = PyPDFLoader(temp_filepath) ## Load the file
        docs = loader.load()
        docs.extend(docs)
    
    return docs
    

def docs_to_chunks(doc):
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = text_splitter.split_documents(doc)

    return chunks