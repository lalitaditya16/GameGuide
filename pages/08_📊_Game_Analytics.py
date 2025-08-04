import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from rawg_client import RAWGClient

# Load RAWG API client
api_key = st.secrets["RAWG_API_KEY"]
rawg_client = RAWGClient(api_key)

# Sidebar filters
st.sidebar.header("🔎 Filters")
selected_year = st.sidebar.selectbox("Select Year", list(range(2025, 2004, -1)), index=0)
genres = rawg_client.get_genres()
platforms = rawg_client.get_platforms()

genre_options = [g["name"] for g in genres]
platform_options = [p["name"] for p in platforms]

genre_mapping = {g["name"]: g["id"] for g in genres}
platform_mapping = {p["name"]: p["id"] for p in platforms}

selected_genre = st.sidebar.selectbox("Select Genre", [None] + genre_options)
selected_platform = st.sidebar.selectbox("Select Platform", [None] + platform_options)

# Fetch data
with st.spinner("Loading analytics data..."):
    raw_data = rawg_client.search_games_analytics(
        ordering="-rating",
        genres=genre_mapping.get(selected_genre),
        platforms=platform_mapping.get(selected_platform),
        year=selected_year,
        page_size=40
    )

# Convert to DataFrame
data = []
for game in raw_data:
    data.append({
        "Name": game.get("name"),
        "Released": game.get("released"),
        "Rating": game.get("rating"),
        "Playtime": game.get("playtime"),
        "Genres": ", ".join([g["name"] for g in game.get("genres", [])]),
        "Platforms": ", ".join([p["platform"]["name"] for p in game.get("platforms", []) if p.get("platform")]),
    })

df = pd.DataFrame(data)

# Page layout
st.markdown("""
    <div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #36D1DC 0%, #5B86E5 100%); color: white; text-align: center; margin-bottom: 2rem;'>
        <h2 style='margin: 0;'>📊 Game Analytics ({})</h2>
        <p style='margin: 0.5rem 0;'>Explore top rated games and trends for {}{}</p>
    </div>
""".format(selected_year, selected_genre + " | " if selected_genre else "", selected_platform if selected_platform else ""), unsafe_allow_html=True)

# Display table
st.dataframe(df, use_container_width=True)

# Visualizations
col1, col2 = st.columns(2)

with col1:
    if not df.empty:
        top_genres = df["Genres"].str.split(", ").explode().value_counts().nlargest(10).reset_index()
        top_genres.columns = ["Genre", "Count"]
        fig = px.bar(top_genres, x="Count", y="Genre", orientation="h",
                     title="🎮 Top Genres", color="Count", color_continuous_scale="Agsunset")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not df.empty:
        top_platforms = df["Platforms"].str.split(", ").explode().value_counts().nlargest(10).reset_index()
        top_platforms.columns = ["Platform", "Count"]
        fig = px.pie(top_platforms, values="Count", names="Platform", title="🕹️ Platform Distribution")
        st.plotly_chart(fig, use_container_width=True)

# Game ratings histogram
if not df.empty:
    fig = px.histogram(df, x="Rating", nbins=20, title="⭐ Rating Distribution of Games")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")
