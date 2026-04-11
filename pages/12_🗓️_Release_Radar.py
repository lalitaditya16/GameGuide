import streamlit as st
from rawg_client import RAWGClient
from helpers import init_session_state, add_to_favorites, remove_from_favorites, is_favorite, load_custom_css, render_theme_toggle


@st.cache_resource
def get_client():
    return RAWGClient(api_key=st.secrets["RAWG_API_KEY"])


@st.cache_data(ttl=3600)
def get_taxonomy(_client):
    return _client.get_genres(), _client.get_platforms()


st.set_page_config(page_title="Release Radar", page_icon="🗓️", layout="wide")
init_session_state()
load_custom_css()
render_theme_toggle()
client = get_client()
genres, platforms = get_taxonomy(client)

st.title("🗓️ Release Radar")
st.markdown("Track upcoming game releases and add promising titles to your wishlist.")

col_filter_1, col_filter_2, col_filter_3 = st.columns(3)

with col_filter_1:
    days_ahead = st.selectbox("Time Window", [30, 60, 90, 180, 365], index=2)

with col_filter_2:
    selected_genre = st.selectbox(
        "Genre",
        ["All"] + [g["name"] for g in genres],
    )

with col_filter_3:
    selected_platform = st.selectbox(
        "Platform",
        ["All"] + [p["name"] for p in platforms],
    )

genre_slug = next((g["slug"] for g in genres if g["name"] == selected_genre), None) if selected_genre != "All" else None
platform_id = next((p["id"] for p in platforms if p["name"] == selected_platform), None) if selected_platform != "All" else None

with st.spinner("Fetching upcoming releases..."):
    upcoming = client.search_upcoming_games(
        days_ahead=int(days_ahead),
        genre=genre_slug,
        platform=platform_id,
        page_size=40,
    )

if not upcoming:
    st.info("No upcoming releases found for this filter set.")
else:
    st.success(f"Found {len(upcoming)} upcoming titles")

    for game in upcoming:
        name = game.get("name", "Unknown")
        game_id = game.get("id")
        released = game.get("released", "TBA")
        rating = game.get("rating", "N/A")
        genres_text = ", ".join([g.get("name") for g in (game.get("genres") or []) if g and g.get("name")]) or "N/A"
        platforms_text = ", ".join([
            p["platform"].get("name")
            for p in (game.get("platforms") or [])
            if p and p.get("platform") and p["platform"].get("name")
        ]) or "N/A"

        c1, c2, c3 = st.columns([1, 3, 1])
        with c1:
            if game.get("background_image"):
                st.image(game["background_image"], width=140)
        with c2:
            st.subheader(name)
            st.write(f"📅 Release Date: {released}")
            st.write(f"⭐ Rating: {rating} / 5")
            st.write(f"🎭 Genres: {genres_text}")
            st.write(f"🎮 Platforms: {platforms_text}")
        with c3:
            if game_id and is_favorite(game_id):
                if st.button("Remove", key=f"rr_remove_{game_id}"):
                    remove_from_favorites(game_id)
                    st.rerun()
            elif game_id:
                if st.button("Wishlist", key=f"rr_add_{game_id}"):
                    add_to_favorites(game_id, game)
                    st.rerun()

        st.markdown("---")

st.caption(f"Wishlist size: {len(st.session_state.get('user_favorites', []))}")
