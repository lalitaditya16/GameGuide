import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from rawg_client import RAWGClient  # ✅ fixed import syntax
from helpers import init_session_state, load_custom_css, validate_environment, get_chat_manager
from steam_client import SteamClient
import requests

# Initialize Steam client
steam_client = SteamClient()

# Load environment variables
load_dotenv()

today = datetime.now().strftime("%B %d, %Y")

# Page configuration
st.set_page_config(
    page_title="🎮 GameGuide",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/rawg-streamlit-app',
        'Report a bug': 'https://github.com/yourusername/rawg-streamlit-app/issues',
        'About': """
        # GAMEGUIDE powered by RAWG

        **Version**: 1.0.0 (with Groq AI integration)

        **Description**: A comprehensive web application for exploring video games with AI-powered features.

        **Features**:
        - 🎮 Browse 500,000+ games
        - 🏢 Explore developers and publishers
        - 📊 Interactive analytics and charts
        - 🔍 Advanced search functionality
        - ❤️ Favorites management
        - 🤖 AI-powered gaming assistant (NEW!)
        """
    }
)

# Initialize session state
init_session_state()

# Load custom CSS
load_custom_css()

# Validate environment
validate_environment()

# Initialize RAWG client
@st.cache_resource
def init_rawg_client():
    """Initialize and cache the RAWG API client."""
    api_key = os.getenv('RAWG_API_KEY')
    if not api_key:
        st.error("⚠️ RAWG API key not found! Please set your API key in the .env file.")
        st.info("Get your free API key from: https://rawg.io/apidocs")
        st.stop()
    return RAWGClient(api_key)

rawg_client = init_rawg_client()


def display_steam_games(title, free_only):
    """Helper to display Steam's most played games."""
    st.subheader(title)
    games = steam_client.get_most_played_games(limit=6, free_only=free_only)

    if games:
        for game in games:
            name = game.get("name", "Unknown Game")
            current_players = game.get("current_players")
            peak_players = game.get("peak_players")
            appid = game.get("appid")
            image = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg" if appid else None

            st.markdown(f"### 🎮 {name}")
            st.write(f"👥 Current Players: {current_players:,}" if current_players else "👥 Current Players: N/A")
            st.write(f"📈 Peak Players: {peak_players:,}" if peak_players else "📈 Peak Players: N/A")
            if image:
                st.image(image, width=600)
            st.markdown("---")
    else:
        st.info("No games found.")


def main():
    """Main application function."""

    # Sidebar branding
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='font-size: 2.5rem; margin: 0;'>🎮</h1>
            <h2 style='color: #FF6B6B; margin: 0;'>RAWG Explorer</h2>
            <p style='color: #666; font-size: 0.9rem;'>Gaming Database</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # AI Status indicator
        chat_manager = get_chat_manager()
        if chat_manager.is_available():
            st.success("🤖 AI Assistant: Online")
            st.markdown("*Powered by Groq + Gemma2-9B*")
        else:
            st.warning("🤖 AI Assistant: Offline")
            st.markdown("*Add GROQ_API_KEY to enable*")

    # Main header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #FF6B6B; font-size: 3rem; margin: 0;'>🎮 GAMEGUIDE</h1>
        <p style='font-size: 1.2rem; color: #666;'>Discover, explore, and analyze the world's largest video game database</p>
        <p style='font-size: 1rem; color: #888;'>✨ Now with AI-powered gaming assistant using Groq + Gemma2-9B and the RAWG database</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Show Steam games sections
    try:
        display_steam_games("🔥 Most Played Free Games on Steam", free_only=True)
        display_steam_games("💰 Most Played Paid Games on Steam", free_only=False)
    except Exception as e:
        st.error("Error loading Steam's most played games:")
        st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #666;'>
        <p>Built with ❤️ using <a href='https://streamlit.io'>Streamlit</a>, <a href='https://rawg.io'>RAWG.io API</a>, and <a href='https://groq.com'>Groq AI</a></p>
        <p>© 2025 RAWG Gaming Database Explorer. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
