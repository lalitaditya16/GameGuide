import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from rawg_client import RAWGClient

# Set up the page
st.set_page_config(page_title="Game Analytics", layout="wide")
st.title("📊 Game Analytics")

# Initialize RAWG API client
rawg_client = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# Fetch current month's top-rated games
with st.spinner("Fetching top-rated games for this month..."):
    current_month_start = f"{datetime.now().year}-{datetime.now().month:02d}-01"
    current_month_end = f"{datetime.now().year}-{datetime.now().month:02d}-31"

    raw_data = rawg_client.search_games(
        ordering="-rating",
        dates=f"{current_month_start},{current_month_end}",
        page_size=20
    )

# Parse relevant game info into a DataFrame
if raw_data:
    df = pd.DataFrame([{
        "name": game.get("name"),
        "rating": game.get("rating"),
        "released": game.get("released"),
        "ratings_count": game.get("ratings_count"),
        "genres": ", ".join([genre["name"] for genre in game.get("genres", [])]),
        "platforms": ", ".join([p["platform"]["name"] for p in game.get("platforms", [])])
    } for game in raw_data if game.get("rating") > 0])

    if not df.empty:
        # Show basic stats
        st.subheader("📈 Basic Statistics")
        st.write(df.describe(numeric_only=True))

        # Sample preview
        st.subheader("🗂️ Sample Data")
        st.dataframe(df, use_container_width=True)

        # Top 10 rated games
        st.subheader("🏆 Top 10 Rated Games")
        top10 = df.sort_values(by="rating", ascending=False).head(10)
        st.table(top10[["name", "rating", "released"]].reset_index(drop=True))

        # Visualization: Ratings Distribution
        st.subheader("📊 Rating Distribution")
        fig = px.histogram(df, x="rating", nbins=10, color_discrete_sequence=["#f093fb"])
        st.plotly_chart(fig, use_container_width=True)

        # Visualization: Top Genres
        st.subheader("🎮 Top Genres (by Count)")
        genre_counts = df["genres"].str.get_dummies(sep=", ").sum().sort_values(ascending=False).head(10)
        genre_fig = px.bar(genre_counts, orientation="h", title="Top Genres", color_discrete_sequence=["#f5576c"])
        st.plotly_chart(genre_fig, use_container_width=True)
    else:
        st.warning("No high-rated games found for the current month.")
else:
    st.error("Failed to fetch data from RAWG API.")
