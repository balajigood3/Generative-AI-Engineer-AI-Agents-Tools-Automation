# Architecture Notes

## Request lifecycle
1. Streamlit receives a user query and maintains the conversation in session state.
2. Uploaded files are parsed by `document_loader.py`.
3. `rag.py` normalizes and chunks text, requests embeddings, and stores vectors in memory.
4. The query is embedded and cosine similarity selects the top four chunks.
5. `agent.py` combines the prompt, conversation and retrieved excerpts.
6. The model may call the calculator tool. The application executes the restricted function and returns its result to the model.
7. The final answer is displayed in Streamlit. The system prompt asks the model to identify source filenames and avoid fabricated citations.

## Components
- UI: Streamlit
- LLM: OpenAI chat completions API
- Embeddings: OpenAI `text-embedding-3-small`
- Retrieval: NumPy cosine similarity, in-memory
- Agent tools: restricted arithmetic calculator
- Parsing: pypdf and python-docx

## Production limitations
This is a capstone starter, not a hardened enterprise service. It has no authentication, durable vector database, OCR, tenant isolation, background jobs or comprehensive observability. Add these before handling sensitive or high-volume workloads.
