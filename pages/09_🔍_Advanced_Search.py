import streamlit as st
from rawg_client import RAWGClient
import os
from dotenv import load_dotenv

load_dotenv()
RAWG_API_KEY = st.secrets["RAWG_API_KEY"]

rawg_client = RAWGClient(RAWG_API_KEY)

st.set_page_config(page_title="Game Achievements & Screenshots", layout="wide")

st.title("🎮 Game Explorer")

game_name = st.text_input("Enter game name")

if game_name:
    with st.spinner("Searching for game..."):
        game_id = rawg_client.get_game_id_by_name(game_name)

    if game_id:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🏆 Achievements")
            achievements = rawg_client.get_achievements_by_game_id(game_id)
            if achievements:
                for ach in achievements:
                    st.markdown(f"**{ach['name']}** — {ach.get('description', 'No description')}")
                    st.caption(f"Unlocked by {ach.get('percent', 0):.2f}% of players")
                    if ach.get("image"):
                        st.image(ach["image"], width=80)
                    st.markdown("---")
            else:
                st.info("No achievements found for this game.")

        with col2:
            st.subheader("🖼️ Screenshots")
            screenshots = rawg_client.get_game_screenshots(game_id)
            if screenshots:
                for s in screenshots:
                    st.image(s["image"])
            else:
                st.info("No screenshots available.")
    else:
        st.error("Game not found. Please try another name.")
