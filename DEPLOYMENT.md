# Deployment Guide

## Streamlit Community Cloud
- Push the project to a GitHub repository.
- Create a Streamlit Community Cloud app and point it to `streamlit_app.py`.
- Add `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, and `OPENAI_EMBEDDING_MODEL` in app Secrets.
- Deploy and verify the health of the app with a non-sensitive test document.

## Other hosting
The app can run anywhere that supports Python and Streamlit. Install `requirements.txt`, inject environment variables through the platform's secret manager, and run:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

Do not bake API keys into Docker images or source control.
