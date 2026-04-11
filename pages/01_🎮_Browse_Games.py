import streamlit as st
from rawg_client import RAWGClient
from helpers import init_session_state, add_to_favorites, remove_from_favorites, is_favorite, load_custom_css, render_theme_toggle


@st.cache_resource
def get_client():
    return RAWGClient(api_key=st.secrets["RAWG_API_KEY"])


@st.cache_data(ttl=3600)
def get_genres_and_platforms(_client):
    return _client.get_genres(), _client.get_platforms()


def parse_year(released_value):
    if not released_value or not isinstance(released_value, str):
        return None
    try:
        return int(released_value[:4])
    except (TypeError, ValueError):
        return None


# Initialize
st.set_page_config(page_title="🎮 Browse Games", page_icon="🎮", layout="wide")
init_session_state()
load_custom_css()
render_theme_toggle()
rawg = get_client()
genres, platforms = get_genres_and_platforms(rawg)

st.title("🎮 Browse Games")
st.markdown("Discover games with advanced filters, saved presets, and wishlist actions.")

if "browse_presets" not in st.session_state:
    st.session_state.browse_presets = {}

# Sidebar - Search options
search_query = st.sidebar.text_input("🔍 Search Games", "")

selected_genre = st.sidebar.selectbox(
    "🎭 Filter by Genre",
    options=["All"] + [genre["name"] for genre in genres],
)

selected_platform = st.sidebar.selectbox(
    "🎮 Filter by Platform",
    options=["All"] + [platform["name"] for platform in platforms],
)

min_rating = st.sidebar.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0, 0.1)
released_after = st.sidebar.number_input("📅 Released After (Year)", min_value=1980, max_value=2100, value=2000)

sort_mapping = {
    "Most Added": "-added",
    "Highest Rated": "-rating",
    "Newest": "-released",
    "Name (A-Z)": "name",
}
sort_label = st.sidebar.selectbox("↕️ Sort by", options=list(sort_mapping.keys()))
sort_option = sort_mapping[sort_label]

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Saved Filter Presets")
preset_name = st.sidebar.text_input("Preset Name", "")
if st.sidebar.button("Save Current Preset"):
    if preset_name.strip():
        st.session_state.browse_presets[preset_name.strip()] = {
            "search_query": search_query,
            "selected_genre": selected_genre,
            "selected_platform": selected_platform,
            "min_rating": min_rating,
            "released_after": int(released_after),
            "sort_label": sort_label,
        }
        st.sidebar.success(f"Saved preset: {preset_name.strip()}")
    else:
        st.sidebar.warning("Enter a preset name before saving.")

preset_options = ["None"] + sorted(st.session_state.browse_presets.keys())
selected_preset = st.sidebar.selectbox("Load Preset", preset_options)
if selected_preset != "None":
    preset = st.session_state.browse_presets[selected_preset]
    st.sidebar.caption(
        f"{preset['selected_genre']} | {preset['selected_platform']} | "
        f"min {preset['min_rating']}⭐ | after {preset['released_after']}"
    )

if st.sidebar.button("Delete Selected Preset") and selected_preset != "None":
    del st.session_state.browse_presets[selected_preset]
    st.sidebar.success(f"Deleted preset: {selected_preset}")
    st.rerun()

# Apply selected preset if user chooses to load
if st.sidebar.button("Apply Selected Preset") and selected_preset != "None":
    preset = st.session_state.browse_presets[selected_preset]
    search_query = preset["search_query"]
    selected_genre = preset["selected_genre"]
    selected_platform = preset["selected_platform"]
    min_rating = preset["min_rating"]
    released_after = preset["released_after"]
    sort_label = preset["sort_label"]
    sort_option = sort_mapping[sort_label]

genre_slug = (
    next((g["slug"] for g in genres if g["name"] == selected_genre), None)
    if selected_genre != "All"
    else None
)
platform_id = (
    next((p["id"] for p in platforms if p["name"] == selected_platform), None)
    if selected_platform != "All"
    else None
)

games = rawg.search_games_browse(
    query=search_query,
    ordering=sort_option,
    genre=genre_slug,
    platform=platform_id,
    page_size=40,
)

# Client-side filtering for score and release year
filtered_games = []
for game in games:
    rating = game.get("rating") or 0
    game_year = parse_year(game.get("released"))
    if rating >= min_rating and (game_year is None or game_year >= int(released_after)):
        filtered_games.append(game)

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Results", len(filtered_games))
with col_b:
    st.metric("Wishlist Items", len(st.session_state.get("user_favorites", [])))

if not filtered_games:
    st.warning("No games found for current filters.")
else:
    for game in filtered_games:
        st.subheader(game.get("name", "Unknown"))
        cols = st.columns([1, 3, 1])
        with cols[0]:
            if game.get("background_image"):
                st.image(game["background_image"], width=140)
        with cols[1]:
            st.write(f"**Released:** {game.get('released', 'N/A')}")
            st.write(f"**Rating:** {game.get('rating', 'N/A')} / 5 ⭐")
            st.write(
                f"**Genres:** {', '.join([genre.get('name', '') for genre in game.get('genres', []) if genre.get('name')]) or 'N/A'}"
            )
        with cols[2]:
            game_id = game.get("id")
            if game_id and is_favorite(game_id):
                if st.button("Remove", key=f"remove_{game_id}"):
                    remove_from_favorites(game_id)
                    st.rerun()
            elif game_id:
                if st.button("Wishlist", key=f"wishlist_{game_id}"):
                    add_to_favorites(game_id, game)
                    st.rerun()
        st.markdown("---")
