import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from rawg_client import RAWGClient

# Initialize API
api_key = st.secrets["RAWG_API_KEY"]
rawg_client = RAWGClient(api_key)

st.title("📊 Game Analytics Dashboard")

# Current year
current_year = datetime.now().year

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
genres_list = [g["name"] for g in rawg_client.get_genres()]
platforms_list = [p["name"] for p in rawg_client.get_platforms()]

selected_genre = st.sidebar.selectbox("Select Genre (optional)", [""] + genres_list)
selected_platform = st.sidebar.selectbox("Select Platform (optional)", [""] + platforms_list)

# Fetch data
try:
    st.subheader(f"🎮 Top Rated Games of {current_year}")
    raw_data = rawg_client.search_games_analytics(
        ordering="-rating",
        genres=selected_genre if selected_genre else None,
        platforms=selected_platform if selected_platform else None,
        year=current_year,
        page_size=40
    )

    # --- Convert to DataFrame ---
