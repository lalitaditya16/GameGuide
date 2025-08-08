import streamlit as st
from rawg_client import RAWGClient
from config import SESSION_KEYS
from helpers import load_custom_css

# Initialize API client
rawg = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# Page config
st.set_page_config(page_title="🎮 Browse Games", page_icon="🎮", layout="wide")
st.title("🎮 Browse Games")
load_custom_css()
st.caption("Find games by search, genre, platform, and sort.")

# Ensure favorites state
if SESSION_KEYS['favorites'] not in st.session_state:
    st.session_state[SESSION_KEYS['favorites']] = []

# Fetch genres and platforms
genres = rawg.get_genres()
platforms = rawg.get_platforms()

# Sidebar - Search options
search_query = st.sidebar.text_input("🔍 Search Games", "")

selected_genre = st.sidebar.selectbox(
    "🎭 Filter by Genre",
    options=["All"] + [genre["name"] for genre in genres]
)

selected_platform = st.sidebar.selectbox(
    "🎮 Filter by Platform",
    options=["All"] + [platform["name"] for platform in platforms]
)

# Define sort mapping
sort_mapping = {
    "Most Added": "-added",
    "Highest Rated": "-rating",
    "Newest": "-released",
    "Name (A-Z)": "name"
}

sort_label = st.sidebar.selectbox("↕️ Sort by", options=list(sort_mapping.keys()))
sort_option = sort_mapping[sort_label]  # Actual value to pass to API

# Prepare filters
genre_slug = next((g["slug"] for g in genres if g["name"] == selected_genre), None) if selected_genre != "All" else None
platform_id = next((p["id"] for p in platforms if p["name"] == selected_platform), None) if selected_platform != "All" else None

# Fetch games
games = rawg.search_games_browse(
    query=search_query,
    ordering=sort_option,
    genre=genre_slug,
    platform=platform_id,
    page_size=24
)

# Display as responsive grid
if not games:
    st.warning("No games found.")
else:
    cards = []
    for game in games:
        name = game.get("name", "Unknown")
        image = game.get("background_image")
        released = game.get("released", "N/A")
        rating = game.get("rating", "N/A")
        genre_names = [g.get('name') for g in game.get('genres', [])][:3]
        card = f"""
        <div class='game-card'>
            <div class='card-image'>
                {'<img src="' + image + '" />' if image else ''}
                <div class='card-overlay'></div>
                <div class='rating-badge'>⭐ {rating}</div>
            </div>
            <div class='card-body'>
                <div class='card-title'>{name}</div>
                <div class='meta'><span class='tag'>{released}</span>{''.join([f"<span class='tag'>{g}</span>" for g in genre_names])}</div>
            </div>
        </div>
        """
        cards.append(card)

    st.markdown("<div class='grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)
