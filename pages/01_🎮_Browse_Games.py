import streamlit as st
from rawg_client import RAWGClient
import config

def main():
    st.title("🎮 Browse Games")
    rawg = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

    # Sidebar Search Filters
    with st.sidebar:
        st.header("🔎 Search Filters")

        search_query = st.text_input("Search for a game")

        genres_data = rawg.get_genres()
        genre_options = [genre["name"] for genre in genres_data.get("results", [])]
        selected_genre = st.selectbox("Genre", ["Any"] + genre_options)

        platforms_data = rawg.get_platforms()
        platform_options = [platform["name"] for platform in platforms_data.get("results", [])]
        selected_platform = st.selectbox("Platform", ["Any"] + platform_options)

        page_size = st.slider("Results per page", 5, 20, 10)

    # Convert genre/platform names to IDs for API
    genre_id = next((g["id"] for g in genres_data.get("results", []) if g["name"] == selected_genre), "") if selected_genre != "Any" else ""
    platform_id = next((p["id"] for p in platforms_data.get("results", []) if p["name"] == selected_platform), "") if selected_platform != "Any" else ""

    if search_query:
        results = rawg.search_games(
            search=search_query,
            genres=genre_id,
            platforms=platform_id,
            page_size=page_size
        )

        games = results.get("results", [])
        if not games:
            st.warning("No games found. Try adjusting your filters.")
        else:
            for game in games:
                with st.container():
                    st.subheader(game["name"])
                    if game.get("background_image"):
                        st.image(game["background_image"], use_column_width=True)
                    st.markdown(f"**Released:** {game.get('released', 'N/A')}")
                    st.markdown(f"**Rating:** {game.get('rating', 'N/A')} ⭐")
                    st.markdown("**Platforms:** " + ", ".join([p["platform"]["name"] for p in game.get("platforms", [])]))
                    if game.get("publishers"):
                        st.markdown("**Publisher:** " + ", ".join([pub["name"] for pub in game["publishers"]]))
                    st.markdown("---")
    else:
        st.info("Enter a search query to find games.")

if __name__ == "__main__":
    main()
