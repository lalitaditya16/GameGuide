
"""
Configuration settings for the RAWG Streamlit Application
=========================================================

This module contains all configuration constants, API settings, and 
application parameters used throughout the application.
"""

import os
from typing import Dict, List, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class AppConfig(BaseSettings):
    """Application configuration using Pydantic BaseSettings and Streamlit secrets support."""

    # RAWG API configuration
    rawg_api_key: str = Field(default_factory=lambda: st.secrets.get("RAWG_API_KEY", ""))
    base_url: str = "https://api.rawg.io/api"  # renamed from rawg_base_url
    user_agent: str = "RAWG-Streamlit-Explorer/1.0"

    # Groq API configuration
    groq_api_key: str = Field(default_factory=lambda: st.secrets.get("GROQ_API_KEY", ""))
    groq_model: str = "gemma2-9b-it"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 1024

    # API request settings
    api_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 40

    # Streamlit cache settings
    cache_ttl: int = 3600  # 1 hour
    max_cache_size: int = 100
    enable_caching: bool = True

    # UI settings
    items_per_row: int = 3
    image_width: int = 300
    image_height: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instantiate configuration
config = AppConfig()

# RAWG API Endpoints
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
    'platform_detail': '/platforms/{id}',
    'genres': '/genres',
    'genre_detail': '/genres/{id}',
    'tags': '/tags',
    'tag_detail': '/tags/{id}',
    'creators': '/creators',
    'creator_detail': '/creators/{id}',
    'creator_roles': '/creator-roles',
    'stores': '/stores',
    'store_detail': '/stores/{id}'
}

# Supported ordering options for games
GAME_ORDERING_OPTIONS = {
    'Name (A-Z)': 'name',
    'Name (Z-A)': '-name',
    'Release Date (Newest)': '-released',
    'Release Date (Oldest)': 'released',
    'Rating (Highest)': '-rating',
    'Rating (Lowest)': 'rating',
    'Metacritic Score (Highest)': '-metacritic',
    'Metacritic Score (Lowest)': 'metacritic',
    'Most Popular': '-added',
    'Least Popular': 'added',
    'Recently Updated': '-updated',
    'Least Recently Updated': 'updated'
}

# Default genres for filtering
DEFAULT_GENRES = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Shooter', 'Puzzle',
    'Racing', 'Sports', 'Simulation', 'Platformer', 'Fighting',
    'Horror', 'Survival', 'MMORPG', 'Battle Royale'
]

# Default platforms
DEFAULT_PLATFORMS = {
    'PC': [4],
    'PlayStation': [1, 2, 3, 16, 18, 19, 167, 187],
    'Xbox': [14, 80, 186],
    'Nintendo': [7, 8, 9, 13, 83, 24, 26],
    'Mobile': [21, 3],
    'Mac': [5],
    'Linux': [6]
}

# Date ranges for filtering
DATE_RANGES = {
    'All Time': None,
    'This Year': f'{2025}-01-01,{2025}-12-31',
    'Last Year': f'{2024}-01-01,{2024}-12-31',
    'Last 5 Years': f'{2020}-01-01,{2025}-12-31',
    'Last 10 Years': f'{2015}-01-01,{2025}-12-31',
    '2020s': '2020-01-01,2029-12-31',
    '2010s': '2010-01-01,2019-12-31',
    '2000s': '2000-01-01,2009-12-31',
    '1990s': '1990-01-01,1999-12-31',
    '1980s': '1980-01-01,1989-12-31'
}

