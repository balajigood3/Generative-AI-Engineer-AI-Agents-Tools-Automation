import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from app.agent import run_agent
from app.document_loader import extract_text
from app.rag import InMemoryVectorStore, chunk_text

load_dotenv()
st.set_page_config(page_title="Career & Research Copilot", page_icon="🧠", layout="wide")

st.title("Career & Research Copilot")
st.caption("GenAI capstone · LLM + prompt engineering + RAG + tools + agent workflow")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Copy .env.example to .env and add your NEW API key.")
    st.stop()

client = OpenAI(api_key=api_key)
chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = InMemoryVectorStore()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()

with st.sidebar:
    st.header("Knowledge base")
    uploads = st.file_uploader(
        "Upload documents", type=["pdf", "docx", "txt", "md"], accept_multiple_files=True
    )
    if st.button("Index uploaded documents", type="primary", disabled=not uploads):
        added = 0
        for uploaded in uploads:
            if uploaded.name in st.session_state.indexed_files:
                continue
            try:
                text = extract_text(uploaded.name, uploaded.getvalue())
                chunks = chunk_text(text, uploaded.name)
                added += st.session_state.vector_store.add_documents(
                    client, chunks, embedding_model
                )
                st.session_state.indexed_files.add(uploaded.name)
            except Exception as exc:
                st.error(f"{uploaded.name}: {exc}")
        st.success(f"Indexed {added} text chunks.")
    st.write(f"Indexed files: {len(st.session_state.indexed_files)}")
    st.caption("Files are held in session memory and are not persisted.")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about your documents, career, research or code...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching your knowledge base..."):
            try:
                retrieved = st.session_state.vector_store.search(
                    client, prompt, embedding_model, top_k=4
                )
                answer = run_agent(
                    client, st.session_state.messages, retrieved, chat_model
                )
            except Exception as exc:
                answer = f"Request failed: {exc}\n\nCheck your API key, quota and network connection."
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
