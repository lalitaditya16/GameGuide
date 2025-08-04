import streamlit as st
import pandas as pd
from datetime import datetime
from collections import Counter
import plotly.express as px
from rawg_client import RAWGClient  # ✅ Replaced import

# Load RAWG API client
api_key = st.secrets["RAWG_API_KEY"]
rawg_client = RAWGClient(api_key)

# Set page config
st.set_page_config(page_title="Game Analytics", page_icon="📊", layout="wide")
st.title("📊 Game Analytics Dashboard")

# Get current month range
today = datetime.today()
current_month_start = today.replace(day=1).strftime("%Y-%m-%d")
current_month_end = today.strftime("%Y-%m-%d")

# Fetch game data from RAWG API
with st.spinner("Fetching latest game analytics..."):
    raw_data = rawg_client.search_games_analytics(
        ordering="-rating",
        dates=f"{current_month_start},{current_month_end}",
        page_size=40
    )

# Initialize lists to store genres, platforms, ratings
genres_flat = []
platforms_flat = []
ratings = []

for game in raw_data:
    # Genres
    if "genres" in game and game["genres"]:
        genres_flat.extend([g["name"] for g in game["genres"] if "name" in g])
    
    # Platforms
    if "platforms" in game and game["platforms"]:
        platforms_flat.extend([
            p["platform"]["name"]
            for p in game["platforms"]
            if p.get("platform") and p["platform"].get("name")
        ])
    
    # Ratings
    if "rating" in game and isinstance(game["rating"], (int, float)):
        ratings.append(game["rating"])

# Count occurrences
genre_counts = Counter(genres_flat)
platform_counts = Counter(platforms_flat)
rating_counts = Counter(ratings)

# Convert to DataFrames
genre_df = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"]).sort_values(by="Count", ascending=False)
platform_df = pd.DataFrame(platform_counts.items(), columns=["Platform", "Count"]).sort_values(by="Count", ascending=False)
rating_df = pd.DataFrame(rating_counts.items(), columns=["Rating", "Count"]).sort_values(by="Rating")

# Layout with columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎮 Top Genres")
    fig_genres = px.bar(genre_df.head(10), x="Count", y="Genre", orientation="h", color="Genre", height=400)
    st.plotly_chart(fig_genres, use_container_width=True)

with col2:
    st.subheader("🕹️ Platform Distribution")
    fig_platforms = px.pie(platform_df, values="Count", names="Platform", hole=0.3, height=400)
    st.plotly_chart(fig_platforms, use_container_width=True)

# Ratings distribution
st.subheader("⭐ Rating Distribution of Games")
fig_ratings = px.bar(rating_df, x="Rating", y="Count", color="Rating", height=400)
st.plotly_chart(fig_ratings, use_container_width=True)
