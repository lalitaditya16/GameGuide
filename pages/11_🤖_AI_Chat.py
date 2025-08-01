import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config

# ──────────────────────────────────────────────
st.set_page_config(page_title="AI Game Chat", page_icon="🤖")
st.title("🤖 AI Game Assistant")
st.write("Chat with a fast AI about games, trends, recommendations, and industry news. Ask anything!")

# System prompt with current date for real-world responses
today = datetime.now().strftime("%B %d, %Y")  # e.g., "July 31, 2025"
SYSTEM_PROMPT = (
    f"Today's date is {today}. You are a gaming expert AI assistant. Be helpful, concise, "
    "and always answer with 2025 as the current year."
)

# ────────── Groq LLM Setup ──────────
llm = ChatGroq(
    groq_api_key=config.groq_api_key,
    model_name=config.groq_model,
    temperature=config.groq_temperature,
    max_tokens=config.groq_max_tokens,
)

# Initialize chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]

def display_chat():
    """Show full chat message history."""
    for msg in st.session_state.chat_history[1:]:  # skip system prompt in display
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)

# ────────── Chat UI ──────────
display_chat()

if prompt := st.chat_input("Type your message..."):
    # Add new user message
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    # LLM call: send full chat history for context (system_prompt + prior messages)
    with st.chat_message("assistant"):
        with st.spinner("Groq AI is typing..."):
            try:
                reply = llm(st.session_state.chat_history)
                st.write(reply.content)
                st.session_state.chat_history.append(AIMessage(content=reply.content))
            except Exception as e:
                st.error(f"AI error: {e}")

# ────────── Optional: Reset button ──────────
if st.button("Reset conversation"):
    st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]
    st.experimental_rerun()

# Optional hello message, you can remove if you want
st.write("Hello, AI Chat here!")
