import streamlit as st
from rawg_client import RAWGClient  # Ensure RAWGClient.py is in the same folder or adjust import
import os
from dotenv import load_dotenv

load_dotenv()

# Load your RAWG API key from .env
API_KEY = st.secrets("RAWG_API_KEY")

# Initialize client
rawg_client = RAWGClient(API_KEY)

st.set_page_config(page_title="Advanced Game Search", layout="wide")

st.title("🔍 Advanced Game Search")
st.markdown("Search for a game and explore its **achievements** and **screenshots**!")

# --- Search Bar ---
game_name = st.text_input("Enter a game name")

if game_name:
    # --- Game Search ---
    search_results = rawg_client.search_games_browse(query=game_name, page_size=1)

    if not search_results:
        st.warning("No game found with that name.")
    else:
        game = search_results[0]
        game_id = game.get("id")

        st.subheader(f"🎮 {game['name']}")
        st.image(game.get("background_image"), use_column_width=True)
        st.markdown(f"**Released:** {game.get('released', 'Unknown')}")
        st.markdown(f"**Rating:** {game.get('rating', 'N/A')} ⭐")
        st.markdown("**Genres:** " + ", ".join(g['name'] for g in game.get("genres", [])))
        st.markdown("**Platforms:** " + ", ".join(p['platform']['name'] for p in game.get("platforms", []) if p.get("platform")))

        st.divider()

        # --- Achievements ---
        st.subheader("🏆 Achievements")
        achievements = rawg_client.get_achievements_by_game_name(game_name)

        if achievements:
            for ach in achievements:
                cols = st.columns([1, 4])
                with cols[0]:
                    if ach.get("image"):
                        st.image(ach["image"], width=64)
                with cols[1]:
                    st.markdown(f"**{ach['name']}** — {ach['description'] or 'No description'}")
                    st.caption(f"Unlocked by {ach['percent']}% of players")
        else:
            st.info("No achievements found.")

        st.divider()

        # --- Screenshots ---
        st.subheader("🖼️ Screenshots")
        screenshots = rawg_client.get_game_screenshots(game_id)

        if screenshots:
            for shot in screenshots[:5]:
                st.image(shot["image"], use_column_width=True)
        else:
            st.info("No screenshots found.")
