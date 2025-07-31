import streamlit as st
from typing import Dict, Any
from rawg_client import RAWGClient
from datetime import datetime

st.set_page_config(page_title="Browse Games", page_icon="🎮")

st.title("🎮 Browse Games")
st.markdown("Explore thousands of games from the RAWG database.")

def get_rawg_api_key() -> str:
    """Safely fetch RAWG API key from Streamlit secrets, warn if missing."""
    key = st.secrets.get("RAWG_API_KEY", "")
    if not key:
        st.error("RAWG API key not found. Please set it up in Streamlit Cloud (Manage App ▶️ Secrets) or locally in `.streamlit/secrets.toml`.")
        st.stop()
    return key


@st.cache_resource(ttl=3600)
def get_rawg_client() -> RAWGClient:
    api_key = get_rawg_api_key()
    # Use default base URL; override if needed
    return RAWGClient(api_key)

def load_filters():
    """Load genres/platforms, warning if missing or failing."""
    rawg = get_rawg_client()
    genres, platforms = {}, {}
    try:
        genres_resp = rawg.get_genres()
        if genres_resp and genres_resp.get('results'):
            genres = {g['name']: g['id'] for g in genres_resp['results']}
        else:
            st.sidebar.warning("No genres available (API may be rate-limited or key is invalid).")
    except Exception as e:
        st.sidebar.error(f"Error loading genres: {e}")

    try:
        platforms_resp = rawg.get_platforms()
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
    selected_genres = st.sidebar.multiselect("Genres", list(genres.keys())) if genres else []
    selected_platforms = st.sidebar.multiselect("Platforms", list(platforms.keys())) if platforms else []

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

    params = {
        "page": st.session_state.page,
        "page_size": 20,  # Or use a value from config if defined
    }
    if search_query:
        params["search"] = search_query
    if selected_genres:
        params["genres"] = ",".join(str(genres[g]) for g in selected_genres)
    if selected_platforms:
        params["platforms"] = ",".join(str(platforms[p]) for p in selected_platforms)
    if ordering_param:
        params["ordering"] = ordering_param

    # Fetch and show games
    with st.spinner("Loading games..."):
        try:
            games_data = rawg.get_games(**params)
        except Exception as e:
            st.error(f"Error loading games: {e}")
            return

    games = games_data.get("results", [])
    total_results = games_data.get("count", 0)
    st.write(f"Total games found: {total_results}")
    st.write(f"Page: {st.session_state.page}")

    # Display game cards (simple grid)
    cols = st.columns(3)
    for idx, game in enumerate(games):
        col = cols[idx % 3]
        with col:
            if game.get("background_image"):
                st.image(game["background_image"], use_column_width=True)
            st.markdown(f"**{game.get('name', 'Unknown')}**")
            st.markdown(f"Released: {game.get('released', 'TBA')}")
            st.markdown(f"Rating: {game.get('rating', 'N/A')}/5")

    col1, _, col3 = st.columns([1,6,1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.experimental_rerun()
    with col3:
        if total_results > st.session_state.page * 20:
            if st.button("Next ➡️"):
                st.session_state.page += 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()
