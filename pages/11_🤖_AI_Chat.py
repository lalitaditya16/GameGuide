import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config

st.set_page_config(page_title="AI Game Chat", page_icon="🤖")
st.title("🤖 AI Game Assistant")
st.write("Chat with a fast AI about games, trends, recommendations, and industry news. Ask anything!")

# System prompt
SYSTEM_PROMPT = (
    "Today's date is July 30, 2025. You are a gaming expert AI assistant. "
    "You must always assume the current year is 2025. Answer accordingly. "
    "Be concise, helpful, and context-aware about recent game trends and titles."
)

# ────────── Groq LLM Setup ──────────
llm = ChatGroq(
    groq_api_key=config.groq_api_key,
    model_name=config.groq_model,
    temperature=config.groq_temperature,
    max_tokens=config.groq_max_tokens,
)

# ────────── Session State Setup ──────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]

# ────────── Display Chat ──────────
for msg in st.session_state.chat_history[1:]:  # skip system message display
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    st.chat_message(role).write(msg.content)

# ────────── Input Handling ──────────
if prompt := st.chat_input("Ask me anything about games..."):
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("Thinking like it's 2025..."):
            try:
                reply = llm(st.session_state.chat_history)
                st.session_state.chat_history.append(AIMessage(content=reply.content))
                st.write(reply.content)
            except Exception as e:
                st.error(f"AI error: {e}")

# ────────── Reset Button ──────────
if st.button("Reset conversation"):
    st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]
    st.experimental_rerun()
