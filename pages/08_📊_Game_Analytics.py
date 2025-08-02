import streamlit as st
import pandas as pd
import plotly.express as px
from client.rawg_client import RAWGClient

st.set_page_config(page_title="📊 Game Analytics", page_icon="📊", layout="wide")
st.title("📊 Game Analytics Dashboard")

# ────────── Load RAWG API ──────────
api_key = st.secrets["RAWG_API_KEY"]
rawg = RAWGClient(api_key)

# ────────── Sidebar Filters ──────────
st.sidebar.header("🔍 Filters")
selected_year = st.sidebar.selectbox("Select Release Year", list(range(2025, 2005, -1)))
selected_genre = st.sidebar.text_input("Filter by Genre (optional)")

# ────────── Fetch Game Data ──────────
with st.spinner("Loading game data..."):
    games_data = rawg.search_games(
        query="",
        genres=selected_genre,
        ordering="-rating",
        page_size=40,
        year=selected_year
    )

# Check data
if not games_data:
    st.warning("No games found for this filter.")
    st.stop()

# ────────── Format Data ──────────
games = pd.DataFrame([{
    "Name": g["name"],
    "Rating": g["rating"],
    "Released": g["released"],
    "Genres": ", ".join([genre["name"] for genre in g["genres"]]) if g["genres"] else "Unknown"
} for g in games_data])

# ────────── Top Rated Games ──────────
st.subheader("⭐ Top Rated Games")
top_chart = px.bar(
    games.sort_values("Rating", ascending=False).head(10),
    x="Rating", y="Name", orientation="h", color="Rating",
    title="Top 10 Rated Games", color_continuous_scale="viridis"
)
st.plotly_chart(top_chart, use_container_width=True)

# ────────── Genre Distribution ──────────
st.subheader("🎮 Genre Distribution")
genre_counts = games["Genres"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
genre_df = pd.DataFrame({"Genre": genre_counts.index, "Count": genre_counts.values})

pie_chart = px.pie(genre_df, names="Genre", values="Count", title="Genre Distribution")
st.plotly_chart(pie_chart, use_container_width=True)

# ────────── Data Table ──────────
st.subheader("📋 Game Data Table")
st.dataframe(games, use_container_width=True)
