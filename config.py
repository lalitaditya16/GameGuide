"""
GameGuide — Configuration
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class AppConfig(BaseSettings):
    # RAWG API
    rawg_api_key: str = Field(default_factory=lambda: os.getenv("RAWG_API_KEY", ""))
    base_url: str = "https://api.rawg.io/api"
    user_agent: str = "GameGuide/2.0"

    # Groq API — llama-3.3-70b-versatile for smarter + faster responses
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fast_model: str = "llama-3.1-8b-instant"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1024

    # IGDB API — free via Twitch Developer account
    igdb_client_id: str = Field(default_factory=lambda: os.getenv("IGDB_CLIENT_ID", ""))
    igdb_client_secret: str = Field(default_factory=lambda: os.getenv("IGDB_CLIENT_SECRET", ""))

    # YouTube Data API v3 — free, 10 000 quota units/day
    youtube_api_key: str = Field(default_factory=lambda: os.getenv("YOUTUBE_API_KEY", ""))

    # Steam API
    steam_api_key: str = Field(default_factory=lambda: os.getenv("STEAM_API_KEY", ""))

    # API settings
    api_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 40

    # Cache
    cache_ttl: int = 3600
    enable_caching: bool = True

    # UI
    items_per_row: int = 3
    image_width: int = 300
    image_height: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


config = AppConfig()

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
API_ENDPOINTS = {
    'games': '/games',
    'game_detail': '/games/{id}',
    'game_screenshots': '/games/{id}/screenshots',
    'game_movies': '/games/{id}/movies',
    'game_achievements': '/games/{id}/achievements',
    'game_reddit': '/games/{id}/reddit',
    'game_stores': '/games/{id}/stores',
    'game_series': '/games/{id}/game-series',
    'game_additions': '/games/{id}/additions',
    'game_parent_games': '/games/{id}/parent-games',
    'game_development_team': '/games/{id}/development-team',
    'developers': '/developers',
    'developer_detail': '/developers/{id}',
    'publishers': '/publishers',
    'publisher_detail': '/publishers/{id}',
    'platforms': '/platforms',
    'genres': '/genres',
    'tags': '/tags',
    'creators': '/creators',
    'stores': '/stores',
}

GAME_ORDERING_OPTIONS = {
    'Name (A-Z)': 'name',
    'Name (Z-A)': '-name',
    'Release Date (Newest)': '-released',
    'Release Date (Oldest)': 'released',
    'Rating (Highest)': '-rating',
    'Rating (Lowest)': 'rating',
    'Metacritic Score (Highest)': '-metacritic',
    'Most Popular': '-added',
    'Recently Updated': '-updated',
}

DEFAULT_GENRES = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Shooter', 'Puzzle',
    'Racing', 'Sports', 'Simulation', 'Platformer', 'Fighting',
    'Horror', 'Survival', 'MMORPG', 'Battle Royale',
]

DEFAULT_PLATFORMS = {
    'PC': [4],
    'PlayStation': [1, 2, 3, 16, 18, 19, 167, 187],
    'Xbox': [14, 80, 186],
    'Nintendo': [7, 8, 9, 13, 83, 24, 26],
    'Mobile': [21, 3],
    'Mac': [5],
    'Linux': [6],
}

DATE_RANGES = {
    'All Time': None,
    'This Year': '2025-01-01,2025-12-31',
    'Last Year': '2024-01-01,2024-12-31',
    'Last 5 Years': '2020-01-01,2025-12-31',
    'Last 10 Years': '2015-01-01,2025-12-31',
    '2020s': '2020-01-01,2029-12-31',
    '2010s': '2010-01-01,2019-12-31',
    '2000s': '2000-01-01,2009-12-31',
    '1990s': '1990-01-01,1999-12-31',
}

AI_PROMPTS = {
    'system_prompt': (
        "You are GameGuide AI — a sharp, enthusiastic gaming expert who knows everything "
        "about video games, industry trends, strategies, and lore. "
        "You give concise, accurate, and helpful answers. "
        "If you don't know something, say so rather than guessing. "
        "Today is {today}."
    ),

    'game_analysis': (
        "Analyze this game and give a structured breakdown:\n"
        "1. What makes it stand out\n2. Who it is for\n3. Strengths and weaknesses\n"
        "4. Score verdict /10\n\nGame data: {game_data}"
    ),

    'game_guide': (
        "Write a structured beginner guide for \"{game_name}\":\n\n"
        "## Quick Start\n- What to do in the first 30 minutes\n\n"
        "## Core Mechanics\n- Key systems to understand\n\n"
        "## Pro Tips\n- 3-5 things that make the biggest difference\n\n"
        "## Common Mistakes\n- What beginners usually get wrong\n\n"
        "## Achievement/Trophy Tips\n- Easiest ones to grab early\n\n"
        "Keep it practical and concise."
    ),

    'recommendation': (
        "Based on these preferences, recommend 4-5 games with reasons:\n\n"
        "User preferences: {preferences}\nAvailable games: {games_data}\n\n"
        "For each: why it fits, estimated playtime, difficulty level."
    ),

    'trend_analysis': (
        "Analyze these gaming trends:\n{trend_data}\n\n"
        "Cover: popular genres, platform trends, rating patterns, what is emerging."
    ),
}

SESSION_KEYS = {
    'favorites': 'user_favorites',
    'search_history': 'search_history',
    'current_page': 'current_page',
    'filters': 'active_filters',
    'user_preferences': 'user_preferences',
    'chat_history': 'chat_history',
    'ai_context': 'ai_context',
    'game_status': 'game_status_list',
}

# MAL-style game status options
GAME_STATUS_OPTIONS = {
    'Playing': {'color': '#10b981', 'icon': '🎮'},
    'Completed': {'color': '#06b6d4', 'icon': '✅'},
    'Want to Play': {'color': '#7c3aed', 'icon': '📌'},
    'On Hold': {'color': '#f59e0b', 'icon': '⏸️'},
    'Dropped': {'color': '#ec4899', 'icon': '❌'},
}

# ---------------------------------------------------------------------------
# Gaming design system — dark-first, neon accents, Orbitron headers
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── Core ── */
[data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0f1a 0%, #0a0a0f 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.22) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 0.04em !important;
}

/* ── Glow title ── */
.glow-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 16px rgba(124,58,237,0.5));
    animation: titlePulse 4s ease-in-out infinite alternate;
    line-height: 1.25;
    margin: 0;
}
@keyframes titlePulse {
    from { filter: drop-shadow(0 0 10px rgba(124,58,237,0.4)); }
    to   { filter: drop-shadow(0 0 28px rgba(6,182,212,0.7)); }
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    color: #94a3b8;
    font-size: 1.05rem;
    margin-top: 0.6rem;
}

/* ── Hero section ── */
.hero-section {
    background: linear-gradient(135deg,
        rgba(124,58,237,0.10) 0%,
        rgba(6,182,212,0.07) 50%,
        rgba(236,72,153,0.07) 100%);
    border: 1px solid rgba(124,58,237,0.28);
    border-radius: 22px;
    padding: 2.8rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: radial-gradient(circle at center, rgba(124,58,237,0.06) 0%, transparent 60%);
    animation: heroSpin 22s linear infinite;
    pointer-events: none;
}
@keyframes heroSpin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

/* ── Game cards ── */
.game-card-new {
    background: linear-gradient(135deg, rgba(13,15,26,0.97) 0%, rgba(18,20,34,0.97) 100%);
    border: 1px solid rgba(124,58,237,0.22);
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    margin-bottom: 1.1rem;
    height: 100%;
}
.game-card-new:hover {
    border-color: rgba(124,58,237,0.72);
    transform: translateY(-4px);
    box-shadow: 0 0 28px rgba(124,58,237,0.22), 0 18px 36px rgba(0,0,0,0.45);
}
.game-card-img  { width: 100%; height: 175px; object-fit: cover; display: block; }
.game-card-body { padding: 0.8rem 0.9rem 0.9rem; }
.game-card-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 0.45rem 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.game-card-meta { font-size: 0.72rem; color: #94a3b8; margin: 0.2rem 0; }

/* ── Carousel ── */
.carousel-wrap {
    display: flex;
    overflow-x: auto;
    gap: 14px;
    padding: 6px 2px 14px;
    scrollbar-width: thin;
    scrollbar-color: rgba(124,58,237,0.45) transparent;
}
.carousel-wrap::-webkit-scrollbar { height: 4px; }
.carousel-wrap::-webkit-scrollbar-track { background: transparent; }
.carousel-wrap::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.45); border-radius: 2px; }
.carousel-item {
    flex: 0 0 190px;
    background: rgba(13,15,26,0.97);
    border: 1px solid rgba(124,58,237,0.22);
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.25s ease;
}
.carousel-item:hover {
    border-color: rgba(124,58,237,0.7);
    transform: translateY(-3px);
    box-shadow: 0 0 20px rgba(124,58,237,0.2);
}
.carousel-item img   { width: 100%; height: 110px; object-fit: cover; display: block; }
.carousel-item-body  { padding: 0.55rem 0.65rem; }
.carousel-item-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    color: #f1f5f9;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0 0 0.25rem;
}
.carousel-item-rating { font-size: 0.68rem; color: #a78bfa; }

/* ── Badges & tags ── */
.rating-badge {
    display: inline-block;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    color: white;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.genre-tag {
    display: inline-block;
    background: rgba(124,58,237,0.16);
    color: #a78bfa;
    border: 1px solid rgba(124,58,237,0.32);
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.66rem;
    margin: 2px 2px 0 0;
}
.status-playing   { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:600; background:rgba(16,185,129,0.16); color:#34d399; border:1px solid rgba(16,185,129,0.38); }
.status-completed { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:600; background:rgba(6,182,212,0.16);  color:#67e8f9; border:1px solid rgba(6,182,212,0.38); }
.status-want      { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:600; background:rgba(124,58,237,0.16); color:#a78bfa; border:1px solid rgba(124,58,237,0.38); }
.status-hold      { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:600; background:rgba(245,158,11,0.16); color:#fbbf24; border:1px solid rgba(245,158,11,0.38); }
.status-dropped   { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:600; background:rgba(236,72,153,0.16); color:#f472b6; border:1px solid rgba(236,72,153,0.38); }

/* ── Feature cards ── */
.feature-card {
    background: linear-gradient(135deg, rgba(13,15,26,0.96) 0%, rgba(20,22,38,0.96) 100%);
    border: 1px solid rgba(124,58,237,0.22);
    border-radius: 16px;
    padding: 1.5rem 1.1rem;
    text-align: center;
    transition: all 0.28s ease;
    height: 100%;
}
.feature-card:hover {
    border-color: rgba(124,58,237,0.68);
    transform: translateY(-5px);
    box-shadow: 0 0 22px rgba(124,58,237,0.18), 0 14px 32px rgba(0,0,0,0.38);
}
.feature-icon  { font-size: 2.2rem; animation: floatIcon 3.2s ease-in-out infinite; display: block; margin-bottom: 0.5rem; }
.feature-title { font-family: 'Orbitron', monospace; font-size: 0.82rem; font-weight: 700; color: #f1f5f9; margin: 0 0 0.3rem; }
.feature-desc  { font-size: 0.75rem; color: #94a3b8; line-height: 1.45; margin: 0; }
@keyframes floatIcon {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-7px); }
}

/* ── Neon divider ── */
.neon-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.55), rgba(6,182,212,0.55), transparent);
    margin: 1.8rem 0;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 14px rgba(124,58,237,0.28) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    box-shadow: 0 0 26px rgba(124,58,237,0.55) !important;
    transform: translateY(-2px) !important;
}

/* ── Chat bubbles ── */
.chat-bubble-user {
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.4rem 0 0.4rem auto;
    max-width: 76%;
    font-size: 0.88rem;
    line-height: 1.5;
}
.chat-bubble-ai {
    background: rgba(13,15,26,0.96);
    border: 1px solid rgba(124,58,237,0.28);
    color: #f1f5f9;
    padding: 0.75rem 1rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.4rem auto 0.4rem 0;
    max-width: 84%;
    font-size: 0.88rem;
    line-height: 1.55;
}

/* ── Quick action chips ── */
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1rem; }
.quick-chip {
    display: inline-block;
    background: rgba(124,58,237,0.13);
    border: 1px solid rgba(124,58,237,0.38);
    color: #a78bfa;
    padding: 5px 13px;
    border-radius: 20px;
    font-size: 0.76rem;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'Inter', sans-serif;
}
.quick-chip:hover {
    background: rgba(124,58,237,0.28);
    border-color: rgba(124,58,237,0.75);
    color: #c4b5fd;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
[data-baseweb="input"] > div {
    background: rgba(13,15,26,0.96) !important;
    border: 1px solid rgba(124,58,237,0.28) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
[data-baseweb="select"] > div {
    background: rgba(13,15,26,0.96) !important;
    border: 1px solid rgba(124,58,237,0.28) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(13,15,26,0.96) !important;
    border: 1px solid rgba(124,58,237,0.22) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    transition: all 0.28s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(124,58,237,0.58) !important;
    box-shadow: 0 0 18px rgba(124,58,237,0.14) !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: rgba(13,15,26,0.96) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(124,58,237,0.18) !important;
    padding: 4px !important;
    gap: 4px !important;
}
[data-baseweb="tab"] { color: #94a3b8 !important; border-radius: 8px !important; }
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(124,58,237,0.22) !important;
    color: #a78bfa !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.42); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.72); }

/* ── Subtle scanline ── */
body::after {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 3px,
        rgba(0,0,0,0.022) 3px, rgba(0,0,0,0.022) 4px
    );
    pointer-events: none;
    z-index: 9998;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""

ERROR_MESSAGES = {
    'api_key_missing': "RAWG API key not found. Add it to your .env file.",
    'groq_key_missing': "Groq API key not found. AI features disabled.",
    'api_request_failed': "Failed to fetch data from RAWG API. Try again later.",
    'ai_request_failed': "Failed to get AI response. Try again later.",
    'no_results_found': "No results found for your search.",
    'invalid_game_id': "Invalid game ID.",
    'network_error': "Network error. Check your connection.",
    'rate_limit_exceeded': "Rate limit hit. Wait a moment.",
    'ai_not_available': "AI is offline. Add your GROQ_API_KEY to enable it.",
}

SUCCESS_MESSAGES = {
    'game_added_to_favorites': "Game added to your list.",
    'game_removed_from_favorites': "Game removed from your list.",
    'search_completed': "Search complete.",
    'ai_response_generated': "AI response ready.",
    'chat_exported': "Chat exported.",
}

PLACEHOLDER_IMAGES = {
    'game': 'https://via.placeholder.com/300x200/0d0f1a/7c3aed?text=No+Image',
    'developer': 'https://via.placeholder.com/150x150/0d0f1a/7c3aed?text=Dev',
}

ANALYTICS_CONFIG = {
    'chart_height': 400,
    'chart_colors': ['#7c3aed', '#06b6d4', '#ec4899', '#10b981', '#f59e0b', '#ef4444'],
    'default_chart_type': 'bar',
    'enable_animations': True,
}

__all__ = [
    'config', 'API_ENDPOINTS', 'GAME_ORDERING_OPTIONS', 'DEFAULT_GENRES',
    'DEFAULT_PLATFORMS', 'DATE_RANGES', 'AI_PROMPTS', 'SESSION_KEYS',
    'GAME_STATUS_OPTIONS', 'CUSTOM_CSS', 'ERROR_MESSAGES', 'SUCCESS_MESSAGES',
    'PLACEHOLDER_IMAGES', 'ANALYTICS_CONFIG',
]
