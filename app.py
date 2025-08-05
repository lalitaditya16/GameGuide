import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime 
from dotenv import load_dotenv

# ✅ Ensure this has no spaces/tabs before it
from rawg_client import RAWGClient
from helpers import init_session_state, load_custom_css, validate_environment, get_chat_manager


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

        Built with ❤️ using Streamlit, RAWG API, and Groq AI
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
        <h1 style='color: #FF6B6B; font-size: 3rem; margin: 0;'>
            🎮 GAMEGUIDE
        </h1>
        <p style='font-size: 1.2rem; color: #666; margin-top: 0.5rem;'>
            Discover, explore, and analyze the world's largest video game database
        </p>
        <p style='font-size: 1rem; color: #888; margin-top: 0.25rem;'>
            ✨ Now with AI-powered gaming assistant using Groq + Gemma2-9B and the RAWG database
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🎮 Total Games", 
            value="500,000+", 
            delta="Growing daily"
        )

    with col2:
        st.metric(
            label="🖼️ Screenshots", 
            value="2,100,000+", 
            delta="High quality"
        )

    with col3:
        st.metric(
            label="🏢 Developers", 
            value="220,000+", 
            delta="Worldwide"
        )

    with col4:
        st.metric(
            label="🤖 AI Speed", 
            value="800 tok/sec", 
            delta="40x faster than GPT"
        )

    st.markdown("---")

    # Featured sections
    st.subheader("🌟 Featured Sections")

    # Create feature cards
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

    with feature_col1:
        with st.container():
            st.markdown("""
            <div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; font-size: 1.5rem;'>🎮 Browse Games</h3>
                <p style='margin: 0.5rem 0;'>Explore our vast collection of games with advanced search and filtering</p>
            </div>
            <a href="/🎮_Browse_Games" target="_self">
                <button style='width: 100%; padding: 0.75rem; border: none; border-radius: 8px; background-color: white; color: #764ba2; font-weight: bold; font-size: 1rem; cursor: pointer;'>
                    🎮 Start Browsing
                </button>
            </a>
            """, unsafe_allow_html=True)
           

    with feature_col2:
        with st.container():
            st.markdown("""
            <div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-align: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; font-size: 1.5rem;'>📊 Analytics</h3>
                <p style='margin: 0.5rem 0;'>Dive into gaming trends, statistics, and interactive visualizations</p>
        </div>
        <a href="/📊Game Analytics" target="_self">
            <button style='width: 100%; padding: 0.75rem; border: none; border-radius: 8px; background-color: white; color: #f5576c; font-weight: bold; font-size: 1rem; cursor: pointer;'>
                📊 View Analytics
            </button>
        </a>
        """, unsafe_allow_html=True)


    with feature_col3:
        with st.container():
            st.markdown("""
            <div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; text-align: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; font-size: 1.5rem;'>🔍 Advanced Search</h3>
                <p style='margin: 0.5rem 0;'>Find exactly what you're looking for with powerful search tools</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔍 Advanced Search", key="advanced_search", use_container_width=True):
                st.info("📝 Create pages/09_🔍_Advanced_Search.py to enable advanced search")

    with feature_col4:
        with st.container():
            st.markdown("""
            <div style='padding: 1.5rem; border-radius: 10px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; text-align: center; margin-bottom: 1rem;'>
                <h3 style='margin: 0; font-size: 1.5rem;'>🤖 AI Assistant</h3>
                <p style='margin: 0.5rem 0;'>Chat with AI about games, get recommendations, and gaming insights</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🤖 Chat with AI", key="ai_chat", use_container_width=True):
                if chat_manager.is_available():
                    st.info("📝 Create pages/11_🤖_AI_Chat.py to enable AI chat interface")
                else:
                    st.warning("⚠️ AI features require GROQ_API_KEY in your .env file")

    st.markdown("---")

    # AI-powered quick demo (if available)
    if chat_manager.is_available():
        st.subheader("🤖 AI Assistant Demo")

        demo_col1, demo_col2 = st.columns([2, 1])

        with demo_col1:
            st.markdown("""
            **Try our AI gaming assistant!** Ask questions like:
            - "What are the best indie games of 2024?"
            - "Recommend some RPGs for beginners"
            - "Compare PlayStation 5 vs Xbox Series X"
            """)

            demo_input = st.text_input("Ask me anything about gaming:", key="demo_chat")

            if st.button("Ask AI", key="demo_ask"):
                if demo_input:
                    with st.spinner("🤖 Thinking..."):
                        response = chat_manager.get_response(demo_input)
                    st.success(f"🤖 AI Response: {response}")

        with demo_col2:
            st.info("""
            **⚡ Lightning Fast**
            - 800+ tokens/second
            - Sub-second responses
            - Powered by Groq + Gemma2

            **🧠 Smart & Knowledgeable**
            - Gaming industry expertise
            - Game recommendations
            - Trend analysis
            """)

    # Recent popular games preview
    try:
        st.subheader("🔥 Popular Games This Month")

    # Get current month date range
        from datetime import datetime
        today = datetime.today()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        popular_games = rawg_client.search_games_popular(
            ordering="-added",
            dates=f"{start_date},{end_date}",
            page_size=6
        )

        for game in popular_games:
            name = game.get("name")
            rating = game.get("rating")
            released = game.get("released")
            platforms = game.get("platforms", [])
            genres = game.get("genres", [])
            image = game.get("background_image")

            st.markdown(f"### 🎮 {name}")
            st.write(f"⭐ Rating: {rating}")
            st.write(f"📅 Released: {released}")
            st.write(f"🧩 Platforms: {', '.join(platforms)}")
            st.write(f"🏷️ Genres: {', '.join(genres)}")

            if image:
                st.image(image, width=600)

            st.markdown("---")

    except Exception as e:
        st.error("Error loading popular games:")
        st.exception(e)

    nav_col1, nav_col2 = st.columns([1, 5])
    with nav_col1:
        st.markdown("""
        **🎮 Game Discovery:**
        - Browse Games: Search and filter games
        - Genres: Explore by game categories  
        - Platforms: Find games for your system
        - Advanced Search: Multi-parameter filtering

        **🤖 AI Features:**
        - AI Chat: Natural language gaming assistant
        - Game Analysis: AI-powered game insights
        - Recommendations: Personalized suggestions
        """)

    with nav_col2:
        st.markdown("""
        **🏢 Industry Insights:**
        - Developers: Game development studios
        - Publishers: Game publishing companies
        - Creators: Individual contributors
        - Analytics: Trends and statistics

        **⚙️ Setup Requirements:**
        - RAWG API Key: Get from rawg.io/apidocs
        - Groq API Key: Get from console.groq.com/keys
        - Environment file: Copy env-template.txt to .env
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #666;'>
        <p>Built with ❤️ using <a href='https://streamlit.io'>Streamlit</a>, <a href='https://rawg.io'>RAWG.io API</a>, and <a href='https://groq.com'>Groq AI</a></p>
        <p>🚀 <strong>40x faster AI responses</strong> with Groq + Gemma2-9B | 🆓 <strong>Free tiers available</strong></p>
        <p>© 2024 RAWG Gaming Database Explorer. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
