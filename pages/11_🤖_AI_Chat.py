import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config

# ──────────────────────────────────────────────
st.set_page_config(page_title="AI Game Chat", page_icon="🤖")
st.title("🤖 AI Game Assistant")
st.write("Chat with a fast AI about games, trends, recommendations, and industry news. Ask anything!")

# System prompt with strict 2025 context and guidance
today = datetime.now().strftime("%B %d, %Y")  # e.g., "July 30, 2025"
SYSTEM_PROMPT = (
    f"Today's date is {today}. You are a highly knowledgeable, helpful, and concise AI assistant who specializes in video games. "
    "Always assume the current year is 2025, regardless of the actual date. Your responses should reflect up-to-date knowledge, as if it is mid-2025. "
    "In your answers, use phrasing such as 'As of 2025...' or 'Currently in 2025...' to reassure the user that your responses are grounded in the current year. "
    "Do not mention older years like 2023 or 2024 unless referring to past releases."
)

# ────────── Groq LLM Setup (strict/deterministic)
llm = ChatGroq(
    groq_api_key=config.groq_api_key,
    model_name=config.groq_model,
    temperature=0,  # deterministic
    max_tokens=config.groq_max_tokens,
)

# Initialize chat history (excluding system prompt)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show chat history (exclude system prompt from visible chat)
def display_chat():
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

display_chat()

# ────────── Handle user input
if prompt := st.chat_input("Ask me anything about games..."):
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("Thinking like it's 2025..."):
            try:
                # Prepend system prompt each time for reliability
                full_chat = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.chat_history
                reply = llm(full_chat)
                st.session_state.chat_history.append(AIMessage(content=reply.content))
                st.write(reply.content)
            except Exception as e:
                st.error(f"AI error: {e}")

# ────────── Optional: Reset conversation
if st.button("Reset conversation"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# Optional: Welcome note
st.caption("Ask about 2025's top games, upcoming releases, or gaming trends!")
