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

    # Create parameters dict
    params = {
        "search": search_query if search_query else None,
        "genres": genres if genres else None,
        "ordering": ordering if ordering else None,
        "page_size": page_size
    }

    # Filter out None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        results = rawg.search_games(**params)
        if not results:
            st.info("No games found.")
            return

        for game in results:
            with st.container():
                st.subheader(game.get("name", "Unknown Title"))
                if game.get("background_image"):
                    st.image(game["background_image"], use_column_width=True)

                released = game.get("released")
                if released:
                    released_date = datetime.strptime(released, "%Y-%m-%d").strftime("%b %d, %Y")
                    st.markdown(f"**Released:** {released_date}")

                rating = game.get("rating")
                if rating:
                    st.markdown(f"**Rating:** {rating} ⭐")

                st.markdown("---")

    except Exception as e:
        st.error(f"Failed to fetch games: {e}")

if __name__ == "__main__":
    main()
