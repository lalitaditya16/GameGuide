# pages/02_🎮_Browse_Games.py

import streamlit as st
from dotenv import load_dotenv
from rawg_client import RAWGClient
from datetime import datetime


load_dotenv()
st.set_page_config(page_title="🎮 Browse Games", layout="wide")

st.title("🎮 Browse Games")

# Initialize API client
rawg = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# Sidebar Filters
st.sidebar.header("Filters")

search_query = st.sidebar.text_input("Search by game title")

# You can hardcode or fetch genres from RAWG API
genre_options = ["action", "adventure", "indie", "rpg", "strategy", "shooter"]
selected_genre = st.sidebar.selectbox("Genre", [""] + genre_options)

year = st.sidebar.slider("Release Year", 2000, datetime.now().year, datetime.now().year)

ordering_options = {
    "Name": "name",
    "Release Date": "-released",
    "Rating": "-rating",
    "Metacritic": "-metacritic"
}
ordering = st.sidebar.selectbox("Sort by", list(ordering_options.keys()))

# Fetch games
with st.spinner("Fetching games..."):
    games = rawg.search_games(
        query=search_query,
        genres=selected_genre if selected_genre else None,
        ordering=ordering_options[ordering],
        year=year
    )

if not games:
    st.warning("No games found for the selected filters.")
else:
    for game in games:
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(game["background_image"], width=150)
            with cols[1]:
                st.subheader(game["name"])
                st.markdown(f"**Released:** {game['released'] or 'N/A'}")
                st.markdown(f"**Rating:** {game['rating']}/5 from {game['ratings_count']} ratings")
                st.markdown(f"**Genres:** {', '.join([g['name'] for g in game.get('genres', [])])}")
                st.markdown(f"[More Info](https://rawg.io/games/{game['slug']})")

