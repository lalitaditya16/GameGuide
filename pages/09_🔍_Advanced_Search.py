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

        # Game Description
        game_details = client.get_game_by_id(game['id'])
        description = game_details.get("description_raw", "No description available.")
        st.markdown(f"**Description:**\n\n{description}")

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

        # Achievements
        achievements = client.get_achievements_by_game_id(game['id'])

        if achievements and isinstance(achievements, list):
            st.subheader("🏆 All Achievements")

            # Fix percent if it's a string
            for ach in achievements:
                percent = ach.get("percent")
                try:
                    ach["percent"] = float(percent)
                except (ValueError, TypeError):
                    ach["percent"] = None

            # Show all achievements in a bulleted list
            for ach in achievements:
                name = ach.get("name")
                description = ach.get("description", "No description")
                percent = ach.get("percent")
                image = ach.get("image")

                with st.container():
                    cols = st.columns([1, 9])
                    if image and isinstance(image, str) and image.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        cols[0].image(image, width=60)
                    cols[1].markdown(f"**{name}**")
                    cols[1].caption(description)
                    if percent is not None:
                        cols[1].caption(f"Unlocked by {percent:.2f}% of players")
                st.markdown("---")
        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
