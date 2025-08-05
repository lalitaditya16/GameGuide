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

# --- Detect Theme ---
theme = st.get_option("theme.base")
is_dark = theme == "dark"
bg_color = "#0e1117" if is_dark else "#ffffff"
text_color = "#ffffff" if is_dark else "#000000"

# --- Caching Genre & Platform API calls ---
@st.cache_data
def load_genres():
    try:
        return [g["name"] for g in rawg_client.get_genres()]
    except:
        return []

@st.cache_data
def load_platforms():
    try:
        return [p["name"] for p in rawg_client.get_platforms()]
    except:
        return []

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
genres_list = load_genres()
platforms_list = load_platforms()

selected_genre = st.sidebar.selectbox("Select Genre (optional)", [""] + genres_list)
selected_platform = st.sidebar.selectbox("Select Platform (optional)", [""] + platforms_list)

# --- Fetch & Display Data ---
try:
    with st.spinner("Fetching game data..."):
        st.subheader(f"🎮 Top Rated Games of {current_year}")
        raw_data = rawg_client.search_games_analytics(
            ordering="-rating",
            genres=selected_genre if selected_genre else None,
            platforms=selected_platform if selected_platform else None,
            year=current_year,
            page_size=40
        )

        # --- Convert to DataFrame ---
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
            top_genres = genre_counts.head(5)
            other_count = genre_counts[5:].sum()
            genre_display = pd.concat([top_genres, pd.Series({"Others": other_count})]) if other_count > 0 else top_genres

            fig2, ax2 = plt.subplots(facecolor=bg_color)
            fig2.patch.set_facecolor(bg_color)
            ax2.set_facecolor(bg_color)
            wedges, texts, autotexts = ax2.pie(
                genre_display,
                labels=genre_display.index,
                autopct="%1.1f%%",
                startangle=140,
                textprops={"color": text_color}
            )
            for text in texts:
                text.set_color(text_color)
            ax2.axis("equal")
            st.pyplot(fig2)

            # --- Platform Usage ---
            st.markdown("### 🖥 Platform Popularity")
            platform_counts = pd.Series([p for platforms in df["Platforms"] for p in platforms]).value_counts()
            fig3, ax3 = plt.subplots(facecolor=bg_color)
            fig3.patch.set_facecolor(bg_color)
            ax3.set_facecolor(bg_color)

            ax3.bar(range(len(platform_counts.index)), platform_counts.values, color="lightgreen")
            ax3.set_ylabel("Count", color=text_color)
            ax3.set_xticks(range(len(platform_counts.index)))
            ax3.set_xticklabels(platform_counts.index, rotation=45, ha="right", color=text_color)
            ax3.tick_params(colors=text_color)
            st.pyplot(fig3)

            # --- Download CSV ---
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Data as CSV", data=csv, file_name="top_games.csv", mime="text/csv")

            # --- Game Cards ---
            st.markdown("### 🎯 Game Details")
            for _, row in df.iterrows():
                with st.container():
                    cols = st.columns([1, 2])
                    with cols[0]:
                        if row["Image"]:
                            st.image(row["Image"], width=250)
                    with cols[1]:
                        st.subheader(row["Name"])
                        st.markdown(f"⭐ **Rating:** {row['Rating']}")
                        st.markdown(f"📅 **Released:** {row['Released']}")
                        st.markdown(f"🎮 **Platforms:** {', '.join(row['Platforms'])}")
                        st.markdown(f"🏷 **Genres:** {', '.join(row['Genres'])}")
                st.markdown("---")

except Exception as e:
    st.error("Failed to load game analytics.")
    st.exception(e)
