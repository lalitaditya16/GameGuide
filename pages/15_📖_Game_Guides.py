"""
Game Guides page — AI walkthroughs, YouTube video guides, IGDB lore, community tips.
All APIs used are free:
  - Groq (AI guide)   — free tier, needs GROQ_API_KEY
  - YouTube Data v3   — free 10k units/day, needs YOUTUBE_API_KEY
  - IGDB via Twitch   — free, needs IGDB_CLIENT_ID + IGDB_CLIENT_SECRET
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import datetime
from helpers import init_session_state, load_custom_css, render_theme_toggle, get_chat_manager
from config import config
from youtube_client import YouTubeClient
from igdb_client import IGDBClient

st.set_page_config(page_title="Game Guides — GameGuide", page_icon="📖", layout="wide")
init_session_state()
load_custom_css()

TIPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "community_tips.json")


def load_tips() -> dict:
    try:
        if os.path.exists(TIPS_FILE):
            with open(TIPS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_tips(tips: dict):
    os.makedirs(os.path.dirname(TIPS_FILE), exist_ok=True)
    with open(TIPS_FILE, "w", encoding="utf-8") as f:
        json.dump(tips, f, indent=2)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    render_theme_toggle()
    st.markdown("---")

    st.markdown(
        '<p style="font-family:Orbitron,monospace; font-size:0.8rem; color:#a78bfa;">API STATUS</p>',
        unsafe_allow_html=True,
    )

    chat_manager = get_chat_manager()
    yt  = YouTubeClient(config.youtube_api_key)
    igdb = IGDBClient(config.igdb_client_id, config.igdb_client_secret)

    st.write("🤖 AI Guide:", "✅ Online" if chat_manager.is_available() else "❌ Needs GROQ_API_KEY")
    st.write("▶️ YouTube:", "✅ Online" if yt.is_available() else "⚠️ No key — link fallback")
    st.write("📚 IGDB:", "✅ Online" if igdb.is_available() else "⚠️ No key — skipped")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#475569; line-height:1.6;">
      <strong style="color:#a78bfa;">Free API setup:</strong><br>
      • <strong>YouTube:</strong> console.cloud.google.com<br>
      • <strong>IGDB:</strong> dev.twitch.tv/console/apps<br>
      Add keys to your .env file.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <h1 style="font-family:Orbitron,monospace; font-size:1.6rem; margin:0;
             background:linear-gradient(135deg,#7c3aed,#06b6d4);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             background-clip:text;">
    📖 GAME GUIDES
  </h1>
  <p style="color:#64748b; font-size:0.85rem; margin-top:0.3rem;">
    AI walkthroughs · YouTube videos · Game lore · Community tips
  </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
search_col, btn_col = st.columns([5, 1])
with search_col:
    game_name = st.text_input(
        "Search for a game",
        placeholder="e.g. Elden Ring, Hollow Knight, Red Dead Redemption 2",
        label_visibility="collapsed",
    )
with btn_col:
    search_clicked = st.button("🔍 Search", use_container_width=True)

if not game_name:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#475569;">
      <div style="font-size:3.5rem; margin-bottom:1rem;">📖</div>
      <p style="font-family:Orbitron,monospace; font-size:0.9rem; color:#7c3aed;">Search for any game to get started</p>
      <p style="font-size:0.8rem;">AI guide · YouTube walkthroughs · Lore · Community tips</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_ai, tab_yt, tab_igdb, tab_tips = st.tabs([
    "🤖 AI Guide",
    "▶️ Video Guides",
    "📚 Game Info",
    "💬 Community Tips",
])

# ── Tab 1: AI Guide ────────────────────────────────────────────────────────
with tab_ai:
    st.markdown(
        f'<p style="font-family:Orbitron,monospace; font-size:0.85rem; color:#a78bfa; margin-bottom:0.8rem;">'
        f'AI-GENERATED GUIDE FOR: {game_name.upper()}</p>',
        unsafe_allow_html=True,
    )

    guide_type = st.radio(
        "Guide type",
        ["Beginner Guide", "Walkthrough Tips", "Trophy/Achievement Guide", "Story Summary (no spoilers)"],
        horizontal=True,
    )

    if st.button("✨ Generate Guide", type="primary"):
        if not chat_manager.is_available():
            st.error("AI is offline — add GROQ_API_KEY to your .env file.")
        else:
            prompts = {
                "Beginner Guide": f"Write a structured beginner guide for \"{game_name}\" covering: quick start, core mechanics, pro tips, and common mistakes. Keep it practical.",
                "Walkthrough Tips": f"Give a step-by-step walkthrough guide for the early game of \"{game_name}\". Include key objectives, important decisions, and things not to miss.",
                "Trophy/Achievement Guide": f"List the most important trophies/achievements in \"{game_name}\" and how to unlock them efficiently. Group by difficulty.",
                "Story Summary (no spoilers)": f"Give a spoiler-free story summary of \"{game_name}\" including the setting, main characters, and overall premise. Do not reveal major plot twists.",
            }

            with st.spinner(f"Generating {guide_type}..."):
                from groq import Groq
                client = Groq(api_key=config.groq_api_key)

                def stream():
                    resp = client.chat.completions.create(
                        model=config.groq_model,
                        messages=[
                            {"role": "system", "content": "You are an expert gaming guide writer. Write clear, structured, practical guides."},
                            {"role": "user",   "content": prompts[guide_type]},
                        ],
                        max_tokens=1200,
                        temperature=0.15,
                        stream=True,
                    )
                    for chunk in resp:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta

                st.markdown('<div class="chat-bubble-ai">', unsafe_allow_html=True)
                st.write_stream(stream())
                st.markdown("</div>", unsafe_allow_html=True)

# ── Tab 2: YouTube Video Guides ────────────────────────────────────────────
with tab_yt:
    guide_filter = st.selectbox(
        "Guide type",
        ["walkthrough", "beginners guide", "tips and tricks", "trophy guide", "review"],
        label_visibility="collapsed",
    )

    if yt.is_available():
        with st.spinner(f"Searching YouTube for {game_name} {guide_filter}..."):
            videos = yt.search_game_guides(game_name, guide_filter, max_results=6)

        if videos:
            for i in range(0, len(videos), 2):
                row = videos[i : i + 2]
                v_cols = st.columns(len(row))
                for col, v in zip(v_cols, row):
                    with col:
                        st.markdown(f"""
                        <div class="game-card-new" style="padding:0; margin-bottom:1rem;">
                          <iframe width="100%" height="195"
                            src="{v['embed_url']}?modestbranding=1&rel=0"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen
                            style="border-radius:16px 16px 0 0; display:block;">
                          </iframe>
                          <div class="game-card-body">
                            <p class="game-card-title" title="{v['title']}">{v['title'][:55]}{'...' if len(v['title'])>55 else ''}</p>
                            <p class="game-card-meta">📺 {v['channel']} &nbsp;·&nbsp; 📅 {v['published']}</p>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No videos found. Try a different guide type.")
    else:
        fallback_url = YouTubeClient.get_fallback_url(game_name, guide_filter)
        st.markdown(f"""
        <div style="text-align:center; padding:2rem;">
          <p style="color:#94a3b8; margin-bottom:1rem;">
            No YouTube API key configured — click below to search directly on YouTube.
          </p>
          <a href="{fallback_url}" target="_blank"
             style="background:linear-gradient(135deg,#7c3aed,#06b6d4); color:white;
                    padding:10px 24px; border-radius:8px; text-decoration:none;
                    font-family:Orbitron,monospace; font-size:0.82rem; font-weight:600;">
            ▶ Search on YouTube
          </a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:2rem; padding:1rem; border:1px solid rgba(124,58,237,0.3); border-radius:12px; font-size:0.78rem; color:#94a3b8;">
          <strong style="color:#a78bfa;">Set up YouTube API (free):</strong><br>
          1. Go to console.cloud.google.com<br>
          2. Create a project → Enable "YouTube Data API v3"<br>
          3. Create an API key → Add to .env as YOUTUBE_API_KEY
        </div>
        """, unsafe_allow_html=True)

