import streamlit as st
from datetime import datetime
from rawg_client import RAWGClient

# Load RAWG API client
api_key = st.secrets["RAWG_API_KEY"]
rawg_client = RAWGClient(api_key)

st.title("📊 Game Analytics Dashboard")

# Current year
current_year = datetime.now().year

# Sidebar filters
st.sidebar.header("Filter Options")
selected_genre = st.sidebar.text_input("Genre (optional)")
selected_platform = st.sidebar.text_input("Platform (optional)")

# Load top-rated games using analytics method
st.subheader(f"Top Rated Games of {current_year}")
try:
    raw_data = rawg_client.search_games_analytics(
        ordering="-rating",
        genres=selected_genre if selected_genre else None,
        platforms=selected_platform if selected_platform else None,
        year=current_year,
        page_size=40
    )

    for game in raw_data:
        st.markdown(f"### {game.get('name', 'Unknown')}")
        st.write(f"⭐ Rating: {game.get('rating', 'N/A')}")
        st.write(f"📅 Released: {game.get('released', 'N/A')}")
        genres = ", ".join([g['name'] for g in game.get("genres", [])])
        platforms = ", ".join([p['platform']['name'] for p in game.get("platforms", []) if p.get("platform")])
        st.write(f"🎮 Platforms: {platforms}")
        st.write(f"🏷 Genres: {genres}")
        if game.get("background_image"):
            st.image(game["background_image"], width=600)
        st.markdown("---")

except Exception as e:
    st.error("Failed to load game analytics.")
    st.exception(e)
