import streamlit as st
from rawg_client import RAWGClient
from helpers import (
    init_session_state, load_custom_css, render_theme_toggle,
    add_to_favorites, remove_from_favorites, is_favorite,
    get_game_status, set_game_status,
)
from config import GAME_STATUS_OPTIONS

st.set_page_config(page_title="Browse Games — GameGuide", page_icon="🎮", layout="wide")
init_session_state()
load_custom_css()


@st.cache_resource
def get_client():
    from config import config
    return RAWGClient(api_key=config.rawg_api_key)


@st.cache_data(ttl=3600)
def get_genres_and_platforms(_client):
    return _client.get_genres(), _client.get_platforms()


def parse_year(val):
    if not isinstance(val, str):
        return None
    try:
        return int(val[:4])
    except (TypeError, ValueError):
        return None


rawg = get_client()
genres, platforms = get_genres_and_platforms(rawg)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    render_theme_toggle()
    st.markdown("---")
    st.markdown(
        '<p style="font-family:Orbitron,monospace; font-size:0.8rem; color:#a78bfa;">FILTERS</p>',
        unsafe_allow_html=True,
    )

    search_query = st.text_input("🔍 Search", "")

    selected_genre = st.selectbox(
        "🎭 Genre",
        options=["All"] + [g["name"] for g in genres],
    )
    selected_platform = st.selectbox(
        "🖥️ Platform",
        options=["All"] + [p["name"] for p in platforms],
    )

    min_rating   = st.slider("⭐ Min Rating", 0.0, 5.0, 0.0, 0.1)
    released_after = st.number_input("📅 Released After", min_value=1980, max_value=2100, value=2000)

    sort_map = {
        "Most Popular": "-added",
        "Highest Rated": "-rating",
        "Newest": "-released",
        "Name (A-Z)": "name",
        "Metacritic": "-metacritic",
    }
    sort_label  = st.selectbox("↕️ Sort by", list(sort_map.keys()))
    sort_option = sort_map[sort_label]

    st.markdown("---")
    st.markdown(
        '<p style="font-family:Orbitron,monospace; font-size:0.8rem; color:#a78bfa;">PRESETS</p>',
        unsafe_allow_html=True,
    )
    if "browse_presets" not in st.session_state:
        st.session_state.browse_presets = {}

    preset_name = st.text_input("Preset name", "")
    if st.button("💾 Save Preset") and preset_name.strip():
        st.session_state.browse_presets[preset_name.strip()] = {
            "search_query": search_query, "selected_genre": selected_genre,
            "selected_platform": selected_platform, "min_rating": min_rating,
            "released_after": int(released_after), "sort_label": sort_label,
        }
        st.sidebar.success(f"Saved: {preset_name.strip()}")

    preset_opts = ["None"] + sorted(st.session_state.browse_presets.keys())
    selected_preset = st.selectbox("Load Preset", preset_opts)

    if st.button("▶ Apply Preset") and selected_preset != "None":
        p = st.session_state.browse_presets[selected_preset]
        search_query    = p["search_query"]
        selected_genre  = p["selected_genre"]
        selected_platform = p["selected_platform"]
        min_rating      = p["min_rating"]
        released_after  = p["released_after"]
        sort_label      = p["sort_label"]
        sort_option     = sort_map[sort_label]

    if st.button("🗑️ Delete Preset") and selected_preset != "None":
        del st.session_state.browse_presets[selected_preset]
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <h1 style="font-family:Orbitron,monospace; font-size:1.6rem; margin:0;
             background:linear-gradient(135deg,#7c3aed,#06b6d4);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             background-clip:text;">
    🎮 BROWSE GAMES
  </h1>
  <p style="color:#64748b; font-size:0.85rem; margin-top:0.3rem;">
    Discover games and track your list — MAL style
  </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Fetch & filter
# ---------------------------------------------------------------------------
genre_slug  = next((g["slug"] for g in genres if g["name"] == selected_genre), None) if selected_genre != "All" else None
platform_id = next((p["id"]   for p in platforms if p["name"] == selected_platform), None) if selected_platform != "All" else None

games = rawg.search_games_browse(
    query=search_query,
    ordering=sort_option,
    genre=genre_slug,
    platform=platform_id,
    page_size=40,
)

filtered = [
    g for g in games
    if (g.get("rating") or 0) >= min_rating
    and (parse_year(g.get("released")) or 9999) >= int(released_after)
]

# Stats row
mc1, mc2, mc3 = st.columns(3)
mc1.metric("Results", len(filtered))
mc2.metric("Your List", sum(1 for g in filtered if is_favorite(g.get("id", 0))))
mc3.metric("Tracked", len(st.session_state.get("game_status_list", {})))

st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Game grid
# ---------------------------------------------------------------------------
STATUS_CHOICES = ["-- None --"] + list(GAME_STATUS_OPTIONS.keys())

if not filtered:
    st.markdown("""
    <div style="text-align:center; padding:3rem; color:#475569;">
        <div style="font-size:3rem; margin-bottom:1rem;">🔍</div>
        <p style="font-family:Orbitron,monospace; font-size:0.9rem;">No games found</p>
        <p style="font-size:0.8rem;">Try adjusting your filters</p>
    </div>
    """, unsafe_allow_html=True)
else:
    COLS = 4
    for row_start in range(0, len(filtered), COLS):
        row_games = filtered[row_start : row_start + COLS]
        cols = st.columns(COLS)

        for col, game in zip(cols, row_games):
            with col:
                game_id = game.get("id")
                name    = game.get("name", "Unknown")
                img     = game.get("background_image") or "https://via.placeholder.com/300x175/0d0f1a/7c3aed?text=No+Image"
                rating  = game.get("rating", 0)
                released = game.get("released", "TBA")
                genres_list = [gn.get("name","") for gn in game.get("genres", [])][:2]
                platforms_list = [p.get("platform", {}).get("name","") for p in game.get("platforms", [])][:2]

                genre_tags = "".join(f'<span class="genre-tag">{g}</span>' for g in genres_list)
                platform_str = " · ".join(platforms_list) or "—"

                current_status = get_game_status(game_id) if game_id else None
                status_html = ""
                if current_status and current_status in GAME_STATUS_OPTIONS:
                    info = GAME_STATUS_OPTIONS[current_status]
                    css_class = {
                        'Playing': 'status-playing',
                        'Completed': 'status-completed',
                        'Want to Play': 'status-want',
                        'On Hold': 'status-hold',
                        'Dropped': 'status-dropped',
                    }.get(current_status, '')
                    status_html = f'<span class="{css_class}">{info["icon"]} {current_status}</span>'

                st.markdown(f"""
                <div class="game-card-new">
                  <img class="game-card-img" src="{img}"
                       onerror="this.src='https://via.placeholder.com/300x175/0d0f1a/7c3aed?text=No+Image'"
                       loading="lazy" alt="{name}">
                  <div class="game-card-body">
                    <p class="game-card-title" title="{name}">{name}</p>
                    <div style="margin-bottom:0.35rem;">
                      <span class="rating-badge">⭐ {rating}/5</span>
                      &nbsp;
                      <span style="font-size:0.66rem; color:#64748b;">📅 {released}</span>
                    </div>
                    <div style="margin-bottom:0.3rem;">{genre_tags}</div>
                    <p class="game-card-meta">🖥️ {platform_str}</p>
                    {f'<div style="margin-top:0.3rem;">{status_html}</div>' if status_html else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                if game_id:
                    # Status selector
                    idx = STATUS_CHOICES.index(current_status) if current_status in STATUS_CHOICES else 0
                    new_status = st.selectbox(
                        "List status",
                        STATUS_CHOICES,
                        index=idx,
                        key=f"status_{game_id}",
                        label_visibility="collapsed",
                    )
                    if new_status != current_status:
                        set_game_status(game_id, new_status)
                        st.rerun()

                    # Wishlist toggle
                    if is_favorite(game_id):
                        if st.button("❤️ Remove", key=f"rem_{game_id}", use_container_width=True):
                            remove_from_favorites(game_id)
                            st.rerun()
                    else:
                        if st.button("🤍 Wishlist", key=f"add_{game_id}", use_container_width=True):
                            add_to_favorites(game_id, game)
                            st.rerun()

                st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)
