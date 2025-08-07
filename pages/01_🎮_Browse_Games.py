import streamlit as st
import pandas as pd
from rawg_client import RAWGClient

st.set_page_config(page_title="Browse Games", layout="wide")
st.title("🎮 Browse Games")

api_key = st.secrets["RAWG_API_KEY"]
client = RAWGClient(api_key)

# Fetch genres and platforms only once (cached)
@st.cache_data(show_spinner=False)
def get_genres_and_platforms():
    genres = client.get_genres()
    platforms = client.get_platforms()
    return genres, platforms

genres, platforms = get_genres_and_platforms()

# Sidebar filters
st.sidebar.header("Filter Games")

selected_genres = st.sidebar.multiselect(
    "Select Genre(s)", options=[g["name"] for g in genres]
)

selected_platforms = st.sidebar.multiselect(
    "Select Platform(s)", options=[p["name"] for p in platforms]
)

sort_by = st.sidebar.selectbox(
    "Sort by",
    options=["name", "rating", "released", "added"]
)

sort_order = st.sidebar.radio("Order", ["Descending", "Ascending"], horizontal=True)
ascending = sort_order == "Ascending"

# Fetch games
@st.cache_data(show_spinner=True)
def fetch_filtered_games():
    return client.get_games()

games_data = fetch_filtered_games()

# Convert to DataFrame for easier filtering/sorting
df = pd.DataFrame(games_data)

# Clean platform and genre info for filtering
def extract_names(entry, key):
    return [item[key]["name"] for item in entry if isinstance(item, dict) and key in item and isinstance(item[key], dict)]

df["genres_list"] = df["genres"].apply(lambda x: extract_names(x, "name") if isinstance(x, list) else [])
df["platforms_list"] = df["platforms"].apply(lambda x: extract_names(x, "platform") if isinstance(x, list) else [])

# Filter
if selected_genres:
    df = df[df["genres_list"].apply(lambda g: any(genre in g for genre in selected_genres))]

if selected_platforms:
    df = df[df["platforms_list"].apply(lambda p: any(platform in p for platform in selected_platforms))]

# Sorting
if sort_by in df.columns:
    df = df.sort_values(by=sort_by, ascending=ascending)

# Display
if df.empty:
    st.warning("No games found with the selected filters.")
else:
    for _, game in df.iterrows():
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                if game.get("background_image"):
                    st.image(game["background_image"], width=150)
            with cols[1]:
                st.subheader(game["name"])
                st.markdown(f"**Released:** {game.get('released', 'N/A')}")
                st.markdown(f"**Rating:** {game.get('rating', 'N/A')} / 5")
                st.caption(f"Genres: {', '.join(game['genres_list'])}")
                st.caption(f"Platforms: {', '.join(game['platforms_list'])}")
                st.markdown("---")
