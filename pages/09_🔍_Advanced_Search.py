import streamlit as st
from rawg_client import RAWGClient

st.set_page_config(page_title="Advanced Game Search", layout="wide")
st.title("🔍 Advanced Game Search")

api_key = st.secrets["RAWG_API_KEY"]
client = RAWGClient(api_key)

game_name = st.text_input("Enter a game name")

if game_name:
    with st.spinner("Searching for game..."):
        game = client.search_best_match(game_name)

    if game:
        st.subheader(game['name'])

        if game.get("background_image"):
            st.image(game["background_image"], use_column_width=True)

        st.markdown(f"**Released:** {game.get('released', 'N/A')}")
        st.markdown(f"**Rating:** {game.get('rating', 'N/A')} / 5 ({game.get('ratings_count', 0)} ratings)")
        st.markdown(f"**Genres:** {', '.join([genre['name'] for genre in game.get('genres', [])])}")
        st.markdown(f"**Platforms:** {', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])}")

        # Screenshots
        screenshots = client.get_game_screenshots(game['id'])
        if screenshots:
            st.subheader("🖼️ Screenshots")
            for url in screenshots:
                if url and url.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    st.image(url, use_column_width=True)
                else:
                    st.warning(f"Skipped invalid image URL: {url}")

        # Achievements
        achievements = client.get_achievements(game['id'])
        if achievements:
            st.subheader("🏆 Achievements")
            for ach in achievements:
                st.markdown(f"**{ach['name']}** — {ach.get('description', 'No description')}")

                percent = ach.get('percent')
                if percent is not None:
                    st.caption(f"Unlocked by {percent:.2f}% of players")
                else:
                    st.caption("Unlock percentage not available")

                if ach.get("image") and ach["image"].lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    st.image(ach["image"], width=80)

                st.markdown("---")
        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
