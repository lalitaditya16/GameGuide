import json
from datetime import datetime

import streamlit as st

from helpers import (
    init_session_state,
    get_favorites,
    remove_from_favorites,
    update_favorite_note,
    export_favorites_json,
    import_favorites_json,
)


st.set_page_config(page_title="Wishlist Manager", page_icon="💖", layout="wide")
init_session_state()

st.title("💖 Wishlist Manager")
st.markdown("Manage saved games with notes, sorting, and backup import/export.")

favorites = get_favorites()

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Total Wishlist Games", len(favorites))
with col_b:
    avg_rating = 0.0
    rating_values = [f.get("rating") for f in favorites if isinstance(f.get("rating"), (int, float))]
    if rating_values:
        avg_rating = sum(rating_values) / len(rating_values)
    st.metric("Average Rating", f"{avg_rating:.2f}")
with col_c:
    noted = len([f for f in favorites if (f.get("note") or "").strip()])
    st.metric("Games With Notes", noted)

st.markdown("---")

sort_option = st.selectbox(
    "Sort Wishlist",
    ["Recently Added", "Rating High to Low", "Name A-Z"],
)

if sort_option == "Rating High to Low":
    favorites = sorted(favorites, key=lambda x: (x.get("rating") or 0), reverse=True)
elif sort_option == "Name A-Z":
    favorites = sorted(favorites, key=lambda x: (x.get("name") or "").lower())
else:
    favorites = sorted(
        favorites,
        key=lambda x: x.get("added_at") or datetime.min.isoformat(),
        reverse=True,
    )

if not favorites:
    st.info("Your wishlist is empty. Add games from Browse, Compare, or Release Radar pages.")
else:
    for fav in favorites:
        game_id = fav.get("id")
        name = fav.get("name", "Unknown")

        c1, c2, c3 = st.columns([1, 3, 1])

        with c1:
            if fav.get("image"):
                st.image(fav["image"], width=130)

        with c2:
            st.subheader(name)
            st.write(f"⭐ Rating: {fav.get('rating', 'N/A')}")
            st.caption(f"Added: {fav.get('added_at', 'N/A')}")

            note_key = f"note_{game_id}"
            default_note = fav.get("note", "")
            note_value = st.text_area(
                "Personal Note",
                value=default_note,
                key=note_key,
                placeholder="Why do you want to play this game?",
                height=90,
            )
            if st.button("Save Note", key=f"save_note_{game_id}"):
                updated = update_favorite_note(game_id, note_value)
                if updated:
                    st.success("Note saved.")
                else:
                    st.warning("Could not update note.")

        with c3:
            if st.button("Remove", key=f"remove_wishlist_{game_id}"):
                remove_from_favorites(game_id)
                st.rerun()

        st.markdown("---")

st.subheader("Backup and Restore")
col_export, col_import = st.columns(2)

with col_export:
    favorites_json = export_favorites_json()
    st.download_button(
        label="Export Wishlist JSON",
        data=favorites_json,
        file_name="gameguide_wishlist.json",
        mime="application/json",
    )

with col_import:
    uploaded_file = st.file_uploader("Import Wishlist JSON", type=["json"])
    import_mode = st.radio("Import Mode", ["merge", "replace"], horizontal=True)

    if uploaded_file is not None and st.button("Import Wishlist"):
        try:
            payload = uploaded_file.read().decode("utf-8")
            result = import_favorites_json(payload, mode=import_mode)
            st.success(
                f"Imported {result['imported']} items, skipped {result['skipped']} items."
            )
            st.rerun()
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Import failed: {e}")
