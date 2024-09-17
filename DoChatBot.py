# Main Function
import os
import streamlit as st
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage

# Helper Function
from src.load_chunks import loadfile, docs_to_chunks
from src.vectorstore import config_retriever
from src.configchat import build_conversation, config_conversation

## ---------------------------------------- ##

# Load Environment variables
load_dotenv()
os.getenv("GROQ_API_KEY")


# Processing the Uploaded File
def processing(uploaded_file, inference, model_api, model_type):
    try:
        ## Extract
        doc = loadfile(uploaded_file)
        ## Split document to Chunks
        documents = docs_to_chunks(doc)
        ## Embed + vectorstore
        retriever = config_retriever(documents)
        
        return config_conversation(inference, model_api, retriever, model_type)
    except Exception as e:
        st.error("An error occurred during PDF processing. Please try again later.")
        return None


# Main Function
def main():   
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
        
    
    st.set_page_config(page_title="Q&A with Documents", page_icon="📜")
    st.title("📜Q&A with Documents")
    
    ## Add any model here.....
    inference = st.sidebar.selectbox("Inference", ['Groq'], index=None, placeholder='Inferencing...')
    model_type = st.sidebar.selectbox("LLM Models", ['Meta - Llama3', 'Google - Gemma2'], index=None, placeholder='Model Type...')
    
    if inference == 'Groq':
        model_api = st.sidebar.text_input("Groq API Key", type="password")
        st.sidebar.markdown("Don't have an API key? [Get it here](https://console.groq.com/keys)")
        if not model_api:
            st.info("Please add your **Groq API key** to continue.")
            st.stop()
    
        uploaded_file = st.sidebar.file_uploader(label="Upload PDF files", type=["pdf"], accept_multiple_files=True)
        
        if not uploaded_file:
            st.info("Please upload **PDF documents** to continue.")
            st.stop()

    
        if uploaded_file:
            with st.spinner("🚀Processing..."):
                st.session_state.conversation = processing(uploaded_file, inference, model_api, model_type)
            
            # Display chat interface if documents have been processed
            if user_query := st.chat_input(placeholder="Ask me anything about the document!"):    
                with st.spinner("💡Thinking..."):       
                    response = st.session_state.conversation({"question": user_query})
                    st.session_state.chat_history = response["chat_history"]

                    for i, message in enumerate(st.session_state.chat_history):
                        with st.chat_message("user" if i % 2 == 0 else "assistant"):
                            st.markdown(message.content)
            
        reset_conversation = st.sidebar.button("⚙️Reset Session")
        if reset_conversation:
            with st.spinner("🥱Resetting..."):
                st.session_state.conversation = None
                st.session_state.chat_history = None
            
    
if __name__ == "__main__":
    main()