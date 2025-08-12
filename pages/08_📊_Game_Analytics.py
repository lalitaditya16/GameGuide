import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from rawg_client import RAWGClient

# --- Initialize API ---
api_key = st.secrets["RAWG_API_KEY"]
rawg_client = RAWGClient(api_key)

st.set_page_config(page_title="Game Analytics", layout="wide")
st.title("📊 Game Analytics Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")
genres_list = [g["name"] for g in rawg_client.get_genres()]
platforms_list = [p["name"] for p in rawg_client.get_platforms()]

# Year selector (from 2015 to current year)
current_year = datetime.now().year
selected_year = st.sidebar.selectbox("Select Year", list(range(current_year, 2014, -1)))



# --- Theme Colors ---
theme = st.get_option("theme.base")
bg_color = "#0e1117" if theme == "dark" else "#ffffff"
text_color = "#ffffff" if theme == "dark" else "#000000"

# --- Fetch and Display Data ---
try:
    st.subheader(f"🎮 Top Rated Games of {selected_year}")
    raw_data = rawg_client.search_games_analytics(
        ordering="-rating",
        year=selected_year,
        page_size=40
    )

    # Convert to DataFrame
    df = pd.DataFrame([{
        "Name": game.get("name"),
        "Rating": game.get("rating"),
        "Released": game.get("released"),
        "Genres": [g["name"] for g in game.get("genres", [])],
        "Platforms": [p["platform"]["name"] for p in game.get("platforms", []) if p.get("platform")],
        "Image": game.get("background_image"),
    } for game in raw_data])

    if df.empty:
        st.warning("No games found for selected filters.")
    else:
        # --- Ratings Chart ---
        st.markdown("### 📈 Game Ratings")
        top_ratings = df.sort_values("Rating", ascending=False).head(10)

        fig, ax = plt.subplots(facecolor=bg_color)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        ax.barh(top_ratings["Name"], top_ratings["Rating"], color="skyblue")
        ax.set_xlabel("Rating", color=text_color)
        ax.set_ylabel("Game", color=text_color)
        ax.tick_params(colors=text_color)
        ax.invert_yaxis()

        st.pyplot(fig)

        # --- Genre Pie Chart ---
        st.markdown("### 🧩 Genre Distribution")
        genre_counts = pd.Series([g for genres in df["Genres"] for g in genres]).value_counts()
        fig2, ax2 = plt.subplots(facecolor=bg_color)
        fig2.patch.set_facecolor(bg_color)
        ax2.set_facecolor(bg_color)

        ax2.pie(genre_counts, labels=genre_counts.index, autopct="%1.1f%%", startangle=140, textprops={'color': text_color})
        ax2.axis("equal")
        st.pyplot(fig2)

        # --- Platform Usage ---
        st.markdown("### 🖥 Platform Popularity")
        platform_counts = pd.Series([p for platforms in df["Platforms"] for p in platforms]).value_counts()
        fig3, ax3 = plt.subplots(facecolor=bg_color)
        fig3.patch.set_facecolor(bg_color)
        ax3.set_facecolor(bg_color)

        ax3.bar(platform_counts.index, platform_counts.values, color="orange")
        ax3.set_ylabel("Count", color=text_color)
        ax3.tick_params(colors=text_color)
        ax3.set_xticklabels(platform_counts.index, rotation=45, ha="right", color=text_color)
        st.pyplot(fig3)

        # --- Game Cards ---
        st.markdown("### 🎯 Game Details")
        for _, row in df.iterrows():
            st.markdown(f"#### {row['Name']}")
            st.write(f"⭐ Rating: {row['Rating']} | 📅 Released: {row['Released']}")
            st.write(f"🎮 Platforms: {', '.join(row['Platforms'])}")
            st.write(f"🏷 Genres: {', '.join(row['Genres'])}")
            if row["Image"]:
                st.image(row["Image"], width=600)
            st.markdown("---")

except Exception as e:
    st.error("Failed to load game analytics.")
    st.exception(e)
try:
    st.subheader(f"🔥 All-Time Peak Players for Games Released in {selected_year}")

# Fetch games from RAWG
    games_year = rawg_client.get_games_with_steam_ids(
    year=selected_year,
    page_size=20
)

    games_peak_data = []
    for game in games_year:
    # Find Steam App ID from RAWG stores list
        steam_info = next(
            (store for store in game.get("stores", []) if store["store"]["name"].lower() == "steam"),
            None
        )
        if steam_info and "url" in steam_info:
            try:
                steam_url = steam_info["url"]
                app_id = steam_url.split("/app/")[1].split("/")[0]
                peak_players = steam_client.get_all_time_peak_players(app_id)
            except:
                peak_players = None
        else:
            peak_players = None

        games_peak_data.append({
            "Name": game.get("name"),
            "Released": game.get("released"),
            "Peak Players": peak_players,
            "Image": game.get("background_image")
        })

# Sort by peak players
    df_peak = pd.DataFrame(games_peak_data).sort_values(
        by="Peak Players", ascending=False, na_position='last'
    )

    if df_peak.empty:
        st.warning(f"No Steam data found for {selected_year}.")
    else:
        st.dataframe(df_peak[["Name", "Released", "Peak Players"]])

        st.markdown("### 🏆 Top 5 Games by Peak Players")
        for _, row in df_peak.head(5).iterrows():
            st.markdown(f"#### {row['Name']}")
            st.write(f"📅 Released: {row['Released']} | 👥 Peak Players: {row['Peak Players']}")
            if row["Image"]:
                st.image(row["Image"], width=600)
            st.markdown("---")
except Exception as e:
    st.error("Failed to load player counts.")
    st.exception(e)