# ── Tab 3: IGDB Game Info ──────────────────────────────────────────────────
with tab_igdb:
    if igdb.is_available():
        with st.spinner(f"Fetching game info for {game_name}..."):
            info = igdb.get_game_summary(game_name)

        if info:
            col_l, col_r = st.columns([1, 2])

            with col_l:
                if info.get('cover'):
                    st.image(info['cover'], use_container_width=True)
                if info.get('rating'):
                    st.markdown(f'<div style="text-align:center; margin-top:0.5rem;"><span class="rating-badge">⭐ {info["rating"]}/10 IGDB</span></div>', unsafe_allow_html=True)

            with col_r:
                st.markdown(
                    f'<h3 style="font-family:Orbitron,monospace; font-size:1rem; color:#f1f5f9;">{info.get("name","")}</h3>',
                    unsafe_allow_html=True,
                )
                if info.get('genres'):
                    tags = "".join(f'<span class="genre-tag">{g}</span>' for g in info['genres'])
                    st.markdown(tags, unsafe_allow_html=True)

                if info.get('platforms'):
                    st.markdown(
                        f'<p class="game-card-meta" style="margin-top:0.5rem;">🖥️ {" · ".join(info["platforms"][:4])}</p>',
                        unsafe_allow_html=True,
                    )

                if info.get('summary'):
                    st.markdown("**Overview**")
                    st.write(info['summary'])

            if info.get('storyline'):
                st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
                st.markdown("**Storyline**")
                st.write(info['storyline'])

            # IGDB trailer
            trailer_id = igdb.get_trailer_id(game_name)
            if trailer_id:
                st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
                st.markdown("**Official Trailer**")
                components.iframe(
                    f"https://www.youtube.com/embed/{trailer_id}?modestbranding=1&rel=0",
                    height=360,
                )
        else:
            st.info(f"No IGDB data found for \"{game_name}\". Try a more specific name.")
    else:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:#94a3b8;">
          <p style="font-size:0.85rem; margin-bottom:1.5rem;">
            IGDB provides rich game data including storylines, lore, and official trailers.
            It is completely free — just needs a Twitch Developer account.
          </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:1rem; border:1px solid rgba(124,58,237,0.3); border-radius:12px; font-size:0.78rem; color:#94a3b8;">
          <strong style="color:#a78bfa;">Set up IGDB (free):</strong><br>
          1. Go to dev.twitch.tv/console/apps<br>
          2. Create an application → Category: "Website Integration"<br>
          3. Copy Client ID and generate a Client Secret<br>
          4. Add to .env: IGDB_CLIENT_ID and IGDB_CLIENT_SECRET
        </div>
        """, unsafe_allow_html=True)

# ── Tab 4: Community Tips ──────────────────────────────────────────────────
with tab_tips:
    tips_data = load_tips()
    game_key  = game_name.strip().lower()
    game_tips = tips_data.get(game_key, [])

    st.markdown(
        f'<p style="font-family:Orbitron,monospace; font-size:0.85rem; color:#a78bfa; margin-bottom:0.8rem;">'
        f'COMMUNITY TIPS FOR: {game_name.upper()}</p>',
        unsafe_allow_html=True,
    )

    if game_tips:
        for tip in reversed(game_tips[-20:]):
            st.markdown(f"""
            <div class="chat-bubble-ai" style="margin-bottom:0.6rem;">
              <strong style="color:#a78bfa;">{tip.get('author','Anonymous')}</strong>
              <span style="color:#475569; font-size:0.72rem; margin-left:0.5rem;">{tip.get('date','')}</span>
              <p style="margin:0.3rem 0 0; font-size:0.85rem;">{tip.get('tip','')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:#475569;">
          <p style="font-size:0.85rem;">No tips yet — be the first to share one!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
    st.markdown("**Share a tip**")

    author = st.text_input("Your name (optional)", placeholder="Anonymous")
    tip_text = st.text_area("Your tip", placeholder="e.g. Always upgrade your stamina first — it makes every fight easier.")

    if st.button("📤 Submit Tip", type="primary"):
        if tip_text.strip():
            if game_key not in tips_data:
                tips_data[game_key] = []
            tips_data[game_key].append({
                'author': author.strip() or "Anonymous",
                'tip':    tip_text.strip(),
                'date':   datetime.now().strftime("%Y-%m-%d"),
            })
            save_tips(tips_data)
            st.success("Tip submitted! Thanks.")
            st.rerun()
        else:
            st.warning("Write something before submitting.")
