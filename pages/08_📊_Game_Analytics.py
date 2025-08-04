import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from rawg_client import RAWGClient
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Game Analytics", page_icon="📊", layout="wide")

st.title("📊 Game Analytics")
st.markdown("Explore game trends, ratings, and releases using data from the RAWG API.")

# Initialize RAWG client
rawg = RAWGClient(api_key=st.secrets["RAWG_API_KEY"])

# Sidebar filters
st.sidebar.header("🔎 Filters")
current_year = datetime.now().year
years = list(range(2000, current_year + 1))[::-1]
selected_year = st.sidebar.selectbox("Release Year", years, index=0)

# Genre and platform filters (optional)
all_genres = rawg.get_genres()
genre_options = ["All"] + [genre["name"] for genre in all_genres]
selected_genre = st.sidebar.selectbox("Genre", genre_options)
genre_param = None if selected_genre == "All" else selected_genre.lower()

all_platforms = rawg.get_platforms()
platform_options = ["All"] + [platform["name"] for platform in all_platforms]
selected_platform = st.sidebar.selectbox("Platform", platform_options)
platform_param = None if selected_platform == "All" else selected_platform.lower()

# Fetch game data
with st.spinner("Fetching game data..."):
    try:
        games_data = rawg.search_games_analytics(
            genres=genre_param,
            platforms=platform_param,
            ordering="-added",
            page_size=100,
            year=selected_year
        )
    except Exception as e:
        st.error(f"Failed to fetch game data: {e}")
        st.stop()

if not games_data:
    st.warning("No games found for the selected filters.")
    st.stop()

# Raw API response sample (debug)


# Data Preprocessing
df = pd.DataFrame(games_data)
df["release_date"] = pd.to_datetime(df["released"], errors="coerce")
df["rating"] = df["rating"].fillna(0)
df["name"] = df["name"].astype(str)

# Debug: Show rating distribution
st.write("Rating Value Distribution", df["rating"].describe())
st.write("Sample Data", df[["name", "rating", "released"]].head(20))

# Visualization 1: Ratings Distribution
st.subheader("⭐ Game Ratings Distribution")
fig_rating = px.histogram(df, x="rating", nbins=20, title="Game Ratings Histogram", color_discrete_sequence=["indigo"])
st.plotly_chart(fig_rating, use_container_width=True)

# Visualization 2: Top Rated Games
top_games = df[df["rating"] > 0].sort_values(by="rating", ascending=False).head(10)
st.subheader("🏆 Top 10 Rated Games")

# Build grid options
gb = GridOptionsBuilder.from_dataframe(top_games[["name", "rating", "released"]])
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_default_column(wrapText=True, autoHeight=True)
grid_options = gb.build()

# Render interactive, styled table
AgGrid(top_games[["name", "rating", "released"]], gridOptions=grid_options, theme="material", height=400)

# Visualization 3: Release Timeline
st.subheader("📅 Release Timeline")
release_df = df.dropna(subset=["release_date"])
release_df["release_month"] = release_df["release_date"].dt.to_period("M").astype(str)
timeline = release_df.groupby("release_month").size().reset_index(name="count")
fig_timeline = px.bar(timeline, x="release_month", y="count", title="Games Released Over Time", color_discrete_sequence=["orange"])
st.plotly_chart(fig_timeline, use_container_width=True)

# Visualization 4: Platform distribution
st.subheader("🕹️ Platforms Distribution")
platform_counts = {}
for game in games_data:
    for platform in game.get("platforms", []):
        name = platform["platform"]["name"]
        platform_counts[name] = platform_counts.get(name, 0) + 1

platform_df = pd.DataFrame(platform_counts.items(), columns=["Platform", "Count"])
fig_platforms = px.pie(platform_df, names="Platform", values="Count", title="Game Platform Distribution")
st.plotly_chart(fig_platforms, use_container_width=True)
