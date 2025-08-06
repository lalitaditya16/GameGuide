
"""
Helper functions for the RAWG Streamlit Application with Groq AI Integration
==========================================================================

This module contains utility functions for session state management, 
CSS loading, AI chat functionality using Groq, and other helper functions.
"""

import streamlit as st
import os
from typing import Dict, List, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
import json
import logging
from datetime import datetime

# Import configurations
from config import config, SESSION_KEYS, ERROR_MESSAGES, SUCCESS_MESSAGES, AI_PROMPTS, CUSTOM_CSS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def clean_description(text):
    # Replace headings like "###Setting" or "### Characters" with bold text
    cleaned = re.sub(r"###\s*(\w+)", r"**\1:**", text)
    return cleaned
def init_session_state():
    """Initialize Streamlit session state variables."""

    # Initialize favorites
    if SESSION_KEYS['favorites'] not in st.session_state:
        st.session_state[SESSION_KEYS['favorites']] = []

    # Initialize search history
    if SESSION_KEYS['search_history'] not in st.session_state:
        st.session_state[SESSION_KEYS['search_history']] = []

    # Initialize current page
    if SESSION_KEYS['current_page'] not in st.session_state:
        st.session_state[SESSION_KEYS['current_page']] = 1

    # Initialize filters
    if SESSION_KEYS['filters'] not in st.session_state:
        st.session_state[SESSION_KEYS['filters']] = {}

    # Initialize user preferences
    if SESSION_KEYS['user_preferences'] not in st.session_state:
        st.session_state[SESSION_KEYS['user_preferences']] = {
            'theme': 'light',
            'items_per_page': config.default_page_size,
            'enable_ai': True
        }

    # Initialize chat history
    if SESSION_KEYS['chat_history'] not in st.session_state:
        st.session_state[SESSION_KEYS['chat_history']] = []

    # Initialize AI context
    if SESSION_KEYS['ai_context'] not in st.session_state:
        st.session_state[SESSION_KEYS['ai_context']] = {}

def load_custom_css():
    """Load custom CSS styles."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def validate_environment():
    """Validate environment setup for the application."""
    issues = []

    # Check RAWG API key
    if not config.rawg_api_key:
        issues.append("RAWG API key is missing")

    # Check Groq API key for AI features
    if not config.groq_api_key:
        issues.append("Groq API key is missing (AI features will be disabled)")

    if issues:
        with st.sidebar:
            st.warning("⚠️ Configuration Issues:")
            for issue in issues:
                st.write(f"• {issue}")

            if "RAWG API key is missing" in str(issues):
                st.error("🔗 Get your RAWG API key: https://rawg.io/apidocs")

            if "Groq API key is missing" in str(issues):
                st.info("🤖 Get your Groq API key: https://console.groq.com/keys")

class GroqChatManager:
    """Manages AI chat functionality using Groq with Gemma2-9B."""

    def __init__(self):
        """Initialize the Groq chat manager."""
        self.groq_api_key = config.groq_api_key
        self.model_name = config.groq_model
        self.temperature = config.groq_temperature
        self.max_tokens = config.groq_max_tokens
        self.llm = None
        self.chain = None

        if self.groq_api_key:
            try:
                self.llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                # Create the chat chain
                prompt = ChatPromptTemplate.from_messages([
                    ("system", AI_PROMPTS['system_prompt']),
                    ("human", "{input}")
                ])

                self.chain = prompt | self.llm | StrOutputParser()
                logger.info("Groq chat manager initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                self.llm = None
                self.chain = None

    def is_available(self) -> bool:
        """Check if AI chat is available."""
        return self.chain is not None

    def get_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Get AI response for user input.

        Args:
            user_input (str): User's message
            context (dict, optional): Additional context for the AI

        Returns:
            str: AI response
        """
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']

        try:
            # Add context to the input if provided
            enhanced_input = user_input
            if context:
                context_str = json.dumps(context, indent=2)
                enhanced_input = f"Context: {context_str}\n\nUser Query: {user_input}"

            response = self.chain.invoke({"input": enhanced_input})
            return response

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def analyze_game(self, game_data: Dict[str, Any]) -> str:
        """
        Analyze a game using AI.

        Args:
            game_data (dict): Game data from RAWG API

        Returns:
            str: AI analysis of the game
        """
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']

        try:
            prompt = AI_PROMPTS['game_analysis'].format(game_data=json.dumps(game_data, indent=2))
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            return f"Sorry, I couldn't analyze this game: {str(e)}"

    def get_recommendations(self, preferences: Dict[str, Any], games_data: List[Dict]) -> str:
        """
        Get game recommendations based on user preferences.

        Args:
            preferences (dict): User preferences
            games_data (list): Available games data

        Returns:
            str: AI recommendations
        """
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']

        try:
            prompt = AI_PROMPTS['recommendation'].format(
                preferences=json.dumps(preferences, indent=2),
                games_data=json.dumps(games_data[:10], indent=2)  # Limit to 10 games
            )
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return f"Sorry, I couldn't generate recommendations: {str(e)}"

    def analyze_trends(self, trend_data: Dict[str, Any]) -> str:
        """
        Analyze gaming trends using AI.

        Args:
            trend_data (dict): Trend data to analyze

        Returns:
            str: AI analysis of trends
        """
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']

        try:
            prompt = AI_PROMPTS['trend_analysis'].format(trend_data=json.dumps(trend_data, indent=2))
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return f"Sorry, I couldn't analyze trends: {str(e)}"

