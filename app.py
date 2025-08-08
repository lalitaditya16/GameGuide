import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd 
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
    <div class='hero'>
        <h1>🎮 GAMEGUIDE</h1>
        <p>Discover, explore, and analyze the world's largest video game database.</p>
        <p style='opacity:.85'>✨ AI-powered assistant (Groq + Gemma2-9B) over the RAWG database</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="🎮 Total Games", value="500,000+", delta="Growing daily")

    with col2:
        st.metric(label="🖼️ Screenshots", value="2,100,000+", delta="High quality")

    with col3:
        st.metric(label="🏢 Developers", value="220,000+", delta="Worldwide")

    with col4:
        st.metric(label="🤖 AI Speed", value="800 tok/sec", delta="40x faster than GPT")

    st.markdown("---")

    # Featured sections
    st.markdown("<div class='section-title'><span class='dot'></span>🌟 Featured Sections</div>", unsafe_allow_html=True)

    # Create feature cards
    c1, c2, c3, c4 = st.columns(4)
    st.markdown("""
    <div class='grid'>
      <div class='game-card'>
        <div class='card-body'>
          <div class='card-title'>🎮 Browse Games</div>
          <div class='meta'><span class='tag'>Search</span><span class='tag'>Filters</span><span class='tag'>Sorting</span></div>
        </div>
      </div>
      <div class='game-card'>
        <div class='card-body'>
          <div class='card-title'>📊 Analytics</div>
          <div class='meta'><span class='tag'>Trends</span><span class='tag'>Charts</span><span class='tag'>Insights</span></div>
        </div>
      </div>
      <div class='game-card'>
        <div class='card-body'>
          <div class='card-title'>🔍 Advanced Search</div>
          <div class='meta'><span class='tag'>Multi-Filter</span><span class='tag'>Exact</span><span class='tag'>Screenshots</span></div>
        </div>
      </div>
      <div class='game-card'>
        <div class='card-body'>
          <div class='card-title'>🤖 AI Assistant</div>
          <div class='meta'><span class='tag'>Chat</span><span class='tag'>Recommend</span><span class='tag'>Explain</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Recent popular games preview
    try:
        st.markdown("<div class='section-title'><span class='dot'></span>🔥 Popular Games</div>", unsafe_allow_html=True)

        # Get current month date range
        from datetime import datetime
        today = datetime.today()
        three_months_ago = today - timedelta(days=90)
        start_date = three_months_ago.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        popular_games = rawg_client.search_games_popular(
            ordering="-rating",
            dates=f"{start_date},{end_date}",
            page_size=6
        )

        # Render grid of game cards
        card_html = [
            f"""
            <div class='game-card'>
                <div class='card-image'>
                    {'<img src="{img}" />'.format(img=game.get('background_image')) if game.get('background_image') else ''}
                    <div class='card-overlay'></div>
                    <div class='rating-badge'>⭐ {game.get('rating','N/A')}</div>
                </div>
                <div class='card-body'>
                    <div class='card-title'>🎮 {game.get('name')}</div>
                    <div class='meta'>
                        <span class='tag'>{game.get('released','N/A')}</span>
                        {''.join([f"<span class='tag'>{g}</span>" for g in game.get('genres', [])[:3]])}
                    </div>
                </div>
            </div>
            """
            for game in popular_games
        ]

        st.markdown("<div class='grid'>" + "".join(card_html) + "</div>", unsafe_allow_html=True)

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
    <div style='text-align:center; padding: 1.5rem 0; color: var(--muted);'>
        <p>Built with ❤️ using <a href='https://streamlit.io' target='_blank'>Streamlit</a>, <a href='https://rawg.io' target='_blank'>RAWG.io API</a>, and <a href='https://groq.com' target='_blank'>Groq AI</a></p>
        <p>© 2025 GameGuide. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
