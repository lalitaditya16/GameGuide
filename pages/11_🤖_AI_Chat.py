import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config
from rawg_client import RAWGClient

# Streamlit config
st.set_page_config(page_title="AI Game Chat", page_icon="🎮")
st.title("🤖 AI Game Assistant")
st.caption("Chat with an AI expert about the 2025 gaming landscape.")

today = datetime.now().strftime("%B %d, %Y")
st.write("Today's date is " + today)

# Initialize RAWG client
rawg = RAWGClient(api_key=config.rawg_api_key)

# System prompt
SYSTEM_PROMPT = (
    f"Today's date is {today}. You are a helpful and concise gaming assistant. "
    "The current year is **2025** — always assume that when answering. "
    "Never refer to the year as 2023 or 2024 unless speaking in the past tense. "
    "Always say things like 'As of 2025' or 'Currently in 2025' when answering. "
    "Be confident and factual. Do not hedge or speculate unnecessarily."
)

# Initialize LLM
llm = ChatGroq(
    groq_api_key=config.groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=config.groq_max_tokens,
)

# Session state for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
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
                # Check if it's a game search query
                game = rawg.search_best_match(prompt)

                if game:
                    game_id = game.get("id")
                    game_details = rawg.get_game_details(game_id)

                    if game_details:
                        st.subheader(f"🎮 {game_details.get('name', 'Unknown Game')}")

                        image = game_details.get("background_image", "")
                        if isinstance(image, str) and image.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                            st.image(image, width=700)

                        st.markdown(f"**Released:** {game_details.get('released', 'N/A')}")
                        st.markdown(f"**Rating:** {game_details.get('rating', 'N/A')} / 5")

                        platforms = [p['platform']['name'] for p in game_details.get("platforms", [])]
                        st.markdown(f"**Platforms:** {', '.join(platforms) if platforms else 'N/A'}")

                        genres = [g['name'] for g in game_details.get("genres", [])]
                        st.markdown(f"**Genres:** {', '.join(genres) if genres else 'N/A'}")

                        st.markdown("**Description:**")
                        st.write(game_details.get("description_raw", "No description available."))

                        esrb_data = game_details.get("esrb_rating")
                        esrb = esrb_data.get("name") if esrb_data else "N/A"
                        st.markdown(f"**ESRB Rating:** {esrb}")

                    # Ask LLM to respond
                    messages = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.chat_history
                    response = llm(messages)
                    st.session_state.chat_history.append(AIMessage(content=response.content))
                    st.write(response.content)

                else:
                    st.error("Game not found. Try refining your query.")

            except Exception as e:
                st.error(f"❌ Error: {e}")

# Reset button
if st.button("🔄 Reset Conversation"):
    st.session_state.chat_history = []
    st.experimental_rerun()
