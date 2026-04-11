import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd 
from dotenv import load_dotenv
from datetime import datetime, timedelta
from rawg_client import RAWGClient
from helpers import init_session_state, load_custom_css, validate_environment, get_chat_manager
from steam_client import SteamClient
import requests

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
        'Get Help': 'https://github.com/lalitaditya16/gameguide-streamlit-app',
        'Report a bug': 'https://github.com/lalitaditya16/gameguide-streamlit-app/issues',
        'About': """
        # GAMEGUIDE powered by RAWG and STEAM
        **Description**: A comprehensive web application for exploring video games with AI-powered features.
        - 🎮 Browse  around 500,000+ games
        - 🏢 Explore developers and publishers
        - 📊 Interactive analytics and charts
        - 🔍 Advanced search functionality
        - 🤖 AI-powered gaming assistant 
        """
    }
)

# Initialize session state
init_session_state()
load_custom_css()
validate_environment()

@st.cache_resource
def init_rawg_client():
    api_key = os.getenv('RAWG_API_KEY')
    if not api_key:
        st.error("⚠️ RAWG API key not found! Please set your API key in the .env file.")
        st.info("Get your free API key from: https://rawg.io/apidocs")
        st.stop()
    return RAWGClient(api_key)

rawg_client = init_rawg_client()

def safe_format_number(value):
    """Return formatted number or 'N/A' if None."""
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return "N/A"

def main():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 0.9rem 0.4rem;'>
            <h1 style='font-size: 2.25rem; margin: 0;'>🎮</h1>
            <h2 style='margin: 0; color: #f97316;'>GAMEGUIDE</h2>
            <p style='font-size: 0.9rem; margin-top: 0.3rem;'>Gaming Database Explorer</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        chat_manager = get_chat_manager()
        if chat_manager.is_available():
            st.success("🤖 AI Assistant: Online")
            st.markdown("*Powered by Groq + Gemma2-9B*")
        else:
            st.warning("🤖 AI Assistant: Offline")
            st.markdown("*Add GROQ_API_KEY to enable*")

    st.markdown("""
    <div class='gg-hero'>
        <h1>🎮 GAMEGUIDE</h1>
        <p style='font-size: 1.08rem;'>Discover, compare, and track games across RAWG and Steam in one place.</p>
        <p>AI-assisted exploration powered by Groq + Gemma2-9B</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="🎮 Total Games", value="500,000+", delta="Growing daily")
    col2.metric(label="🖼️ Screenshots", value="2,100,000+", delta="High quality")
    col3.metric(label="🏢 Developers", value="220,000+", delta="Worldwide")
    col4.metric(label="🤖 AI Speed", value="800 tok/sec", delta="Rapid responses")

    st.markdown("---")
    st.subheader("🌟 Featured Sections")
     # Create feature cards
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

    with feature_col1:
        with st.container():
            st.markdown("""
            <div class='feature-card gg-feature-a'>
                <h3 style='margin: 0; font-size: 1.35rem;'>🎮 Browse Games</h3>
                <p style='margin: 0.45rem 0;'>Explore thousands of games with fast filters and wishlist actions.</p>
            </div>
            """, unsafe_allow_html=True)
           

    with feature_col2:
        with st.container():
            st.markdown("""
            <div class='feature-card gg-feature-b'>
                <h3 style='margin: 0; font-size: 1.35rem;'>📊 Analytics</h3>
                <p style='margin: 0.45rem 0;'>Understand ratings, genres, and platform trends across release years.</p>
        </div>
       """, unsafe_allow_html=True)


    with feature_col3:
        with st.container():
            st.markdown("""
            <div class='feature-card gg-feature-c'>
                <h3 style='margin: 0; font-size: 1.35rem;'>🔍 Advanced Search</h3>
                <p style='margin: 0.45rem 0;'>Jump to exact titles, deep details, screenshots, and achievements.</p>
            </div>
            """, unsafe_allow_html=True)

            

    with feature_col4:
        with st.container():
            st.markdown("""
            <div class='feature-card gg-feature-d'>
                <h3 style='margin: 0; font-size: 1.35rem;'>🤖 AI Assistant</h3>
                <p style='margin: 0.45rem 0;'>Chat for recommendations, quick comparisons, and gaming insights.</p>
            </div>
            """, unsafe_allow_html=True)

    # Featured cards (omitted here for brevity — same as yours)

    st.markdown("---")

    # 🔄 Updated Popular Games Section (Free & Paid)
    try:
        st.subheader("🔥 Most Played Games on Steam")
        col_free, col_paid = st.columns(2)

        with col_free:
            st.markdown("### 🆓 Free to Play")
            free_games = steam_client.get_most_played_games(limit=6, free_only=True)
            if free_games:
                for game in free_games:
                    appid = game.get("appid")
                    st.image(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg", width=300)
                    st.write(f"**{game.get('name')}**")
                    st.caption(f"👥 {safe_format_number(game.get('current_players'))} | 📈 Peak: {safe_format_number(game.get('peak_players'))}")
                    st.markdown("---")
            else:
                st.info("No free games found.")

        with col_paid:
            st.markdown("### 💰 Paid Games")
            paid_games = steam_client.get_most_played_games(limit=6, free_only=False)
            if paid_games:
                for game in paid_games:
                    appid = game.get("appid")
                    st.image(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg", width=300)
                    st.write(f"**{game.get('name')}**")
                    st.caption(f"👥 {safe_format_number(game.get('current_players'))} | 📈 Peak: {safe_format_number(game.get('peak_players'))}")
                    st.markdown("---")
            else:
                st.info("No paid games found.")

    except Exception as e:
        st.error("Error loading Steam's most played games:")
        st.exception(e)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #666;'>
        <p>Built with ❤️ using <a href='https://streamlit.io'>Streamlit</a>, <a href='https://rawg.io'>RAWG.io API</a>, and <a href='https://groq.com'>Groq AI</a></p>
        <p>© GAMEGUIDE VERSION 2025</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