# AI Prompts for Groq Integration
AI_PROMPTS = {
    'system_prompt': """You are an expert gaming assistant with deep knowledge of video games, gaming industry, trends, and player preferences. You help users discover games, understand gaming concepts, and provide gaming recommendations.

Key capabilities:
- Game recommendations based on preferences
- Gaming industry insights and trends
- Platform and genre explanations
- Game analysis and reviews
- Gaming culture and community insights

Always be helpful, enthusiastic about gaming, and provide accurate information. If you're unsure about something, say so rather than making up facts.
""",

    'game_analysis': """Analyze this game data and provide insights about:
1. Game quality and player reception
2. Notable features or mechanics
3. Target audience
4. Comparison to similar games
5. Recommendation verdict

Game data: {game_data}
""",

    'recommendation': """Based on the user's preferences, recommend games that would be a good fit:

User preferences: {preferences}
Available games: {games_data}

Provide 3-5 specific game recommendations with reasons why each game matches their preferences.
""",

    'trend_analysis': """Analyze the gaming trends from this data:
{trend_data}

Provide insights about:
1. Popular genres
2. Platform trends
3. Release patterns
4. Rating distributions
5. Emerging trends
"""
}

# Session state keys
SESSION_KEYS = {
    'favorites': 'user_favorites',
    'search_history': 'search_history',
    'current_page': 'current_page',
    'filters': 'active_filters',
    'user_preferences': 'user_preferences',
    'chat_history': 'chat_history',
    'ai_context': 'ai_context'
}

# CSS Styles
CUSTOM_CSS = """
<style>
    :root {
        --bg: #0f1223;
        --panel: #151936;
        --panel-2: #1b214a;
        --text: #e9ecff;
        --muted: #a3abda;
        --brand-1: #6a7cff;
        --brand-2: #a66bff;
        --accent-1: #f5576c;
        --accent-2: #4facfe;
        --success: #30d158;
        --warning: #ffd166;
        --danger: #ff6b6b;
        --card-shadow: 0 8px 24px rgba(0,0,0,0.35);
        --inner-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }

    html, body, .block-container { background: var(--bg) !important; color: var(--text) !important; }
    .stMarkdown, .stText, .stCaption, p, span, li { color: var(--text) !important; }

    /* Main padding */
    .main > div { padding-top: 1.2rem; }

    /* Hero section */
    .hero {
        position: relative;
        border-radius: var(--radius-lg);
        background: radial-gradient(1200px 600px at 10% -20%, rgba(106,124,255,0.45) 0%, transparent 60%),
                    radial-gradient(1200px 600px at 90% 120%, rgba(166,107,255,0.35) 0%, transparent 60%),
                    linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
        padding: 2.25rem 2rem;
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(255,255,255,0.06);
    }
    .hero h1 {
        margin: 0 0 .25rem 0;
        font-size: 2.25rem;
        letter-spacing: 0.3px;
        background: linear-gradient(90deg, var(--brand-1), var(--brand-2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .hero p { margin: 0.25rem 0 0 0; color: var(--muted) !important; }

    /* Section title */
    .section-title {
        display: flex; align-items: center; gap: .6rem;
        font-weight: 700; color: var(--text);
        margin: .25rem 0 1rem 0;
    }
    .section-title .dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(90deg, var(--brand-1), var(--brand-2)); box-shadow: 0 0 20px rgba(106,124,255,.7); }

    /* Grid cards */
    .grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 16px; width: 100%;
    }
    .game-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.00) 100%), var(--panel);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--card-shadow);
        transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    }
    .game-card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.14); box-shadow: 0 16px 36px rgba(0,0,0,0.45); }

    .card-image { position: relative; height: 150px; background: #0b0e20; overflow: hidden; }
    .card-image img { width: 100%; height: 100%; object-fit: cover; filter: saturate(105%); }
    .card-overlay { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,12,30,0.0) 0%, rgba(10,12,30,0.6) 100%); }

    .rating-badge {
        position: absolute; top: 10px; right: 10px;
        background: linear-gradient(135deg, rgba(0,0,0,0.55), rgba(0,0,0,0.15));
        border: 1px solid rgba(255,255,255,0.12);
        color: #fff; padding: 4px 8px; font-weight: 700; font-size: .85rem; border-radius: 999px; backdrop-filter: blur(6px);
    }

    .card-body { padding: 12px 12px 14px 12px; }
    .card-title { margin: 0 0 6px 0; font-weight: 700; font-size: 1.0rem; color: var(--text); }
    .meta { display: flex; flex-wrap: wrap; gap: 6px; }

    .tag {
        font-size: .72rem; padding: 4px 8px; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.10);
        background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        color: var(--muted);
    }

    .btn-primary {
        display: inline-flex; align-items: center; justify-content: center; gap: .5rem;
        width: 100%; border: none; border-radius: var(--radius-sm);
        padding: 10px 12px; color: #fff; font-weight: 700; cursor: pointer;
        background: linear-gradient(90deg, var(--brand-1), var(--brand-2));
        box-shadow: 0 10px 24px rgba(106,124,255,0.35);
        transition: transform .15s ease, box-shadow .15s ease, opacity .15s ease;
    }
    .btn-primary:hover { transform: translateY(-1px); opacity: .95; box-shadow: 0 16px 36px rgba(106,124,255,0.5); }

    /* Sidebar tweaks */
    .sidebar .sidebar-content { background: var(--panel-2) !important; }

    /* Chat bubbles */
    .chat-message { padding: 1rem; margin: 0.5rem 0; border-radius: 12px; max-width: 85%; }
    .user-message { background: linear-gradient(90deg, var(--brand-1), var(--brand-2)); color: white; margin-left: auto; }
    .ai-message { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: var(--text); }

    /* Buttons */
    .stButton > button {
        width: 100%; border-radius: 10px; border: none; padding: .65rem 1rem;
        background: linear-gradient(90deg, var(--brand-1), var(--brand-2)); color: #fff;
        transition: transform .15s ease, box-shadow .15s ease;
        box-shadow: 0 10px 24px rgba(106,124,255,.35);
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 16px 36px rgba(106,124,255,.5); }

    /* Hide default chrome */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #0b0e20; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #2a315f; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #39438a; }
</style>
"""

