import streamlit as st
from client.rawg_client import RAWGClient
from datetime import datetime

def main():
    st.title("🎮 Browse Games")

    # Load API key from environment or Streamlit secrets
    api_key = st.secrets["RAWG_API_KEY"]
    rawg = RAWGClient(api_key)

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Search Filters")
        search_query = st.text_input("Search for games", "")
        genres = st.text_input("Genres (comma separated)", "")
        ordering = st.selectbox("Order by", ["", "name", "-released", "-rating", "-added"])
        page_size = st.slider("Number of results", 5, 40, 10)

    # Prepare parameters
    params = {
        "search": search_query,
        "page_size": page_size
    }
    if genres:
        params["genres"] = genres
    if ordering:
        params["ordering"] = ordering

    # Search games
    results = rawg.search_games(**params)

    if results:
        for game in results:
            st.subheader(game.get("name"))
            st.write(f"Released: {game.get('released', 'N/A')}")
            st.write(f"Rating: {game.get('rating', 'N/A')}")
            st.write(f"Platforms: {', '.join([p['platform']['name'] for p in game.get('platforms', [])])}")
            st.write(f"Publisher: {', '.join([pub.get('name') for pub in game.get('publishers', [])])}")
            st.image(game.get("background_image", ""), width=600)
            st.markdown("---")
    else:
        st.warning("No games found.")

if __name__ == "__main__":
    main()

