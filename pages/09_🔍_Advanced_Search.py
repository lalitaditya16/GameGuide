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

        # Get full game details
        game_details = client.get_game_details(game['id'])

        if game_details:
            st.subheader("📖 Game Details")

            raw_description = game_details.get("description_raw", "No description available.")
            description = clean_description(raw_description)
            developers = ', '.join([dev['name'] for dev in game_details.get('developers', [])])
            publishers = ', '.join([pub['name'] for pub in game_details.get('publishers', [])])
            website = game_details.get('website', '')
            esrb = game_details.get('esrb_rating', {}).get('name', 'N/A')

            st.markdown(f"**Description:** {description}")
            if developers:
                st.markdown(f"**Developer(s):** {developers}")
            if publishers:
                st.markdown(f"**Publisher(s):** {publishers}")
            st.markdown(f"**ESRB Rating:** {esrb}")
            if website:
                st.markdown(f"**Website:** [Visit Official Site]({website})")

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

            for ach in achievements:
                cols = st.columns([1, 6])  # [image column, info column]
                image = ach.get("image")
                name = ach.get("name")
                description = ach.get("description", "No description")
                percent = ach.get("percent")

                with cols[0]:
                    if image and isinstance(image, str) and image.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        st.image(image, width=64)
                    else:
                        st.empty()

                with cols[1]:
                    st.markdown(f"**{name}**")
                    st.caption(description)
                    if percent is not None:
                        st.caption(f"Unlocked by {percent:.2f}% of players")

                st.markdown("---")
        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
