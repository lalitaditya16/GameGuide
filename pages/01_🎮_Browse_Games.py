import streamlit as st
from client.rawg_client import rawg_client
from config import config

st.set_page_config(page_title="Browse Games", layout="wide")

st.title("🎮 Browse Games")
st.write("Explore thousands of games from the RAWG database.")

client = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# --- Sidebar ---
st.sidebar.header("🔍 Filter games")

search_query = st.sidebar.text_input("Search by name", value="")

# --- API Query Params ---
query_params = {"search": search_query, "page_size": 20}

# --- API Call ---
with st.spinner("Loading games..."):
    response = client.get_games(**query_params)
    games = response.get("results", [])
    total = response.get("count", 0)

# --- Display ---
st.subheader(f"Total games found: {total}")
if games:
    for game in games:
        st.markdown(f"### {game['name']}")
        if game.get("background_image"):
            st.image(game["background_image"], width=400)
        st.write(f"Released: {game.get('released', 'N/A')}")
        st.write("---")
else:
    st.warning("No games found. Try a different search term.")
