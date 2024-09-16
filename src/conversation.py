import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


# Function for version 0-2
def build_conversation(model_type, model_api, retriever):
    if model_type == 'Groq':
        llm = ChatGroq(model="mixtral-8x7b-32768", groq_api_key=model_api, temperature=0)
    else:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    
    contextualize_q_system_prompt ="""
    Given a chat history and the latest user question which might reference context in the chat history, \
    formulate a standalone question which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is.
    """
    
    
    ## Promp Template for question system
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
    
    ## store the retriever with the history inside (context)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    system_prompt = """
    You are an expert assistant, specialized in understanding PDF documents and answering questions contextually. \
    The user might ask follow-up questions. Always keep the document and previous interactions in mind when responding. \
    Use five sentences maximum and keep the answer concise.\
    
    {context}
    """
    
    qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
    
    # feed all retrieved context into the LLM
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    return rag_chain
    
    
    
def config_conversation(inference, model_api, retriever, model_type):
    ## Can add any model in it
    if inference == 'Groq':
        if model_type == 'Meta - Llama3':
            llm = ChatGroq(model="llama3-8b-8192", groq_api_key=model_api, temperature=0.5)
        else:
            llm = ChatGroq(model="gemma2-9b-it", groq_api_key=model_api, temperature=0.5)
        
    ## Create a memory and chain
    memory = ConversationBufferMemory(memory_key = "chat_history", return_messages = True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever = retriever,
        memory = memory
    )
    
    return conversation_chain