def get_chat_manager() -> GroqChatManager:
    """Get or create a cached chat manager instance."""
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = GroqChatManager()
    return st.session_state.chat_manager

def display_chat_interface():
    """Display the chat interface in Streamlit."""
    chat_manager = get_chat_manager()

    if not chat_manager.is_available():
        st.error(ERROR_MESSAGES['ai_not_available'])
        return

    # Chat history
    st.subheader("💬 Chat History")

    # Display messages
    for message in st.session_state[SESSION_KEYS['chat_history']]:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🤖 AI:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    st.markdown("---")
    user_input = st.text_input("Ask me anything about gaming:", key="chat_input")

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("Send", type="primary"):
            if user_input:
                # Add user message
                st.session_state[SESSION_KEYS['chat_history']].append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })

                # Get AI response
                with st.spinner("🤖 Thinking..."):
                    ai_response = chat_manager.get_response(user_input)

                # Add AI response
                st.session_state[SESSION_KEYS['chat_history']].append({
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })

                st.rerun()

    with col2:
        if st.button("Clear Chat"):
            st.session_state[SESSION_KEYS['chat_history']] = []
            st.rerun()

def show_message(message: str, message_type: str = "info"):
    """
    Display a formatted message to the user.

    Args:
        message (str): Message to display
        message_type (str): Type of message ('info', 'success', 'warning', 'error')
    """
    if message_type == "success":
        st.success(message)
    elif message_type == "warning":
        st.warning(message)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)

def add_to_favorites(game_id: int, game_data: Dict[str, Any]):
    """Add a game to user favorites."""
    favorites = st.session_state[SESSION_KEYS['favorites']]

    if game_id not in [fav['id'] for fav in favorites]:
        favorites.append({
            'id': game_id,
            'name': game_data.get('name', 'Unknown'),
            'image': game_data.get('background_image', ''),
            'rating': game_data.get('rating', 0),
            'added_at': datetime.now().isoformat()
        })
        show_message(SUCCESS_MESSAGES['game_added_to_favorites'], "success")
    else:
        show_message("Game is already in favorites!", "warning")

def remove_from_favorites(game_id: int):
    """Remove a game from user favorites."""
    favorites = st.session_state[SESSION_KEYS['favorites']]
    st.session_state[SESSION_KEYS['favorites']] = [
        fav for fav in favorites if fav['id'] != game_id
    ]
    show_message(SUCCESS_MESSAGES['game_removed_from_favorites'], "success")

def is_favorite(game_id: int) -> bool:
    """Check if a game is in user favorites."""
    favorites = st.session_state[SESSION_KEYS['favorites']]
    return game_id in [fav['id'] for fav in favorites]

def format_game_card(game: Dict[str, Any]) -> str:
    """Format a game as an HTML card."""
    genres = ', '.join([g['name'] for g in game.get('genres', [])][:3])
    platforms = ', '.join([p['platform']['name'] for p in game.get('platforms', [])][:3])

    return f"""
    <div class="game-card">
        <img src="{game.get('background_image', '')}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;">
        <h4 style="margin: 0.5rem 0;">{game.get('name', 'Unknown')}</h4>
        <p style="margin: 0; color: #666;">
            ⭐ {game.get('rating', 'N/A')}/5 | 
            📅 {game.get('released', 'TBA')}<br>
            🎯 {genres}<br>
            🎮 {platforms}
        </p>
    </div>
    """

def export_chat_history() -> str:
    """Export chat history as JSON."""
    chat_history = st.session_state[SESSION_KEYS['chat_history']]
    return json.dumps(chat_history, indent=2)

def get_ai_quick_actions() -> List[str]:
    """Get list of quick action prompts for AI chat."""
    return [
        "Recommend some indie games",
        "What are the trending games this year?",
        "Best RPGs for beginners",
        "Compare PlayStation vs Xbox",
        "Upcoming game releases",
        "Best co-op games",
        "Gaming industry trends",
        "Free-to-play game recommendations"
    ]

# Utility functions for data processing
def safe_get(data: Dict, key: str, default: Any = None):
    """Safely get a value from a dictionary."""
    return data.get(key, default) if data else default

def format_date(date_string: str) -> str:
    """Format date string for display."""
    if not date_string:
        return "TBA"

    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_string

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length-3] + "..."

def format_number(number: int) -> str:
    """Format number for display (e.g., 1234 -> 1.2K)."""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(number)
