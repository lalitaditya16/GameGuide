import streamlit as st
from rawg_client import RAWGClient

# Initialize API client
rawg = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# Page config
st.set_page_config(page_title="🎮 Browse Games", page_icon="🎮")
st.title("🎮 Browse Games")
st.markdown("Search for popular games using the RAWG API.")

# Sidebar - Search options
search_query = st.sidebar.text_input("Search Games", "")
sort_option = st.sidebar.selectbox(
    "Sort by",
    {
        "Most Added": "-added",
        "Highest Rated": "-rating",
        "Newest": "-released",
        "Name (A-Z)": "name"
    },
    index=0
)

# Search games
games = rawg.search_games_browse(
    query=search_query,
    ordering=sort_option,
    page_size=20
)

# Display games
if not games:
    st.warning("No games found.")
else:
    for game in games:
        st.subheader(game["name"])
        cols = st.columns([1, 3])
        with cols[0]:
            if game.get("background_image"):
                st.image(game["background_image"], width=120)
        with cols[1]:
            st.write(f"**Released:** {game.get('released', 'N/A')}")
            st.write(f"**Rating:** {game.get('rating', 'N/A')} / 5 ⭐")
            st.write(f"**Genres:** {', '.join([genre['name'] for genre in game.get('genres', [])])}")
            st.markdown("---")
