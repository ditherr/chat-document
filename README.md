<h1 align="center">💎DoChatBot💎</h1>
<h4 align="center">"Let's chat with your <b>Documents </b>"</h4>

## 🚀 About DoChatBot
DoChatBot is a Web-app ChatBot that allows users to interact with documents that they have uploaded. Users can ask questions that are appropriate to the contents of the document, and bots assisted by the LLM model will answer these questions.

⚠️(+) You need to have a **Groq API Key** to be able chat with the DoChatBot.


https://github.com/user-attachments/assets/c03c5b9e-18b6-4fd5-ad7a-78c3b2592924



<p align="center">
  <a href="https://do-chatbot.app/"></a>
</p>

### 🔧 How does it work?
<p>
This is an Implementation of the RAG (Retrieval-Augmented Generation) that is built with Streamlit and it encapsulates a comprehensive Python environment that includes all necessary libraries. The Web-App also playing with Inferencing <a href='https://console.groq.com/docs'>(Groq)</a>, <a href='https://python.langchain.com/docs/introduction/'>Langchain</a>, and LLM models (Llama3 and Gemma2) to provide everything inside such as connect to LLM model, storing session and chat memory, prompting the task, etc.
</p>

## 👑Streamlit Application
🔗: [📜 DoChatBot](https://dochatbott.streamlit.app/)

## ⚙️Requirements & Installation
- `Requirements`, you need a **GROQ_API_KEY** to use the Groq inference.
- `Installation`, the packages and libraries required in the `requirements.txt` file.

### ⚙️Interact with the Project
1. **Clone the repository**
    ```
    git clone https://github.com/ditherr/chat-document.git
    ````
2. Navigate to the repository
3. **Create and Activate Environment**
    ```
    conda create -p venv python==3.10.12 -y
    conda activate venv/
    ```
4. **Install The Requirements**
    ```
    pip install -r requirements.txt
    ```
5. **Run the Application**
    ```
    streamlit run app.py
    ```

### 👑Streamlit Secrets Key
This part is adding a secret API key by using **Streamlit Secrets**, it similar with the `.env` or how `os.getenv()` works to get the secret API keys from the environment.  We can store any secret keys or variables securely there (in this project it is `GROQ_API_KEY`).

If you want to use it, please add it in `secrets.toml` file. For more detail how to create this Secrets Key, you can read the documentation here: [Secrets Management](https://docs.streamlit.io/develop/concepts/connections/secrets-management)

## Additional Features
- Audio to Text
- Add other API_KEY (OpenAI, Gemini, etc)
- Offline models

*(More features will be updated)*
