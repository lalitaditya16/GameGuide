import streamlit as st
from typing import List, Dict, Any
from rawg_client import RAWGClient
from config import config, API_ENDPOINTS
from helpers import get_chat_manager
from datetime import datetime

st.set_page_config(page_title="🎮 Browse Games", page_icon="🎮")

# Title & intro
st.title("🎮 Browse Games")
st.markdown("Explore thousands of games from the RAWG database.")


@st.cache_resource(ttl=config.cache_ttl)
def get_rawg_client() -> RAWGClient:
    return RAWGClient(config.rawg_api_key, base_url=config.base_url)


def load_filters():
    """Load filter options (genres, platforms) for sidebar."""
    rawg = get_rawg_client()

    genres_resp = rawg.get_genres()
    genres = {g['name']: g['id'] for g in genres_resp.get('results', [])}

    platforms_resp = rawg.get_platforms()
    platforms = {p['name']: p['id'] for p in platforms_resp.get('results', [])}

    return genres, platforms


def main():
    rawg = get_rawg_client()

    genres, platforms = load_filters()

    # Sidebar filters
    st.sidebar.header("Filter games")

    search_query = st.sidebar.text_input("Search by name")

    selected_genres = st.sidebar.multiselect("Genres", options=list(genres.keys()))
    selected_platforms = st.sidebar.multiselect("Platforms", options=list(platforms.keys()))

    ordering = st.sidebar.selectbox(
        "Order by",
        options=[
            "Relevance", 
            "Name (A-Z)",
            "Name (Z-A)", 
            "Release date (newest)", 
            "Release date (oldest)",
            "Rating (highest)", 
            "Rating (lowest)"
        ],
        index=0
    )

    # Map ordering to API values
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

    # Pagination state: page number
    if 'page' not in st.session_state:
        st.session_state.page = 1

    # Button to reset page when filters/search changes
    def reset_page():
        st.session_state.page = 1

    if st.sidebar.button("Reset Filters / Search"):
        st.session_state.page = 1
        st.experimental_rerun()

    # Compose API parameters
    params = {
        "page": st.session_state.page,
        "page_size": config.default_page_size,
    }
    if search_query:
        params["search"] = search_query

    if selected_genres:
        # Convert genre names to IDs
        genre_ids = ",".join(str(genres[g]) for g in selected_genres)
        params["genres"] = genre_ids

    if selected_platforms:
        platform_ids = ",".join(str(platforms[p]) for p in selected_platforms)
        params["platforms"] = platform_ids

    if ordering_param:
        params["ordering"] = ordering_param

    # Fetch games data
    with st.spinner("Loading games..."):
        games_data = rawg.get_games(**params)

    games = games_data.get("results", [])

    # Display results count and page
    total_results = games_data.get("count", 0)
    st.write(f"Total games found: {total_results}")
    st.write(f"Page: {st.session_state.page}")

    # Show game cards in columns
    cols_per_row = config.items_per_row
    cols = st.columns(cols_per_row)

    for idx, game in enumerate(games):
        col = cols[idx % cols_per_row]
        with col:
            name = game.get("name", "Unknown")
            released = game.get("released", "TBA")
            rating = game.get("rating", "N/A")
            genres_list = ", ".join([g["name"] for g in game.get("genres", [])][:2])
            background_img = game.get("background_image") or ""

            # Display image if available
            if background_img:
                st.image(background_img, use_column_width=True, width=config.image_width, clamp=True)

            st.markdown(f"### {name}")
            st.markdown(f"**Released:** {released}")
            st.markdown(f"**Rating:** {rating}/5")
            st.markdown(f"**Genres:** {genres_list}")

    # Pagination buttons
    col1, col2, col3 = st.columns([1,6,1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.experimental_rerun()
    with col3:
        # Enable next only if more results exist
        if total_results > st.session_state.page * config.default_page_size:
            if st.button("Next ➡️"):
                st.session_state.page += 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()

