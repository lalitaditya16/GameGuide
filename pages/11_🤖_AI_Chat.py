import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config

# Streamlit config
st.set_page_config(page_title="AI Game Chat", page_icon="🎮")
st.title("🤖 AI Game Assistant")
st.caption("Chat with an AI expert about the 2025 gaming landscape.")

# Strict prompt for 2025-based answers
today = datetime.now().strftime("%B %d, %Y")
SYSTEM_PROMPT = (
    f"Today's date is {today}. You are a helpful and concise gaming assistant. "
    "The current year is **2025** — always assume that when answering. "
    "Never refer to the year as 2023 or 2024 unless speaking in the past tense. "
    "Always say things like 'As of 2025' or 'Currently in 2025' when answering. "
    "Be confident and factual. Do not hedge or speculate unnecessarily."
)

# Groq LLM setup
llm = ChatGroq(
    groq_api_key=config.groq_api_key,
    model_name="whisper-large-v3",  # e.g., "mixtral-8x7b-32768"
    temperature=0,
    max_tokens=config.groq_max_tokens,
)

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show past messages
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# Chat input
if prompt := st.chat_input("Ask about 2025 games..."):
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("Thinking like it’s 2025..."):
            try:
                # Always prepend the system message freshly
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.chat_history
                response = llm(messages)
                st.session_state.chat_history.append(AIMessage(content=response.content))
                st.write(response.content)
            except Exception as e:
                st.error(f"Error from AI: {e}")

# Reset option
if st.button("🔄 Reset Conversation"):
    st.session_state.chat_history = []
    st.experimental_rerun()
