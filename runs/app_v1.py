import os
import streamlit as st
import tempfile
import asyncio
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

## Helper Function
from helper import configure_retriever, PrintRetrievalHandler, StreamHandler

## ---------------------------------------- ##

## Load Environment
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')


## Configure the Retriever
def config_retriever(uploaded_file):
    docs = []
    temp_dir = tempfile.TemporaryDirectory() ## create a temporary directory
    for file in uploaded_file:
        temp_filepath = os.path.join(temp_dir.name, file.name) ## create a temporary file
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
            
        loader = PyPDFLoader(temp_filepath) ## Load the file
        docs = loader.load()
        docs.extend(docs)
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # Store in Chroma Vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(splits, embeddings)
    retriever = vectordb.as_retriever()
    
    return retriever

    
## Configure the Chain for Question-answer
async def config_qa(llm, retriever, question):
    # Create a chain
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    
    ## Promp Template for question system
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ]
        )
    
    ## store the retriever with the history inside (context)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # Define system prompt template
    system_prompt = """
    You are an expert assistant, specialized in understanding PDF documents and answering questions contextually.
    The user might ask follow-up questions. Always keep the document and previous interactions in mind when responding.
    Use three sentences maximum and keep the answer concise.
    \n
    {context}.
    """
    
    qa_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ]
        )
    
    # Create a document processing chain
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt) ## all documents sent to the model (LLM)
    
    # Combine the retriever with the chain
    qa_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Get response asynchronously
    response = await qa_chain.run(question)
    
     # Initialize chat history if not done yet
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # Append the current question and response to the session history
    st.session_state["chat_history"].append({"question": question, "response": response})
    
    return response


def main():    
    st.set_page_config(page_title="Chat with Documents", page_icon="📜")
    st.title("📜 Chat with Documents")
    
    
    api_radio = ["Groq", "Google Gemini"] 
    selected_opt = st.sidebar.radio(label="Choose the Model API...", options=api_radio) 
    
    if api_radio.index(selected_opt) == 0:
        groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
        if not groq_api_key:
            st.info("Please add your Groq API key to continue.")
            st.stop()
    else:
        gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
        if not gemini_api_key:
            st.info("Please add your Google API key to continue.")
            st.stop()
            
    ## Setup LLM and QA chain
    if api_radio.index(selected_opt) == 0:
        llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key, temperature=0)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        
    ## 1. Load document
    uploaded_files = st.sidebar.file_uploader(label="Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if not uploaded_files:
        st.info("Please upload PDF documents to continue.")
        st.stop()


    retriever = config_retriever(uploaded_files)
    

    ## input for user
    if user_query := st.chat_input(placeholder="Ask me anything about the document!"):
        # User's query
        st.chat_message("user").write(user_query)
        
        ## Assistant is responses
        with st.chat_message("assistant"):
            # Run the async function using asyncio's event loop
            response = asyncio.create_task(config_qa(llm, retriever, user_query))

            # Wait for the task to complete and fetch the result
            response_result = asyncio.run(response)  # This will block until the async function completes
            # response = await config_qa(llm, retriever, user_query)
            
            st.write(f"Assistant: {response_result}")
            # st.write(f"History: {st.session_state['chat_history']}")
            
            if "chat_history" in st.session_state:
                st.write("Chat History:")
                for entry in st.session_state["chat_history"]:
                    st.write(f"User: {entry['question']}")
                    st.write(f"Assistant: {entry['response']}")
    
        
    

if __name__ == "__main__":
    main()