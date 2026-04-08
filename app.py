import streamlit as st
import anthropic
import json
import re
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MemoryOS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

  .stApp { background: #080b10; color: #e8edf5; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
  }
  [data-testid="stSidebar"] * { color: #e8edf5 !important; }

  /* Main area */
  .main .block-container { padding-top: 1.5rem; max-width: 860px; }

  /* Chat bubbles */
  .user-bubble {
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 16px 4px 16px 16px;
    padding: 12px 16px; margin: 6px 0 6px 60px;
    font-size: 15px; line-height: 1.7; color: #e8edf5;
  }
  .ai-bubble {
    background: #111820;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px 16px 16px 16px;
    padding: 12px 16px; margin: 6px 60px 6px 0;
    font-size: 15px; line-height: 1.7; color: #e8edf5;
  }
  .mem-ref {
    background: rgba(126,232,162,0.06);
    border: 1px solid rgba(126,232,162,0.2);
    border-radius: 6px; padding: 6px 12px;
    margin-top: 8px; font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #7ee8a2;
  }
  .msg-label {
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
    color: #5a6478; margin-bottom: 2px; letter-spacing: 0.1em;
  }

  /* Memory cards */
  .mem-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 10px 12px;
    margin: 5px 0; font-size: 12px;
    color: #8892a4; line-height: 1.55;
    position: relative;
  }
  .mem-card-s { border-left: 2px solid #38bdf8; }
  .mem-card-e { border-left: 2px solid #c084fc; }
  .mem-card-b { border-left: 2px solid #7ee8a2; background: rgba(126,232,162,0.04); border-color: rgba(126,232,162,0.15); }
  .belief-key {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: #7ee8a2;
    font-weight: 600; margin-bottom: 3px;
  }
  .mem-time { font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #5a6478; margin-top: 3px; }

  /* Layer headers */
  .layer-header {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;
  }
  .layer-title { font-size: 12px; font-weight: 600; color: #e8edf5; }
  .layer-count { font-size: 10px; font-family: 'JetBrains Mono', monospace; color: #5a6478; }

  /* Logo */
  .logo-section {
    text-align: center; padding: 16px 0 20px;
    border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 20px;
  }
  .logo-title { font-size: 18px; font-weight: 700; letter-spacing: 0.12em; color: #e8edf5; }
  .logo-sub   { font-size: 9px; font-family: 'JetBrains Mono', monospace; color: #5a6478; letter-spacing: 0.15em; margin-top: 2px; }

  /* Stats pills */
  .stats-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
  .stat-pill {
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
    border: 1px solid rgba(255,255,255,0.1); border-radius: 99px;
    padding: 4px 12px; color: #8892a4;
  }

  /* Input area */
  .stTextArea textarea {
    background: #111820 !important; color: #e8edf5 !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: 10px !important; font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
  }
  .stTextArea textarea:focus {
    border-color: rgba(56,189,248,0.4) !important;
    box-shadow: none !important;
  }
  .stButton button {
    background: linear-gradient(135deg, #38bdf8, #c084fc) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'Syne', sans-serif !important;
    width: 100%;
  }
  .stButton button:hover { opacity: 0.88 !important; }

  /* Welcome */
  .welcome-box {
    text-align: center; padding: 48px 20px;
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: 16px; margin: 20px 0;
  }
  .welcome-box h1 { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
  .welcome-box p  { color: #8892a4; font-size: 14px; line-height: 1.75; max-width: 400px; margin: 0 auto; }
  .grad { background: linear-gradient(90deg,#7ee8a2,#38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

  /* Divider */
  hr { border-color: rgba(255,255,255,0.06) !important; }

  /* Hide streamlit default elements */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = {
        "sensory":      [],   # last 5 messages
        "episodic":     [],   # key events
        "semantic":     {},   # learned beliefs
        "all_messages": []    # full history for API
    }
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []   # {role, text, mem_ref}
if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# ── Helper functions ───────────────────────────────────────────────────────
def build_system_prompt():
    mem = st.session_state.memory
    beliefs = "\n".join(f"- {k}: {v}" for k, v in mem["semantic"].items()) or "none yet"
    episodes = "\n".join(f"- [{e['timestamp']}] {e['summary']}" for e in mem["episodic"][-5:]) or "none yet"
    return f"""You are MemoryOS — an AI with a 3-layer cognitive memory architecture based on the
Atkinson-Shiffrin memory model from cognitive psychology. You genuinely remember this user.

━━━━━━━━━━━━━━━━━━━━
YOUR CURRENT MEMORY
━━━━━━━━━━━━━━━━━━━━

SEMANTIC BELIEFS (what you've learned about this user):
{beliefs}

EPISODIC MEMORY (key past moments):
{episodes}

━━━━━━━━━━━━━━━━━━━━
BEHAVIOR
━━━━━━━━━━━━━━━━━━━━
- Reference past memories naturally when relevant
- Adapt your tone to their expertise level
- You are NOT meeting this person fresh — you know them

━━━━━━━━━━━━━━━━━━━━
MEMORY UPDATE
━━━━━━━━━━━━━━━━━━━━
After your reply, ALWAYS append:

<MEMORY_UPDATE>
{{
  "episodic": "one sentence summary of this exchange, or null",
  "beliefs": {{ "belief_key": "value" }}
}}
</MEMORY_UPDATE>

Only include NEW or CHANGED beliefs. Use snake_case keys like:
preferred_topics, communication_style, expertise_level, goals, personality_traits, current_project, location"""


def parse_memory_update(raw_text):
    pattern = r"<MEMORY_UPDATE>(.*?)</MEMORY_UPDATE>"
    match = re.search(pattern, raw_text, re.DOTALL)
    clean = re.sub(pattern, "", raw_text, flags=re.DOTALL).strip()
    if not match:
        return clean, None
    try:
        return clean, json.loads(match.group(1).strip())
    except:
        return clean, None


def apply_memory_update(user_text, ai_text, update):
    mem = st.session_state.memory
    now = datetime.now().strftime("%H:%M")

    # Layer 1 — Sensory
    mem["sensory"].append({"role": "user",      "content": user_text, "time": now})
    mem["sensory"].append({"role": "assistant", "content": ai_text,   "time": now})
    mem["sensory"] = mem["sensory"][-5:]

    if update:
        # Layer 2 — Episodic
        if update.get("episodic"):
            mem["episodic"].append({"summary": update["episodic"], "timestamp": now})
        # Layer 3 — Semantic
        if update.get("beliefs"):
            mem["semantic"].update(update["beliefs"])


def get_ai_response(user_message):
    mem = st.session_state.memory
    mem["all_messages"].append({"role": "user", "content": user_message})

    api_key = st.session_state.api_key or st.secrets.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=build_system_prompt(),
        messages=mem["all_messages"][-20:]
    )
    raw = response.content[0].text
    mem["all_messages"].append({"role": "assistant", "content": raw})
    return raw


# ── SIDEBAR — Memory Layers ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-section">
      <div class="logo-title">🧠 MEMORY OS</div>
      <div class="logo-sub">ATKINSON-SHIFFRIN MODEL</div>
    </div>
    """, unsafe_allow_html=True)

    # API Key input
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        value=st.session_state.api_key,
        help="Get your key free at console.anthropic.com"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.markdown("---")

    mem = st.session_state.memory

    # Stats
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-pill">⚡ {len(mem['sensory'])} sensory</div>
      <div class="stat-pill">💜 {len(mem['episodic'])} episodic</div>
      <div class="stat-pill">🧠 {len(mem['semantic'])} beliefs</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layer 1: Sensory ──
    st.markdown(f"""
    <div class="layer-header">
      <div class="layer-title">⚡ Sensory Buffer</div>
      <div class="layer-count">{len(mem['sensory'])}/5</div>
    </div>
    """, unsafe_allow_html=True)

    if mem["sensory"]:
        for m in reversed(mem["sensory"]):
            icon = "👤" if m["role"] == "user" else "🤖"
            preview = m["content"][:70] + ("…" if len(m["content"]) > 70 else "")
            st.markdown(f"""
            <div class="mem-card mem-card-s">
              {icon} {preview}
              <div class="mem-time">{m['time']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:#5a6478;font-family:monospace;padding:4px 8px">// last 5 messages</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Layer 2: Episodic ──
    st.markdown(f"""
    <div class="layer-header">
      <div class="layer-title">💜 Episodic Memory</div>
      <div class="layer-count">{len(mem['episodic'])} events</div>
    </div>
    """, unsafe_allow_html=True)

    if mem["episodic"]:
        for e in reversed(mem["episodic"][-5:]):
            st.markdown(f"""
            <div class="mem-card mem-card-e">
              {e['summary']}
              <div class="mem-time">{e['timestamp']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:#5a6478;font-family:monospace;padding:4px 8px">// key moments stored here</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Layer 3: Semantic ──
    st.markdown(f"""
    <div class="layer-header">
      <div class="layer-title">🧠 Semantic Beliefs</div>
      <div class="layer-count">{len(mem['semantic'])} beliefs</div>
    </div>
    """, unsafe_allow_html=True)

    if mem["semantic"]:
        for k, v in mem["semantic"].items():
            st.markdown(f"""
            <div class="mem-card mem-card-b">
              <div class="belief-key">{k}</div>
              {v}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:11px;color:#5a6478;font-family:monospace;padding:4px 8px">// evolving model of you</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑 Reset Memory", use_container_width=True):
        st.session_state.memory = {
            "sensory": [], "episodic": [], "semantic": [], "all_messages": []
        }
        st.session_state.chat_display = []
        st.rerun()


# ── MAIN CHAT AREA ─────────────────────────────────────────────────────────
if not st.session_state.chat_display:
    st.markdown("""
    <div class="welcome-box">
      <h1>Hello, I'm <span class="grad">MemoryOS</span></h1>
      <p>I remember you — not just this conversation, but across all of them.
         I build a cognitive model of <em>how you think</em>, not just what you say.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_display:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-label" style="text-align:right">YOU</div>
            <div class="user-bubble">{msg["text"]}</div>
            """, unsafe_allow_html=True)
        else:
            mem_ref_html = ""
            if msg.get("mem_ref"):
                mem_ref_html = f'<div class="mem-ref">⟲ {msg["mem_ref"]}</div>'
            st.markdown(f"""
            <div class="msg-label">MEMORY OS</div>
            <div class="ai-bubble">{msg["text"].replace(chr(10), "<br>")}{mem_ref_html}</div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_area(
            label="message",
            placeholder="Talk to MemoryOS… (Enter to send)",
            label_visibility="collapsed",
            height=80,
            key="user_input"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Send ➤", use_container_width=True)

# ── Send logic ─────────────────────────────────────────────────────────────
if send and user_input.strip():
    api_key = st.session_state.api_key or st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar first.")
        st.stop()

    st.session_state.chat_display.append({"role": "user", "text": user_input.strip()})

    with st.spinner("Scanning memory layers…"):
        try:
            raw_reply = get_ai_response(user_input.strip())
            clean_reply, update = parse_memory_update(raw_reply)
            apply_memory_update(user_input.strip(), clean_reply, update)

            mem_ref = None
            if update and update.get("beliefs"):
                keys = list(update["beliefs"].keys())
                mem_ref = f"updated beliefs: {', '.join(keys)}"

            st.session_state.chat_display.append({
                "role": "ai",
                "text": clean_reply,
                "mem_ref": mem_ref
            })
        except Exception as e:
            st.error(f"⚠️ API Error: {str(e)}")

    st.rerun()
