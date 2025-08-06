import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from config import config
from rawg_client import RAWGClient  # Ensure this path is correct

# Streamlit config
st.set_page_config(page_title="AI Game Chat", page_icon="🎮")
st.title("🤖 AI Game Assistant")
st.caption("Chat with an AI expert about the 2025 gaming landscape.")

today = datetime.now().strftime("%B %d, %Y")
today_iso = datetime.now().strftime("%Y-%m-%d")  # For release date comparison
st.write("Today's date is " + today)

# Rawg Client init
rawg = RAWGClient(api_key=config.rawg_api_key)

# LLM setup
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

# Input field
if prompt := st.chat_input("Ask about 2025 games..."):
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        with st.spinner("Thinking like it’s 2025..."):
            try:
                # Check if it's a game query
                game = rawg.search_best_match(prompt)
                if game:
                    game_id = game.get("id")
                    game_details = rawg.get_game_details(game_id)
                    game_name = game_details.get("name", "Unknown Game")
                    release_date = game_details.get("released", "")
                    background_image = game_details.get("background_image", "")

                    st.subheader(f"🎮 {game_name}")
                    if background_image:
                        st.image(background_image, width=700)
                    st.markdown(f"**Released:** {release_date or 'N/A'}")
                    st.markdown(f"**Rating:** {game_details.get('rating', 'N/A')}")

                    platforms = ", ".join([p['platform']['name'] for p in game_details.get("platforms", [])])
                    genres = ", ".join([g['name'] for g in game_details.get("genres", [])])
                    st.markdown(f"**Platforms:** {platforms or 'N/A'}")
                    st.markdown(f"**Genres:** {genres or 'N/A'}")

                    st.markdown("**Description:**")
                    st.write(game_details.get("description_raw", "No description available."))

                    esrb_data = game_details.get("esrb_rating")
                    esrb_name = esrb_data.get("name") if esrb_data else "N/A"
                    st.markdown(f"**ESRB Rating:** {esrb_name}")

                    # Build system prompt dynamically
                    SYSTEM_PROMPT = (
                        f"Today's date is {today}. You are a helpful and concise gaming assistant. "
                        "Try to explain the game mechanics,a basic synopsis of the plot without spoiling any key elements "
                        "Be confident and factual. Do not hedge or speculate unnecessarily."
                    )

                    # Inject game release logic
                    if release_date and release_date <= today_iso:
                        SYSTEM_PROMPT += f"\n\nNote: '{game_name}' has already been released on {release_date}."
                    else:
                        SYSTEM_PROMPT += f"\n\nNote: '{game_name}' is an upcoming game expected to release on {release_date or 'an unknown future date'}."

                    # Generate response
                    messages = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.chat_history
                    response = llm(messages)
                    st.session_state.chat_history.append(AIMessage(content=response.content))
                    st.write(response.content)

                else:
                    st.error("Game not found. Try refining your query.")
            except Exception as e:
                st.error(f"Error: {e}")

# Reset button
if st.button("🔄 Reset Conversation"):
    st.session_state.chat_history = []
    st.experimental_rerun()
