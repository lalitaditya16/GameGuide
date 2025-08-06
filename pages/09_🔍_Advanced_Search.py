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
            for shot in screenshots:
                url = shot.get("image")
                if isinstance(url, str) and url.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    st.image(url, use_column_width=True)
                else:
                    st.warning(f"Skipped invalid image URL: {url}")

        # Achievements in columns
        achievements = client.get_achievements_by_game_id(game['id'])
        if achievements:
            st.subheader("🏆 Achievements")
            cols = st.columns(3)
            for i, ach in enumerate(achievements):
                with cols[i % 3]:
                    st.markdown(f"**{ach['name']}**")
                    st.caption(ach.get('description', 'No description'))

                    percent = ach.get('percent')
                    try:
                        percent_val = float(percent)
                        st.caption(f"Unlocked by {percent_val:.2f}% of players")
                    except (TypeError, ValueError):
                        st.caption("Unlock percentage not available")

                    img = ach.get("image")
                    if isinstance(img, str) and img.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        st.image(img, width=80)

        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
