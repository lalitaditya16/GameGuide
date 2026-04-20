import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from datetime import datetime
from rawg_client import RAWGClient
from helpers import init_session_state, load_custom_css, validate_environment, get_chat_manager, render_theme_toggle
from steam_client import SteamClient

load_dotenv()
steam_client = SteamClient()

st.set_page_config(
    page_title="GameGuide",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_bar="expanded",
    menu_items={
        'Get Help': 'https://github.com/lalitaditya16/GameGuide',
        'Report a bug': 'https://github.com/lalitaditya16/GameGuide/issues',
        'About': "# GameGuide\nYour complete gaming companion powered by RAWG, Steam, and Groq AI.",
    }
)

init_session_state()
load_custom_css()
validate_environment()


@st.cache_resource
def init_rawg_client():
    api_key = os.getenv('RAWG_API_KEY')
    if not api_key:
        st.error("RAWG API key not found. Add it to your .env file.")
        st.stop()
    return RAWGClient(api_key)


rawg_client = init_rawg_client()


def safe_fmt(value):
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return "N/A"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    render_theme_toggle()
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding: 0.5rem 0 1rem;'>
        <div style='font-size:2.8rem;'>🎮</div>
        <div style='font-family:Orbitron,monospace; font-size:1.1rem; font-weight:700;
                    background:linear-gradient(135deg,#7c3aed,#06b6d4);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text;'>
            GAMEGUIDE
        </div>
        <div style='color:#64748b; font-size:0.75rem; margin-top:2px;'>Your Gaming Companion</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    chat_manager = get_chat_manager()
    if chat_manager.is_available():
        st.success("🤖 AI Online — llama-3.3-70b")
    else:
        st.warning("🤖 AI Offline — add GROQ_API_KEY")


# ---------------------------------------------------------------------------
# Particle animation canvas (background)
# ---------------------------------------------------------------------------
PARTICLE_HTML = """
<style>
  body { margin:0; background:transparent; overflow:hidden; }
  canvas { display:block; width:100%; }
</style>
<canvas id="pc"></canvas>
<script>
  const c   = document.getElementById('pc');
  const ctx = c.getContext('2d');
  function resize() { c.width = window.innerWidth; c.height = 220; }
  resize();
  window.addEventListener('resize', resize);

  const colors = ['#7c3aed','#06b6d4','#ec4899','#a78bfa','#67e8f9'];
  const particles = Array.from({length: 90}, () => mkP());

  function mkP() {
    return {
      x: Math.random() * c.width,
      y: Math.random() * c.height,
      size: Math.random() * 2.2 + 0.4,
      vx: (Math.random() - 0.5) * 0.35,
      vy: -Math.random() * 0.55 - 0.08,
      opacity: Math.random() * 0.65 + 0.15,
      color: colors[Math.floor(Math.random() * colors.length)],
    };
  }

  function resetP(p) {
    p.x = Math.random() * c.width;
    p.y = c.height + 4;
    p.opacity = Math.random() * 0.65 + 0.15;
  }

  function draw() {
    ctx.clearRect(0, 0, c.width, c.height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy; p.opacity -= 0.0007;
      if (p.y < -4 || p.opacity <= 0) resetP(p);
      ctx.save();
      ctx.globalAlpha = p.opacity;
      ctx.shadowBlur  = 7;
      ctx.shadowColor = p.color;
      ctx.fillStyle   = p.color;
      ctx.fillRect(p.x, p.y, p.size, p.size);
      ctx.restore();
    });
    requestAnimationFrame(draw);
  }
  draw();
</script>
"""


# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
components.html(PARTICLE_HTML, height=220)

st.markdown("""
<div class="hero-section">
  <p class="glow-title">GAMEGUIDE</p>
  <p class="hero-sub">
    Discover, track, and explore 500,000+ games &nbsp;·&nbsp;
    AI-powered guides &nbsp;·&nbsp; MAL-style lists
  </p>
  <div style="margin-top:1.2rem; display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
    <span class="rating-badge" style="font-size:0.78rem; padding:4px 14px;">🎮 RAWG Database</span>
    <span class="rating-badge" style="font-size:0.78rem; padding:4px 14px; background:linear-gradient(135deg,#06b6d4,#10b981);">⚡ Groq AI</span>
    <span class="rating-badge" style="font-size:0.78rem; padding:4px 14px; background:linear-gradient(135deg,#ec4899,#7c3aed);">🎯 Steam Live Data</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Stats row
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("🎮 Games", "500,000+", "Growing daily")
c2.metric("📸 Screenshots", "2.1M+", "HD quality")
c3.metric("🏢 Developers", "220,000+", "Worldwide")
c4.metric("⚡ AI Speed", "2,000+ tok/s", "Streaming")

st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Feature cards
# ---------------------------------------------------------------------------
st.markdown(
    '<h2 style="font-family:Orbitron,monospace; font-size:1.1rem; color:#a78bfa; margin-bottom:1rem;">EXPLORE</h2>',
    unsafe_allow_html=True,
)

fc1, fc2, fc3, fc4, fc5 = st.columns(5)
features = [
    ("🎮", "Browse Games", "500K+ games with filters, sorting & MAL-style status tracking"),
    ("🤖", "AI Assistant", "Streaming chat with llama-3.3-70b — fast, smart, context-aware"),
    ("📖", "Game Guides", "AI walkthroughs + YouTube video guides for any game"),
    ("📊", "Analytics", "Trends, charts, and insights across the gaming world"),
    ("🔍", "Advanced Search", "Filter by genre, platform, year, Metacritic score and more"),
]
for col, (icon, title, desc) in zip([fc1, fc2, fc3, fc4, fc5], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
          <span class="feature-icon">{icon}</span>
          <p class="feature-title">{title}</p>
          <p class="feature-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Trending games carousel (top-rated from RAWG)
# ---------------------------------------------------------------------------
st.markdown(
    '<h2 style="font-family:Orbitron,monospace; font-size:1.1rem; color:#a78bfa; margin-bottom:0.8rem;">🔥 TRENDING NOW</h2>',
    unsafe_allow_html=True,
)

try:
    @st.cache_data(ttl=3600)
    def fetch_trending():
        return rawg_client.get_games(ordering="-added", page_size=18)

    trending = fetch_trending()

    if trending:
        cards_html = ""
        for game in trending:
            img   = game.get('background_image') or 'https://via.placeholder.com/190x110/0d0f1a/7c3aed?text=No+Image'
            name  = game.get('name', 'Unknown')[:28]
            rating = game.get('rating', 0)
            stars  = "⭐" * round(rating) if rating else "—"
            cards_html += f"""
            <div class="carousel-item">
              <img src="{img}" alt="{name}" loading="lazy">
              <div class="carousel-item-body">
                <p class="carousel-item-title">{name}</p>
                <span class="carousel-item-rating">{stars} {rating}/5</span>
              </div>
            </div>
            """
        st.markdown(
            f'<div class="carousel-wrap">{cards_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Could not load trending games right now.")
except Exception:
    st.info("Trending games unavailable.")

st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Most played on Steam
# ---------------------------------------------------------------------------
st.markdown(
    '<h2 style="font-family:Orbitron,monospace; font-size:1.1rem; color:#a78bfa; margin-bottom:0.8rem;">🎯 MOST PLAYED ON STEAM</h2>',
    unsafe_allow_html=True,
)

try:
    col_free, col_paid = st.columns(2)

    with col_free:
        st.markdown(
            '<p style="font-family:Orbitron,monospace; font-size:0.82rem; color:#34d399; margin-bottom:0.8rem;">🆓 FREE TO PLAY</p>',
            unsafe_allow_html=True,
        )
        free_games = steam_client.get_most_played_games(limit=5, free_only=True)
        if free_games:
            for game in free_games:
                appid = game.get("appid")
                st.markdown(f"""
                <div class="game-card-new" style="margin-bottom:0.8rem;">
                  <img class="game-card-img"
                       src="https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
                       onerror="this.src='https://via.placeholder.com/300x175/0d0f1a/7c3aed?text=Steam'"
                       loading="lazy">
                  <div class="game-card-body">
                    <p class="game-card-title">{game.get('name','Unknown')}</p>
                    <p class="game-card-meta">👥 {safe_fmt(game.get('current_players'))} playing &nbsp;·&nbsp; 📈 Peak {safe_fmt(game.get('peak_players'))}</p>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No free games found.")

    with col_paid:
        st.markdown(
            '<p style="font-family:Orbitron,monospace; font-size:0.82rem; color:#a78bfa; margin-bottom:0.8rem;">💎 PREMIUM</p>',
            unsafe_allow_html=True,
        )
        paid_games = steam_client.get_most_played_games(limit=5, free_only=False)
        if paid_games:
            for game in paid_games:
                appid = game.get("appid")
                st.markdown(f"""
                <div class="game-card-new" style="margin-bottom:0.8rem;">
                  <img class="game-card-img"
                       src="https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
                       onerror="this.src='https://via.placeholder.com/300x175/0d0f1a/7c3aed?text=Steam'"
                       loading="lazy">
                  <div class="game-card-body">
                    <p class="game-card-title">{game.get('name','Unknown')}</p>
                    <p class="game-card-meta">👥 {safe_fmt(game.get('current_players'))} playing &nbsp;·&nbsp; 📈 Peak {safe_fmt(game.get('peak_players'))}</p>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No paid games found.")

except Exception as e:
    st.error(f"Could not load Steam data: {e}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#475569; font-size:0.78rem; padding:1rem 0 2rem;'>
  Built with Streamlit &nbsp;·&nbsp; RAWG.io &nbsp;·&nbsp; Steam &nbsp;·&nbsp; Groq AI (llama-3.3-70b-versatile)<br>
  <span style='color:#7c3aed;'>GAMEGUIDE</span> &nbsp;©&nbsp; 2025
</div>
""", unsafe_allow_html=True)
