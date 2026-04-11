import streamlit as st
from rawg_client import RAWGClient
from helpers import init_session_state, add_to_favorites, remove_from_favorites, is_favorite, load_custom_css, render_theme_toggle


@st.cache_resource
def get_client():
    return RAWGClient(api_key=st.secrets["RAWG_API_KEY"])


def safe_join(values):
    return ", ".join(values) if values else "N/A"


def extract_game_snapshot(client, query):
    match = client.search_best_match(query)
    if not match:
        return None

    details = client.get_game_details(match["id"])
    genres = [g.get("name") for g in (details.get("genres") or []) if g and g.get("name")]
    platforms = [
        p["platform"].get("name")
        for p in (details.get("platforms") or [])
        if p and p.get("platform") and p["platform"].get("name")
    ]

    return {
        "id": details.get("id"),
        "name": details.get("name", "Unknown"),
        "rating": details.get("rating"),
        "ratings_count": details.get("ratings_count"),
        "metacritic": details.get("metacritic"),
        "released": details.get("released"),
        "playtime": details.get("playtime"),
        "genres": genres,
        "platforms": platforms,
        "esrb": (details.get("esrb_rating") or {}).get("name", "N/A"),
        "website": details.get("website", ""),
        "image": details.get("background_image"),
    }


def render_game_panel(game, col):
    with col:
        st.subheader(game["name"])
        if game.get("image"):
            st.image(game["image"], use_column_width=True)

        st.write(f"⭐ Rating: {game.get('rating', 'N/A')} ({game.get('ratings_count', 0)} ratings)")
        st.write(f"🏆 Metacritic: {game.get('metacritic', 'N/A')}")
        st.write(f"📅 Released: {game.get('released', 'N/A')}")
        st.write(f"⏱ Estimated Playtime: {game.get('playtime', 'N/A')} hours")
        st.write(f"🎭 Genres: {safe_join(game.get('genres', []))}")
        st.write(f"🕹 Platforms: {safe_join(game.get('platforms', []))}")
        st.write(f"🔞 ESRB: {game.get('esrb', 'N/A')}")

        if game.get("website"):
            st.markdown(f"🌐 [Official Website]({game['website']})")

        game_id = game.get("id")
        if game_id and is_favorite(game_id):
            if st.button("Remove from Wishlist", key=f"compare_remove_{game_id}"):
                remove_from_favorites(game_id)
                st.rerun()
        elif game_id:
            if st.button("Add to Wishlist", key=f"compare_add_{game_id}"):
                add_to_favorites(game_id, game)
                st.rerun()


def winner_text(left_game, right_game):
    left_score = (left_game.get("rating") or 0) + ((left_game.get("metacritic") or 0) / 20)
    right_score = (right_game.get("rating") or 0) + ((right_game.get("metacritic") or 0) / 20)

    if left_score > right_score:
        return f"🏁 {left_game['name']} looks stronger overall on review metrics."
    if right_score > left_score:
        return f"🏁 {right_game['name']} looks stronger overall on review metrics."
    return "🤝 Both games are very close based on review metrics."


st.set_page_config(page_title="Compare Games", page_icon="⚔️", layout="wide")
init_session_state()
load_custom_css()
render_theme_toggle()
client = get_client()

st.title("⚔️ Compare Games")
st.markdown("Search two games and compare them side-by-side before you decide what to play.")

col_a, col_b = st.columns(2)
with col_a:
    game_a_query = st.text_input("First game", placeholder="e.g., Elden Ring")
with col_b:
    game_b_query = st.text_input("Second game", placeholder="e.g., Baldur's Gate 3")

if st.button("Compare Now", type="primary"):
    if not game_a_query or not game_b_query:
        st.warning("Enter both game names to compare.")
    else:
        with st.spinner("Building comparison..."):
            game_a = extract_game_snapshot(client, game_a_query)
            game_b = extract_game_snapshot(client, game_b_query)

        if not game_a or not game_b:
            st.error("Could not find one or both games. Try more precise names.")
        else:
            left_col, right_col = st.columns(2)
            render_game_panel(game_a, left_col)
            render_game_panel(game_b, right_col)

            st.markdown("---")
            st.subheader("Quick Verdict")
            st.info(winner_text(game_a, game_b))

            comparison_rows = [
                ("Rating", game_a.get("rating", "N/A"), game_b.get("rating", "N/A")),
                ("Metacritic", game_a.get("metacritic", "N/A"), game_b.get("metacritic", "N/A")),
                ("Released", game_a.get("released", "N/A"), game_b.get("released", "N/A")),
                ("Playtime (hours)", game_a.get("playtime", "N/A"), game_b.get("playtime", "N/A")),
                ("ESRB", game_a.get("esrb", "N/A"), game_b.get("esrb", "N/A")),
            ]

            st.table({
                "Metric": [row[0] for row in comparison_rows],
                game_a["name"]: [row[1] for row in comparison_rows],
                game_b["name"]: [row[2] for row in comparison_rows],
            })

st.markdown("---")
st.caption(f"Wishlist size: {len(st.session_state.get('user_favorites', []))}")
