import streamlit as st
from typing import Dict, Any
from rawg_client import RAWGClient
from config import config
from helpers import get_chat_manager
from datetime import datetime

st.set_page_config(page_title="Browse Games", page_icon="🎮")

st.title("🎮 Browse Games")
st.markdown("Explore thousands of games from the RAWG database.")
st.sidebar.write("RAWG API KEY DETECTED:", st.secrets.get("RAWG_API_KEY", None))

def get_rawg_client() -> RAWGClient:
    api_key = st.secrets.get("RAWG_API_KEY", "")
    if not api_key:
        st.error("RAWG API key missing!")
        st.stop()
    return RAWGClient(api_key)

def load_filters():
    rawg = get_rawg_client()
    genres, platforms = {}, {}
    try:
        genres_resp = rawg.get_genres()
        st.sidebar.write("Genres API Response:", genres_resp)
        if genres_resp and genres_resp.get('results'):
            genres = {g['name']: g['id'] for g in genres_resp['results']}
        else:
            st.sidebar.warning("No genres available (API may be rate-limited or key is invalid).")
    except Exception as e:
        st.sidebar.error(f"Error loading genres: {e}")

    try:
        platforms_resp = rawg.get_platforms()
        st.sidebar.write("Platforms API Response:", platforms_resp)
        if platforms_resp and platforms_resp.get('results'):
            platforms = {p['name']: p['id'] for p in platforms_resp['results']}
        else:
            st.sidebar.warning("No platforms available (API may be rate-limited or key is invalid).")
    except Exception as e:
        st.sidebar.error(f"Error loading platforms: {e}")

    return genres, platforms

def main():
    rawg = get_rawg_client()
    genres, platforms = load_filters()

    st.sidebar.header("Filter games")

    search_query = st.sidebar.text_input("Search by name")

    if genres:
        selected_genres = st.sidebar.multiselect("Genres", options=list(genres.keys()))
    else:
        selected_genres = []

    if platforms:
        selected_platforms = st.sidebar.multiselect("Platforms", options=list(platforms.keys()))
    else:
        selected_platforms = []

    ordering = st.sidebar.selectbox(
        "Order by",
        options=[
            "Relevance", 
            "Name (A-Z)", "Name (Z-A)", 
            "Release date (newest)", "Release date (oldest)",
            "Rating (highest)", "Rating (lowest)"
        ],
        index=0
    )

    ordering_map = {
        "Relevance": "",
        "Name (A-Z)": "name",
        "Name (Z-A)": "-name",
        "Release date (newest)": "-released",
        "Release date (oldest)": "released",
        "Rating (highest)": "-rating",
        "Rating (lowest)": "rating"
    }
    ordering_param = ordering_map.get(ordering, "")

    if 'page' not in st.session_state:
        st.session_state.page = 1

    if st.sidebar.button("Reset Filters / Search"):
        st.session_state.page = 1
        st.experimental_rerun()

    # --- Debugging: Build and show parameters ---
    params = {
        "page": st.session_state.page,
        "page_size": config.default_page_size,
    }

    if search_query:
        params["search"] = search_query
    if selected_genres:
        genre_ids = ",".join(str(genres[g]) for g in selected_genres)
        params["genres"] = genre_ids
    if selected_platforms:
        platform_ids = ",".join(str(platforms[p]) for p in selected_platforms)
        params["platforms"] = platform_ids
    if ordering_param:
        params["ordering"] = ordering_param

    st.sidebar.subheader("Query Parameters")
    st.sidebar.code(params, language="json")

    with st.spinner("Loading games..."):
        try:
            games_data = rawg.get_games(**params)
            st.sidebar.subheader("RAWG Response")
            st.sidebar.code(games_data, language="json")
        except Exception as e:
            st.error(f"Error loading games: {e}")
            return

    games = games_data.get("results", [])
    total_results = games_data.get("count", 0)
    st.write(f"Total games found: {total_results}")
    st.write(f"Page: {st.session_state.page}")

    if not games:
        st.warning("No games found. Try a different search term or adjust filters.")
        return

    # Display Game Cards
    cols_per_row = config.items_per_row if hasattr(config, "items_per_row") else 3
    cols = st.columns(cols_per_row)

    for idx, game in enumerate(games):
        col = cols[idx % cols_per_row]
        with col:
            name = game.get("name", "Unknown")
            released = game.get("released", "TBA")
            rating = game.get("rating", "N/A")
            genres_list = ", ".join([g["name"] for g in game.get("genres", [])][:2])
            background_img = game.get("background_image") or ""
            if background_img:
                st.image(background_img, use_column_width=True, clamp=True)
            st.markdown(f"### {name}")
            st.markdown(f"**Released:** {released}")
            st.markdown(f"**Rating:** {rating}/5")
            st.markdown(f"**Genres:** {genres_list}")

    # Pagination
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.experimental_rerun()
    with col3:
        if total_results > st.session_state.page * config.default_page_size:
            if st.button("Next ➡️"):
                st.session_state.page += 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()
