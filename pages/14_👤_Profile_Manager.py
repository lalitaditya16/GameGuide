import streamlit as st

from rawg_client import RAWGClient
from helpers import (
    init_session_state,
    load_custom_css,
    render_theme_toggle,
    get_profiles,
    get_active_profile_name,
    set_active_profile,
    create_profile,
    delete_profile,
    get_user_preferences,
    update_user_preferences,
    get_favorites,
    get_played_games,
    add_played_game,
    remove_played_game,
)


@st.cache_resource
def get_client():
    from config import config
    return RAWGClient(api_key=config.rawg_api_key)


@st.cache_data(ttl=3600)
def get_taxonomy(_client):
    genres = [g.get("name") for g in _client.get_genres() if g.get("name")]
    platforms = [p.get("name") for p in _client.get_platforms() if p.get("name")]
    return genres, platforms


st.set_page_config(page_title="Profile Manager", page_icon="👤", layout="wide")
init_session_state()
load_custom_css()
render_theme_toggle()

client = get_client()
all_genres, all_platforms = get_taxonomy(client)

st.title("👤 Profile Manager")
st.markdown("Create profiles, set preferences, and log the games you have played.")

profiles = get_profiles()
active_profile = get_active_profile_name()

st.subheader("Profile")
col_p1, col_p2, col_p3 = st.columns([2, 2, 2])

with col_p1:
    selected_profile = st.selectbox("Active Profile", profiles, index=profiles.index(active_profile) if active_profile in profiles else 0)
    if selected_profile != active_profile:
        if set_active_profile(selected_profile):
            st.success(f"Switched to profile: {selected_profile}")
            st.rerun()

with col_p2:
    new_profile_name = st.text_input("Create New Profile", placeholder="e.g., Lalit")
    if st.button("Create Profile"):
        if create_profile(new_profile_name):
            st.success(f"Created profile: {new_profile_name.strip()}")
            st.rerun()
        else:
            st.warning("Profile name is invalid or already exists.")

with col_p3:
    delete_target = st.selectbox("Delete Profile", profiles, key="delete_profile_target")
    if st.button("Delete Selected Profile"):
        if delete_profile(delete_target):
            st.success(f"Deleted profile: {delete_target}")
            st.rerun()
        else:
            st.warning("Cannot delete this profile. Keep at least one profile.")

st.markdown("---")
st.subheader("Preferences")

prefs = get_user_preferences()
col_pref1, col_pref2 = st.columns(2)

with col_pref1:
    preferred_genres = st.multiselect(
        "Favorite Genres",
        options=all_genres,
        default=[g for g in prefs.get("favorite_genres", []) if g in all_genres],
    )

with col_pref2:
    preferred_platforms = st.multiselect(
        "Favorite Platforms",
        options=all_platforms,
        default=[p for p in prefs.get("favorite_platforms", []) if p in all_platforms],
    )

items_per_page = st.slider("Items Per Page", 10, 60, int(prefs.get("items_per_page", 20)), 5)
enable_ai = st.toggle("Enable AI Features", value=bool(prefs.get("enable_ai", True)))

if st.button("Save Preferences"):
    update_user_preferences(
        {
            "favorite_genres": preferred_genres,
            "favorite_platforms": preferred_platforms,
            "items_per_page": items_per_page,
            "enable_ai": enable_ai,
        }
    )
    st.success("Preferences saved.")

st.markdown("---")
st.subheader("Played Games Log")

wishlist = get_favorites()
played_games = get_played_games()

m1, m2 = st.columns(2)
with m1:
    st.metric("Wishlist", len(wishlist))
with m2:
    st.metric("Played", len(played_games))

col_log1, col_log2 = st.columns([2, 1])
with col_log1:
    search_name = st.text_input("Log a Played Game", placeholder="Enter game title")
with col_log2:
    source_mode = st.selectbox("Source", ["Search", "Wishlist"])

hours_played = st.number_input("Hours Played", min_value=0.0, max_value=5000.0, value=0.0, step=0.5)
user_rating = st.slider("Your Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.5)
played_note = st.text_area("Played Note", placeholder="What did you like or dislike?", height=80)

selected_wishlist_name = None
if source_mode == "Wishlist":
    wishlist_options = [g.get("name", "Unknown") for g in wishlist]
    if wishlist_options:
        selected_wishlist_name = st.selectbox("Select Wishlist Game", wishlist_options)
    else:
        st.info("Your wishlist is empty. Switch source to Search or add wishlist items first.")

if st.button("Add To Played Log", type="primary"):
    target_game = None
    if source_mode == "Wishlist" and selected_wishlist_name:
        target_game = next((g for g in wishlist if g.get("name") == selected_wishlist_name), None)
    elif source_mode == "Search" and search_name.strip():
        target_game = client.search_best_match(search_name.strip())

    if not target_game:
        st.warning("Could not find a game to log.")
    else:
        if add_played_game(target_game, hours_played=hours_played, user_rating=user_rating, note=played_note):
            st.success(f"Logged as played: {target_game.get('name', 'Unknown')}")
            st.rerun()
        else:
            st.error("Failed to log played game.")

st.markdown("---")
st.subheader("Your Played Games")

if not played_games:
    st.info("No played games logged yet.")
else:
    for game in sorted(played_games, key=lambda x: x.get("last_played_at", ""), reverse=True):
        g1, g2, g3 = st.columns([1, 3, 1])
        with g1:
            if game.get("image"):
                st.image(game["image"], width=130)
        with g2:
            st.markdown(f"### {game.get('name', 'Unknown')}")
            st.write(f"⏱ Hours: {game.get('hours_played', 0)}")
            st.write(f"⭐ Your Rating: {game.get('user_rating', 'N/A')} / 5")
            st.write(f"📅 Last Played: {game.get('last_played_at', 'N/A')}")
            if game.get("note"):
                st.caption(game.get("note"))
        with g3:
            if st.button("Remove", key=f"remove_played_{game.get('id')}"):
                remove_played_game(game.get("id"))
                st.rerun()

        st.markdown("---")
