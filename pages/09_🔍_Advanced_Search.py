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

        # Achievements
        achievements = client.get_achievements_by_game_id(game['id'])

        with st.expander("🔧 Raw Achievements Debug"):
            st.write(achievements)

        if achievements and isinstance(achievements, list):
            st.subheader("🏆 All Achievements")

            # Filter and sort by rarity
            filtered_achievements = [
                ach for ach in achievements
                if ach.get("name") and isinstance(ach.get("percent"), (int, float))
            ]
            filtered_achievements.sort(key=lambda x: x["percent"])

            if filtered_achievements:
                has_images = any(
                    isinstance(ach.get("image"), str) and ach["image"].lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                    for ach in filtered_achievements
                )

                if has_images:
                    cols = st.columns(3)
                    for i, ach in enumerate(filtered_achievements):
                        with cols[i % 3]:
                            st.markdown(f"**{ach['name']}**")
                            st.caption(ach.get('description', 'No description'))
                            st.caption(f"Unlocked by {ach['percent']:.2f}% of players")

                            img = ach.get("image")
                            if img and isinstance(img, str) and img.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                                st.image(img, width=80)
                else:
                    st.info("No achievement images found. Showing in table format.")
                    st.dataframe([
                        {
                            "Name": ach.get("name"),
                            "Description": ach.get("description", ""),
                            "Unlocked %": f"{ach.get('percent', 0):.2f}"
                        }
                        for ach in filtered_achievements
                    ])
            else:
                st.warning("✅ No valid achievements found after filtering.")
        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
