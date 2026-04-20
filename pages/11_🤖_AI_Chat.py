import streamlit as st
from datetime import datetime
from groq import Groq
from config import config, SESSION_KEYS, AI_PROMPTS
from rawg_client import RAWGClient
from helpers import init_session_state, load_custom_css, render_theme_toggle, get_ai_quick_actions

st.set_page_config(page_title="AI Chat — GameGuide", page_icon="🤖", layout="wide")
init_session_state()
load_custom_css()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    render_theme_toggle()
    st.markdown("---")
    st.markdown(
        '<p style="font-family:Orbitron,monospace; font-size:0.8rem; color:#a78bfa;">AI MODEL</p>',
        unsafe_allow_html=True,
    )
    model_choice = st.radio(
        "Speed vs power",
        ["llama-3.3-70b-versatile (Smart)", "llama-3.1-8b-instant (Fast)"],
        label_visibility="collapsed",
    )
    active_model = (
        "llama-3.3-70b-versatile" if "70b" in model_choice else "llama-3.1-8b-instant"
    )
    st.caption(f"Using: `{active_model}`")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state[SESSION_KEYS['chat_history']] = []
        st.session_state[SESSION_KEYS['ai_context']] = {}
        st.rerun()

    context = st.session_state.get(SESSION_KEYS['ai_context'], {})
    if context.get('game_name'):
        st.markdown("---")
        st.markdown(
            '<p style="font-family:Orbitron,monospace; font-size:0.75rem; color:#06b6d4;">CONTEXT</p>',
            unsafe_allow_html=True,
        )
        st.caption(f"🎮 {context['game_name']}")
        if st.button("✕ Clear context"):
            st.session_state[SESSION_KEYS['ai_context']] = {}
            st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom:1rem;">
  <h1 style="font-family:Orbitron,monospace; font-size:1.6rem; margin:0;
             background:linear-gradient(135deg,#7c3aed,#06b6d4);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             background-clip:text;">
    🤖 AI GAME ASSISTANT
  </h1>
  <p style="color:#64748b; font-size:0.85rem; margin-top:0.3rem;">
    Powered by Groq &nbsp;·&nbsp; Streaming responses &nbsp;·&nbsp; Context-aware
  </p>
</div>
""", unsafe_allow_html=True)

today = datetime.now().strftime("%B %d, %Y")
today_iso = datetime.now().strftime("%Y-%m-%d")

if not config.groq_api_key:
    st.error("🤖 AI offline — add GROQ_API_KEY to your .env file.")
    st.stop()

groq_client = Groq(api_key=config.groq_api_key)
rawg = RAWGClient(api_key=config.rawg_api_key)

chat_history = st.session_state.setdefault(SESSION_KEYS['chat_history'], [])
ai_context   = st.session_state.setdefault(SESSION_KEYS['ai_context'], {})

# ---------------------------------------------------------------------------
# Quick action chips
# ---------------------------------------------------------------------------
quick_actions = get_ai_quick_actions()
chips_html = "".join(f'<span class="quick-chip" id="chip_{i}">{a}</span>' for i, a in enumerate(quick_actions))
st.markdown(f'<div class="chip-row">{chips_html}</div>', unsafe_allow_html=True)

chip_cols = st.columns(len(quick_actions))
selected_quick = None
for i, (col, action) in enumerate(zip(chip_cols, quick_actions)):
    with col:
        if st.button(action, key=f"chip_{i}", use_container_width=True):
            selected_quick = action

# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------
if chat_history:
    st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
    for msg in chat_history:
        if msg['role'] == 'user':
            st.markdown(
                f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
prompt = st.chat_input("Ask about any game, genre, tips, recommendations...")

if selected_quick:
    prompt = selected_quick

if prompt:
    # ------------------------------------------------------------------
    # Game lookup — try to detect game context from the prompt
    # ------------------------------------------------------------------
    game_info = {}
    try:
        game = rawg.search_best_match(prompt)
        if game:
            game_id      = game.get("id")
            game_details = rawg.get_game_details(game_id)
            game_name    = game_details.get("name", "")
            release_date = game_details.get("released", "")
            bg_img       = game_details.get("background_image", "")
            rating       = game_details.get("rating", "N/A")
            platforms_str = ", ".join(p['platform']['name'] for p in game_details.get("platforms", []))
            genres_str    = ", ".join(g['name'] for g in game_details.get("genres", []))
            description   = game_details.get("description_raw", "")[:600]

            game_info = {
                "game_name":    game_name,
                "released":     release_date,
                "rating":       rating,
                "platforms":    platforms_str,
                "genres":       genres_str,
                "description":  description,
            }
            st.session_state[SESSION_KEYS['ai_context']] = game_info

            if bg_img:
                st.image(bg_img, use_container_width=True)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("⭐ Rating", f"{rating}/5")
            col_b.metric("📅 Released", release_date or "TBA")
            col_c.metric("🎯 Genres", genres_str[:30] or "—")

    except Exception:
        pass

    # ------------------------------------------------------------------
    # Build messages for Groq
    # ------------------------------------------------------------------
    system_note = ""
    if game_info.get("released"):
        if game_info["released"] <= today_iso:
            system_note = f"\n\nNote: '{game_info.get('game_name')}' was released on {game_info['released']}."
        else:
            system_note = f"\n\nNote: '{game_info.get('game_name')}' is upcoming — expected {game_info['released']}."

    system_content = AI_PROMPTS['system_prompt'].format(today=today) + system_note

    messages = [{"role": "system", "content": system_content}]

    if game_info:
        messages.append({
            "role":    "system",
            "content": f"Game context: {str(game_info)}",
        })

    for msg in chat_history[-8:]:
        role = "user" if msg.get('role') == 'user' else "assistant"
        messages.append({"role": role, "content": msg.get('content', '')})

    messages.append({"role": "user", "content": prompt})

    # ------------------------------------------------------------------
    # Save user message and stream response
    # ------------------------------------------------------------------
    chat_history.append({'role': 'user', 'content': prompt, 'timestamp': datetime.now().isoformat()})

    st.markdown('<div class="chat-bubble-user">🧑 ' + prompt + '</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        def token_stream():
            stream = groq_client.chat.completions.create(
                model=active_model,
                messages=messages,
                max_tokens=config.groq_max_tokens,
                temperature=config.groq_temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        full_response = st.write_stream(token_stream())

    chat_history.append({
        'role':      'assistant',
        'content':   full_response,
        'timestamp': datetime.now().isoformat(),
    })
    st.session_state[SESSION_KEYS['chat_history']] = chat_history
