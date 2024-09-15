## Main application runner

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Chaining Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory, StreamlitChatMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# Model LLM + Embedding
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

## Helper Function
from helper import configure_retriever, PrintRetrievalHandler, StreamHandler

## ------------------------------------- ##

## Load Env - Embeeding - Model
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def main():
    st.set_page_config(page_title="Chat with Documents", page_icon="📜")
    st.title("📜 Chat with Documents")
    
    api_radio = ["Groq", "Google Gemini"] 
    selected_opt = st.sidebar.radio(label="Choose the API that you have...", options=api_radio) 
    
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
    
    ## 1. Load document
    uploaded_files = st.sidebar.file_uploader(label="Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if not uploaded_files:
        st.info("Please upload PDF documents to continue.")
        st.stop()
    
    ## 2. Configure retriever (chunks, embed, vectorstore)
    retriever = configure_retriever(uploaded_files)
    
    ## Setup LLM and QA chain
    if api_radio.index(selected_opt) == 0:
        llm = ChatGroq(model="llama3-8b-8192", groq_api_key=groq_api_key, temperature=0)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        
    ## chat interface
    session_id = st.text_input("Session ID", value="default_session") ## session_id
    
    ## statefully manage chat history
    if 'store' not in st.session_state:
        st.session_state.store = {} ## store all the information for each session
    
    ## Create a chain
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question"
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        ) # Promp Template for question system
    
    ## store the retriever with the history inside (context)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # Answer question
    system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
    
    qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt) ## all documents sent to the model (LLM)
    qa_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain) ## final rag-chain
    
    ## Function to get and store the session_id
    def get_session_history(session:str) -> BaseChatMessageHistory:
        if session_id not in st.session_state.store:
            st.session_state.store[session_id] = ChatMessageHistory()
        return st.session_state.store[session_id]
        
    ## Final chain to include all the important step
    conversational_rag_chain = RunnableWithMessageHistory(
        qa_chain, ## final chain
        get_session_history, ## get the session_id
        input_messages_key="input", ## user input
        history_messages_key="chat_history", ## store the question in chat_history
        output_messages_key="answer" ## provide the answer based on the input/question
    )
    
    # msgs = StreamlitChatMessageHistory()
    
    # ## Start message
    # if len(msgs.messages) == 0 or st.sidebar.button("Clear message history"):
    #     msgs.clear()
    #     msgs.add_ai_message("How can I help you?")
    
    # ## chat message type
    # avatars = {"human": "user", "ai": "assistant"}
    # for msg in msgs.messages:
    #     st.chat_message(avatars[msg.type]).write(msg.content)
    
    ## input for user
    if user_query := st.chat_input(placeholder="Ask me anything!"):
        st.chat_message("user").write(user_query)
        session_history = get_session_history(session_id)
        
        ## Assistant is responses
        with st.chat_message("assistant"):
            response = conversational_rag_chain.invoke(
                {"input": user_query},
                config = {"configurable": {"session_id": session_id}},
            )
            
            st.write(st.session_state.store)
            st.write("Assistant:", response['answer'])
            st.write("Chat History:", session_history.messages)
            
            # response = qa_chain({"question": user_query, "chat_history": msgs.messages})
    else:
        st.write("Waiting for user input...")
    
if __name__ == "__main__":
    main()
