import streamlit as st
from rawg_client import RAWGClient
from helpers import clean_description, load_custom_css

st.set_page_config(page_title="Advanced Game Search", layout="wide")
st.title("🔍 Advanced Game Search")
load_custom_css()

api_key = st.secrets["RAWG_API_KEY"]
client = RAWGClient(api_key)

left, right = st.columns([1, 2])

with left:
    game_name = st.text_input("Enter a game name", placeholder="e.g., Baldur's Gate 3")

with right:
    if game_name:
        with st.spinner("Searching for game..."):
            game = client.search_best_match(game_name)

        if game:
            st.markdown("<div class='section-title'><span class='dot'></span>Result</div>", unsafe_allow_html=True)
            if game.get("background_image"):
                st.image(game["background_image"], use_column_width=True)

            st.subheader(game['name'])
            st.caption(f"Released: {game.get('released', 'N/A')} • Rating: {game.get('rating', 'N/A')} / 5")
            st.caption(f"Genres: {', '.join([genre['name'] for genre in game.get('genres', [])])}")
            st.caption(f"Platforms: {', '.join([platform['platform']['name'] for platform in game.get('platforms', [])])}")

            # Get full game details
            game_details = client.get_game_details(game['id'])

            if game_details:
                st.markdown("<div class='section-title'><span class='dot'></span>📖 Game Details</div>", unsafe_allow_html=True)

                description = game_details.get("description_raw", "No description available.")
                developers = ', '.join([dev['name'] for dev in game_details.get('developers', [])])
                publishers = ', '.join([pub['name'] for pub in game_details.get('publishers', [])])
                website = game_details.get('website', '')

                # Safely access ESRB info
                esrb_data = game_details.get('esrb_rating')
                esrb = esrb_data.get('name') if isinstance(esrb_data, dict) else 'N/A'

                st.markdown(clean_description(description))
                if developers:
                    st.markdown(f"**Developer(s):** {developers}")
                if publishers:
                    st.markdown(f"**Publisher(s):** {publishers}")
                st.markdown(f"**ESRB Rating:** {esrb}")
                if website:
                    st.markdown(f"**Website:** [Visit Official Site]({website})")

            # Screenshots
            screenshots = client.get_game_screenshots(game['id'])
            if screenshots:
                st.markdown("<div class='section-title'><span class='dot'></span>🖼️ Screenshots</div>", unsafe_allow_html=True)
                shots = [s.get("image") for s in screenshots if isinstance(s.get("image"), str)]
                grid = [
                    f"<div class='game-card'><div class='card-image'><img src='{url}' /><div class='card-overlay'></div></div></div>"
                    for url in shots[:8]
                ]
                st.markdown("<div class='grid'>" + "".join(grid) + "</div>", unsafe_allow_html=True)

            # Achievements
            achievements = client.get_achievements_by_game_id(game['id'])

            if achievements and isinstance(achievements, list):
                st.markdown("<div class='section-title'><span class='dot'></span>🏆 Achievements</div>", unsafe_allow_html=True)

                for ach in achievements:
                    percent = ach.get("percent")
                    try:
                        ach["percent"] = float(percent)
                    except (ValueError, TypeError):
                        ach["percent"] = None

                cards = []
                for ach in achievements[:20]:
                    image = ach.get("image")
                    name = ach.get("name")
                    description = ach.get("description", "No description")
                    percent = ach.get("percent")

                    cards.append(f"""
                    <div class='game-card'>
                        <div class='card-image'>
                            {f"<img src='{image}' />" if image else ''}
                            <div class='card-overlay'></div>
                        </div>
                        <div class='card-body'>
                            <div class='card-title'>{name}</div>
                            <div class='meta'><span class='tag'>{(percent and f"{percent:.2f}%") or '—' } unlocked</span></div>
                        </div>
                    </div>
                    """)

                st.markdown("<div class='grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)
            else:
                st.info("No achievements available for this game.")
        else:
            st.error("Game not found. Please check the name and try again.")