# Error messages
ERROR_MESSAGES = {
    'api_key_missing': "⚠️ RAWG API key not found! Please set your API key in the .env file.",
    'groq_key_missing': "⚠️ Groq API key not found! Please set your API key in the .env file.",
    'api_request_failed': "❌ Failed to fetch data from RAWG API. Please try again later.",
    'ai_request_failed': "❌ Failed to get AI response. Please try again later.",
    'no_results_found': "🔍 No results found for your search criteria.",
    'invalid_game_id': "❌ Invalid game ID provided.",
    'network_error': "🌐 Network error occurred. Please check your internet connection.",
    'rate_limit_exceeded': "⏰ Rate limit exceeded. Please wait a moment before making another request.",
    'ai_not_available': "🤖 AI features are currently unavailable. Please check your Groq API key."
}

# Success messages
SUCCESS_MESSAGES = {
    'game_added_to_favorites': "❤️ Game added to favorites!",
    'game_removed_from_favorites': "💔 Game removed from favorites.",
    'search_completed': "✅ Search completed successfully!",
    'data_cached': "⚡ Data cached for faster loading.",
    'ai_response_generated': "🤖 AI response generated successfully!",
    'chat_exported': "📁 Chat history exported successfully!"
}

# Image placeholders
PLACEHOLDER_IMAGES = {
    'game': 'https://via.placeholder.com/300x200/667eea/white?text=Game+Image',
    'developer': 'https://via.placeholder.com/150x150/764ba2/white?text=Developer',
    'platform': 'https://via.placeholder.com/100x100/f093fb/white?text=Platform',
    'genre': 'https://via.placeholder.com/200x150/4facfe/white?text=Genre'
}

# Analytics configuration
ANALYTICS_CONFIG = {
    'chart_height': 400,
    'chart_colors': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
    'default_chart_type': 'bar',
    'enable_animations': True
}

# Export all configurations
__all__ = [
    'config',
    'API_ENDPOINTS',
    'GAME_ORDERING_OPTIONS',
    'DEFAULT_GENRES',
    'DEFAULT_PLATFORMS',
    'DATE_RANGES',
    'AI_PROMPTS',
    'SESSION_KEYS',
    'CUSTOM_CSS',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'PLACEHOLDER_IMAGES',
    'ANALYTICS_CONFIG'
]
