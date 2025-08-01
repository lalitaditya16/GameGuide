import streamlit as st
from rawg_client import RAWGClient
import config


def main():
    st.title("🎮 Browse Games")
    rawg = RAWGClient(config.api_key)

    # Sidebar Filters
    with st.sidebar:
        st.header("🔎 Filters")
        genres_data = rawg.get_genres()
        platforms_data = rawg.get_platforms()

        genre_options = [g["name"] for g in genres_data["results"]] if genres_data else []
        platform_options = [p["name"] for p in platforms_data["results"]] if platforms_data else []

        selected_genre = st.selectbox("Genre", ["Any"] + genre_options)
        selected_platform = st.selectbox("Platform", ["Any"] + platform_options)
        search_query = st.text_input("Search Games")

    if search_query:
        st.write(f"### Results for: {search_query}")
        params = {"search": search_query, "page_size": 12}

        if selected_genre != "Any":
            genre_id = next((g["id"] for g in genres_data["results"] if g["name"] == selected_genre), None)
            if genre_id:
                params["genres"] = genre_id

        if selected_platform != "Any":
            platform_id = next((p["id"] for p in platforms_data["results"] if p["name"] == selected_platform), None)
            if platform_id:
                params["platforms"] = platform_id

        results = rawg.search_games(**params)

        if results and results.get("results"):
            for game in results["results"]:
                with st.container():
                    st.subheader(game.get("name", "Unknown Game"))
                    cols = st.columns([1, 3])

                    with cols[0]:
                        if game.get("background_image"):
                            st.image(game["background_image"], width=150)

                    with cols[1]:
                        st.markdown(f"**Released:** {game.get('released', 'N/A')}")
                        st.markdown(f"**Rating:** {game.get('rating', 'N/A')}")

                        if game.get("platforms"):
                            platforms = [p["platform"]["name"] for p in game["platforms"]]
                            st.markdown(f"**Platforms:** {', '.join(platforms)}")

                        if game.get("genres"):
                            genres = [g["name"] for g in game["genres"]]
                            st.markdown(f"**Genres:** {', '.join(genres)}")

                        if game.get("publishers"):
                            publishers = [p["name"] for p in game["publishers"]]
                            st.markdown(f"**Publishers:** {', '.join(publishers)}")

        else:
            st.warning("No results found. Try refining your search or filters.")


if __name__ == "__main__":
    main()
