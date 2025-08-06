import streamlit as st
import matplotlib.pyplot as plt
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
        st.markdown(f"**Metacritic:** {game.get('metacritic', 'N/A')}")
        st.markdown(f"**Tags:** {', '.join([tag['name'] for tag in game.get('tags', [])[:5]])}")

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

            for ach in achievements:
                percent = ach.get("percent")
                try:
                    ach["percent"] = float(percent)
                except (ValueError, TypeError):
                    ach["percent"] = None

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
                            st.image(ach.get("image"), width=80)
                            st.markdown(f"**{ach['name']}**")
                            st.caption(ach.get('description', 'No description'))
                            st.caption(f"Unlocked by {ach['percent']:.2f}% of players")
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

                # Pie Chart Visualization
                st.subheader("📊 Unlock Rate Distribution")
                buckets = {"<5%": 0, "5-25%": 0, "25-75%": 0, ">75%": 0}
                for ach in filtered_achievements:
                    p = ach["percent"]
                    if p < 5:
                        buckets["<5%"] += 1
                    elif p < 25:
                        buckets["5-25%"] += 1
                    elif p < 75:
                        buckets["25-75%"] += 1
                    else:
                        buckets[">75%"] += 1

                labels = list(buckets.keys())
                sizes = list(buckets.values())
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig)

            else:
                st.warning("✅ No valid achievements found after filtering.")
        else:
            st.info("No achievements available for this game.")
    else:
        st.error("Game not found. Please check the name and try again.")
