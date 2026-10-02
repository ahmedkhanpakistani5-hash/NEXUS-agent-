import streamlit as st


def get_groq_api_key() -> str:
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        return str(key).strip()
    except Exception:
        return ""


def get_groq_model() -> str:
    try:
        return str(st.secrets.get("GROQ_MODEL", "openai/gpt-oss-20b")).strip()
    except Exception:
        return "openai/gpt-oss-20b"
