
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
    /* Main styling */
    .main > div {
        padding-top: 2rem;
    }

    /* Game card styling */
    .game-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .game-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* Header styling */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    /* AI Chat styling */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }

    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }

    .ai-message {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        color: #333;
    }

    .chat-input {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #e9ecef;
    }

    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* Feature card styling */
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        color: white;
        cursor: pointer;
        transition: transform 0.2s ease;
    }

    .feature-card:hover {
        transform: scale(1.05);
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #5a6fd8;
    }

    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }

    /* Error message styling */
    .error-message {
        background: #ffebee;
        border: 1px solid #f44336;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #c62828;
    }

    /* Success message styling */
    .success-message {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2e7d32;
    }

    /* Info message styling */
    .info-message {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1565c0;
    }
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
