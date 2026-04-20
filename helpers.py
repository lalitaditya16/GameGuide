"""
GameGuide helpers — session state, profiles, favorites, AI chat (with streaming).
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
import re

from config import config, SESSION_KEYS, ERROR_MESSAGES, SUCCESS_MESSAGES, AI_PROMPTS, CUSTOM_CSS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")
PROFILES_FILE  = os.path.join(DATA_DIR, "profiles.json")
DEFAULT_PROFILE_NAME = "Player1"


# ---------------------------------------------------------------------------
# Profile helpers
# ---------------------------------------------------------------------------

def _default_preferences() -> Dict[str, Any]:
    return {
        'theme': 'dark',
        'items_per_page': config.default_page_size,
        'enable_ai': True,
        'favorite_genres': [],
        'favorite_platforms': [],
    }


def _default_profile(name: str) -> Dict[str, Any]:
    return {
        'display_name': name,
        'created_at':   datetime.now().isoformat(),
        'preferences':  _default_preferences(),
        'wishlist':     [],
        'played_games': [],
    }


def _load_favorites_from_disk() -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(FAVORITES_FILE):
            return []
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception as e:
        logger.warning(f"Failed to load favorites: {e}")
    return []


def _save_favorites_to_disk(favorites: List[Dict[str, Any]]) -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(favorites, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save favorites: {e}")


def _load_profiles_from_disk() -> Dict[str, Any]:
    store = {'active_profile': DEFAULT_PROFILE_NAME, 'profiles': {}}
    try:
        if os.path.exists(PROFILES_FILE):
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict) and isinstance(loaded.get('profiles'), dict):
                store = loaded
    except Exception as e:
        logger.warning(f"Failed to load profiles: {e}")

    if not store['profiles']:
        profile = _default_profile(DEFAULT_PROFILE_NAME)
        profile['wishlist'] = _load_favorites_from_disk()
        store['profiles'][DEFAULT_PROFILE_NAME] = profile
        store['active_profile'] = DEFAULT_PROFILE_NAME

    active = store.get('active_profile')
    if active not in store['profiles']:
        store['active_profile'] = next(iter(store['profiles'].keys()))

    for name, profile in store['profiles'].items():
        profile.setdefault('display_name', name)
        profile.setdefault('created_at', datetime.now().isoformat())
        profile.setdefault('preferences', _default_preferences())
        profile.setdefault('wishlist', [])
        profile.setdefault('played_games', [])
        prefs = profile.get('preferences', {})
        for key, value in _default_preferences().items():
            prefs.setdefault(key, value)

    return store


def _save_profiles_to_disk(store: Dict[str, Any]) -> None:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
        active_profile = store['profiles'].get(store.get('active_profile'))
        if active_profile:
            _save_favorites_to_disk(active_profile.get('wishlist', []))
    except Exception as e:
        logger.warning(f"Failed to save profiles: {e}")


def _get_profile_store() -> Dict[str, Any]:
    if 'profile_store' not in st.session_state:
        st.session_state['profile_store'] = _load_profiles_from_disk()
    return st.session_state['profile_store']


def _get_active_profile_data() -> Dict[str, Any]:
    store = _get_profile_store()
    return store['profiles'][store['active_profile']]


def _persist_profile_store() -> None:
    _save_profiles_to_disk(_get_profile_store())


def get_profiles() -> List[str]:
    return sorted(_get_profile_store()['profiles'].keys())


def get_active_profile_name() -> str:
    return _get_profile_store()['active_profile']


def create_profile(name: str) -> bool:
    normalized = (name or "").strip()
    if not normalized:
        return False
    store = _get_profile_store()
    if normalized in store['profiles']:
        return False
    store['profiles'][normalized] = _default_profile(normalized)
    store['active_profile'] = normalized
    _persist_profile_store()
    return True


def set_active_profile(name: str) -> bool:
    store = _get_profile_store()
    if name not in store['profiles']:
        return False
    store['active_profile'] = name
    _persist_profile_store()
    return True


def delete_profile(name: str) -> bool:
    store = _get_profile_store()
    if name not in store['profiles'] or len(store['profiles']) <= 1:
        return False
    del store['profiles'][name]
    if store['active_profile'] == name:
        store['active_profile'] = next(iter(store['profiles'].keys()))
    _persist_profile_store()
    return True


def get_user_preferences() -> Dict[str, Any]:
    return _get_active_profile_data().get('preferences', _default_preferences())


def update_user_preferences(preferences: Dict[str, Any]) -> None:
    profile = _get_active_profile_data()
    current = profile.get('preferences', _default_preferences())
    current.update(preferences)
    profile['preferences'] = current
    st.session_state[SESSION_KEYS['user_preferences']] = current
    _persist_profile_store()


def clean_description(text: str) -> str:
    return re.sub(r"###\s*(\w+)", r"**\1:**", text)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_session_state():
    store = _get_profile_store()
    active_profile = store['profiles'][store['active_profile']]

    st.session_state[SESSION_KEYS['favorites']] = active_profile.get('wishlist', [])

    if SESSION_KEYS['search_history'] not in st.session_state:
        st.session_state[SESSION_KEYS['search_history']] = []
    if SESSION_KEYS['current_page'] not in st.session_state:
        st.session_state[SESSION_KEYS['current_page']] = 1
    if SESSION_KEYS['filters'] not in st.session_state:
        st.session_state[SESSION_KEYS['filters']] = {}
    if SESSION_KEYS['game_status'] not in st.session_state:
        st.session_state[SESSION_KEYS['game_status']] = {}

    st.session_state[SESSION_KEYS['user_preferences']] = active_profile.get('preferences', _default_preferences())

    if SESSION_KEYS['chat_history'] not in st.session_state:
        st.session_state[SESSION_KEYS['chat_history']] = []
    if SESSION_KEYS['ai_context'] not in st.session_state:
        st.session_state[SESSION_KEYS['ai_context']] = {}


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def load_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_theme_mode() -> str:
    return get_user_preferences().get('theme', 'dark')


def render_theme_toggle():
    current_mode = get_theme_mode()
    is_dark = st.sidebar.toggle("🌗 Dark Mode", value=(current_mode == "dark"), key="gg_theme_toggle")
    new_mode = "dark" if is_dark else "light"
    if get_user_preferences().get('theme') != new_mode:
        update_user_preferences({'theme': new_mode})
        st.rerun()


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------

def validate_environment():
    issues = []
    if not config.rawg_api_key:
        issues.append("RAWG API key is missing")
    if not config.groq_api_key:
        issues.append("Groq API key is missing (AI features disabled)")

    if issues:
        with st.sidebar:
            st.warning("Configuration issues:")
            for issue in issues:
                st.write(f"• {issue}")


# ---------------------------------------------------------------------------
# AI Chat Manager — llama-3.3-70b-versatile with streaming
# ---------------------------------------------------------------------------

class GroqChatManager:
    def __init__(self):
        self.groq_api_key = config.groq_api_key
        self.model_name   = config.groq_model
        self.temperature  = config.groq_temperature
        self.max_tokens   = config.groq_max_tokens
        self.llm          = None
        self.chain        = None

        if self.groq_api_key:
            try:
                self.llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                prompt = ChatPromptTemplate.from_messages([
                    ("system", AI_PROMPTS['system_prompt']),
                    ("human",  "{input}"),
                ])
                self.chain = prompt | self.llm | StrOutputParser()
                logger.info(f"Groq ready — {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to init Groq: {e}")

    def is_available(self) -> bool:
        return self.chain is not None

    def get_response(self, user_input: str, context: Dict = None) -> str:
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']
        try:
            enhanced = user_input
            if context:
                enhanced = f"Context: {json.dumps(context)}\n\nUser: {user_input}"
            return self.chain.invoke({"input": enhanced})
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return f"Sorry, ran into an error: {e}"

    def stream_response(self, user_input: str, context: Dict = None):
        """Yields text tokens — use with st.write_stream()."""
        if not self.groq_api_key:
            yield ERROR_MESSAGES['ai_not_available']
            return
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)

            today = datetime.now().strftime("%B %d, %Y")
            messages = [
                {"role": "system", "content": AI_PROMPTS['system_prompt'].format(today=today)}
            ]

            if context:
                messages.append({
                    "role":    "system",
                    "content": f"Game context: {json.dumps(context, indent=2)}",
                })

            for msg in st.session_state.get(SESSION_KEYS['chat_history'], [])[-8:]:
                role = "user" if msg.get('role') == 'user' else "assistant"
                messages.append({"role": role, "content": msg.get('content', '')})

            messages.append({"role": "user", "content": user_input})

            stream = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        except Exception as e:
            yield f"Error: {e}"

    def analyze_game(self, game_data: Dict) -> str:
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']
        try:
            prompt = AI_PROMPTS['game_analysis'].format(game_data=json.dumps(game_data, indent=2))
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Could not analyse game: {e}"

    def generate_guide(self, game_name: str) -> str:
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']
        try:
            prompt = AI_PROMPTS['game_guide'].format(game_name=game_name)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Could not generate guide: {e}"

    def get_recommendations(self, preferences: Dict, games_data: List[Dict]) -> str:
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']
        try:
            prompt = AI_PROMPTS['recommendation'].format(
                preferences=json.dumps(preferences, indent=2),
                games_data=json.dumps(games_data[:10], indent=2),
            )
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Could not get recommendations: {e}"

    def analyze_trends(self, trend_data: Dict) -> str:
        if not self.is_available():
            return ERROR_MESSAGES['ai_not_available']
        try:
            prompt = AI_PROMPTS['trend_analysis'].format(trend_data=json.dumps(trend_data, indent=2))
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Could not analyse trends: {e}"


def get_chat_manager() -> GroqChatManager:
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = GroqChatManager()
    return st.session_state.chat_manager


# ---------------------------------------------------------------------------
# Favorites / wishlist
# ---------------------------------------------------------------------------

def show_message(message: str, message_type: str = "info"):
    if message_type == "success":
        st.success(message)
    elif message_type == "warning":
        st.warning(message)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)


def add_to_favorites(game_id: int, game_data: Dict):
    profile   = _get_active_profile_data()
    favorites = profile.get('wishlist', [])
    if game_id not in [f['id'] for f in favorites]:
        favorites.append({
            'id':       game_id,
            'name':     game_data.get('name', 'Unknown'),
            'image':    game_data.get('background_image', ''),
            'rating':   game_data.get('rating', 0),
            'added_at': datetime.now().isoformat(),
        })
        profile['wishlist'] = favorites
        st.session_state[SESSION_KEYS['favorites']] = favorites
        _persist_profile_store()
        show_message(SUCCESS_MESSAGES['game_added_to_favorites'], "success")
    else:
        show_message("Already in your list.", "warning")


def get_favorites() -> List[Dict]:
    return _get_active_profile_data().get('wishlist', [])


def replace_favorites(favorites: List[Dict]) -> None:
    profile = _get_active_profile_data()
    profile['wishlist'] = favorites
    st.session_state[SESSION_KEYS['favorites']] = favorites
    _persist_profile_store()


def update_favorite_note(game_id: int, note: str) -> bool:
    favorites = get_favorites()
    for fav in favorites:
        if fav.get('id') == game_id:
            fav['note'] = note.strip()
            replace_favorites(favorites)
            return True
    return False


def export_favorites_json() -> str:
    return json.dumps(get_favorites(), indent=2)


def import_favorites_json(json_text: str, mode: str = "merge") -> Dict[str, int]:
    data = json.loads(json_text)
    if not isinstance(data, list):
        raise ValueError("Imported data must be a JSON array.")
    incoming = [
        {
            'id':       item.get('id'),
            'name':     item.get('name', 'Unknown'),
            'image':    item.get('image', ''),
            'rating':   item.get('rating', 0),
            'added_at': item.get('added_at', datetime.now().isoformat()),
            'note':     item.get('note', ''),
        }
        for item in data
        if isinstance(item, dict) and item.get('id') is not None
    ]
    if mode == "replace":
        replace_favorites(incoming)
        return {'imported': len(incoming), 'skipped': len(data) - len(incoming)}
    existing     = get_favorites()
    existing_ids = {f.get('id') for f in existing}
    added = skipped = 0
    for item in incoming:
        if item['id'] in existing_ids:
            skipped += 1
        else:
            existing.append(item)
            existing_ids.add(item['id'])
            added += 1
    replace_favorites(existing)
    return {'imported': added, 'skipped': skipped + (len(data) - len(incoming))}


def remove_from_favorites(game_id: int):
    replace_favorites([f for f in get_favorites() if f['id'] != game_id])
    show_message(SUCCESS_MESSAGES['game_removed_from_favorites'], "success")


def is_favorite(game_id: int) -> bool:
    return game_id in [f['id'] for f in get_favorites()]


# ---------------------------------------------------------------------------
# Game status list (MAL-style)
# ---------------------------------------------------------------------------

def get_game_status(game_id: int) -> Optional[str]:
    return st.session_state.get(SESSION_KEYS['game_status'], {}).get(game_id)


def set_game_status(game_id: int, status: Optional[str]):
    status_map = st.session_state.setdefault(SESSION_KEYS['game_status'], {})
    if status and status != "-- None --":
        status_map[game_id] = status
    else:
        status_map.pop(game_id, None)


# ---------------------------------------------------------------------------
# Played games
# ---------------------------------------------------------------------------

def get_played_games() -> List[Dict]:
    return _get_active_profile_data().get('played_games', [])


def add_played_game(
    game_data: Dict,
    hours_played: float = 0.0,
    user_rating: Optional[float] = None,
    note: str = "",
):
    profile      = _get_active_profile_data()
    played_games = profile.get('played_games', [])
    game_id      = game_data.get('id')
    if not game_id:
        return False
    entry = {
        'id':             game_id,
        'name':           game_data.get('name', 'Unknown'),
        'image':          game_data.get('background_image', ''),
        'released':       game_data.get('released', 'N/A'),
        'rawg_rating':    game_data.get('rating', 0),
        'hours_played':   float(hours_played or 0.0),
        'user_rating':    user_rating,
        'note':           (note or '').strip(),
        'last_played_at': datetime.now().isoformat(),
    }
    replaced = False
    for i, item in enumerate(played_games):
        if item.get('id') == game_id:
            played_games[i] = entry
            replaced = True
            break
    if not replaced:
        played_games.append(entry)
    profile['wishlist']     = [f for f in profile.get('wishlist', []) if f.get('id') != game_id]
    profile['played_games'] = played_games
    st.session_state[SESSION_KEYS['favorites']] = profile['wishlist']
    _persist_profile_store()
    return True


def remove_played_game(game_id: int):
    profile = _get_active_profile_data()
    profile['played_games'] = [g for g in profile.get('played_games', []) if g.get('id') != game_id]
    _persist_profile_store()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def format_date(date_string: str) -> str:
    if not date_string:
        return "TBA"
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00')).strftime("%B %d, %Y")
    except Exception:
        return date_string


def truncate_text(text: str, max_length: int = 100) -> str:
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length - 3] + "..."


def format_number(number: int) -> str:
    if number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number/1_000:.1f}K"
    return str(number)


def export_chat_history() -> str:
    return json.dumps(st.session_state.get(SESSION_KEYS['chat_history'], []), indent=2)


def get_ai_quick_actions() -> List[str]:
    return [
        "Recommend some indie games",
        "Best RPGs for beginners",
        "Trending games in 2025",
        "Best co-op games to play with friends",
        "Free-to-play games worth trying",
        "Compare PlayStation vs Xbox exclusives",
        "Hidden gem games",
        "Best open world games",
    ]


def display_chat_interface():
    chat_manager = get_chat_manager()
    if not chat_manager.is_available():
        st.error(ERROR_MESSAGES['ai_not_available'])
        return

    st.subheader("Chat History")
    for message in st.session_state[SESSION_KEYS['chat_history']]:
        if message['role'] == 'user':
            st.markdown(
                f'<div class="chat-bubble-user"><strong>You:</strong> {message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-ai"><strong>AI:</strong> {message["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    user_input = st.text_input("Ask anything about gaming:", key="chat_input")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Send", type="primary") and user_input:
            st.session_state[SESSION_KEYS['chat_history']].append(
                {'role': 'user', 'content': user_input, 'timestamp': datetime.now().isoformat()}
            )
            with st.spinner("Thinking..."):
                ai_response = chat_manager.get_response(user_input)
            st.session_state[SESSION_KEYS['chat_history']].append(
                {'role': 'assistant', 'content': ai_response, 'timestamp': datetime.now().isoformat()}
            )
            st.rerun()
    with col2:
        if st.button("Clear Chat"):
            st.session_state[SESSION_KEYS['chat_history']] = []
            st.rerun()
