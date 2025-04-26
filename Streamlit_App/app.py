import os
import requests
import streamlit as st
from datetime import datetime, timezone

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ─────────────────────────  PAGE CONFIG & GLOBAL CSS  ─────────────────────────
st.set_page_config(page_title="Multimodal RAG", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
      body            {background:#f7f9fc; font-family:"Trebuchet MS",sans-serif;}
      .block-container{padding-top:2.5rem;}
      h1,h2,h3,h4     {color:#003366;}
      .stButton>button{background:#003366;border:none;color:white;
                       padding:0.5rem 1.1rem;border-radius:4px;font-size:0.9rem;}
      .stButton>button:hover{background:#00509e;}
      .chat-bubble    {padding:0.6rem 0.9rem;border-radius:12px;margin-bottom:0.5rem;
                       max-width:80%;word-wrap:break-word;}
      .user-bubble    {background:#00509e;color:white;margin-left:auto;}
      .ai-bubble      {background:#e1ecf7;color:#000;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────  SESSION DEFAULTS  ────────────────────────────────
_defaults = {
    "logged_in": False,
    "token": None,
    "username": None,
    "page": "home",          # home | signin | signup | chat
    "indexes": [],
    "selected_index": None,
    "chat_history": [],
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────  HELPERS  ─────────────────────────────────────────
def _rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.rerun()

def _reset_session():
    st.session_state.update({
        "logged_in": False,
        "token": None,
        "username": None,
        "indexes": [],
        "selected_index": None,
        "chat_history": [],
    })

def _auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def _handle_401(resp: requests.Response):
    if resp.status_code == 401:
        st.warning("Session expired – please log in again.")
        _reset_session(); st.session_state.page = "signin"; _rerun()

# ─────────────────────────  PUBLIC HOME  ─────────────────────────────────────
def public_home():
    st.markdown('<h1 style="text-align:center;">Multimodal Retrieval-Augmented Generation System</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center;">Your AI-powered Multimodal RAG Assistant</h3>', unsafe_allow_html=True)
    st.write("---")
    st.markdown(
        """
        <div style="text-align:center;font-size:1.1rem;">
          📚 <b>Document Selection</b>  |  💡 <b>Multimodal&nbsp;RAG</b>  |
          📝 <b>Interactive&nbsp;Q/A</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("---")
    st.markdown('<div style="text-align:center;font-size:1.5rem;">🚀 Click <b>🔒 Login</b> to get started</div>', unsafe_allow_html=True)

# ─────────────────────────  CHAT UTILITIES  ─────────────────────────────────-
def _load_indexes():
    resp = requests.get(f"{API_URL}/indexes", headers=_auth_headers())
    _handle_401(resp)
    if resp.ok:
        st.session_state.indexes = resp.json().get("indexes", [])
        if st.session_state.indexes and st.session_state.selected_index not in st.session_state.indexes:
            st.session_state.selected_index = st.session_state.indexes[0]
    else:
        st.error(resp.json().get("detail", resp.text))

# ─────────────────────────  CHAT PAGE  ───────────────────────────────────────
def chat_page():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {st.session_state.username}")
        if st.button("🚪 Logout"):
            _reset_session(); st.session_state.page = "home"; _rerun()

        st.write("---")
        if st.button("🔄 Refresh Indexes") or not st.session_state.indexes:
            _load_indexes()

        if st.session_state.indexes:
            st.session_state.selected_index = st.selectbox(
                "📂 Index",
                st.session_state.indexes,
                index=st.session_state.indexes.index(st.session_state.selected_index)
                if st.session_state.selected_index in st.session_state.indexes else 0,
            )
        else:
            st.info("No indexes available.")

    # Main area
    st.markdown("<h2>💬 Chat with your documents</h2>", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        cls = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="chat-bubble {cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    query = st.chat_input("Ask something…")
    if query and st.session_state.selected_index:
        now = datetime.now(timezone.utc).isoformat()
        st.session_state.chat_history.append({"role": "user", "content": query, "timestamp": now})
        st.markdown(f'<div class="chat-bubble user-bubble">{query}</div>', unsafe_allow_html=True)

        # Show spinner while waiting for backend
        with st.spinner("Generating answer…"):
            payload = {"question": query, "top_k": 5}
            resp = requests.post(
                f"{API_URL}/qa/{st.session_state.selected_index}",
                json=payload,
                headers=_auth_headers(),
            )
            _handle_401(resp)
            answer = resp.json().get("answer", "<no answer>") if resp.ok else f"Error: {resp.text}"

        now = datetime.now(timezone.utc).isoformat()
        st.session_state.chat_history.append({"role": "assistant", "content": answer, "timestamp": now})
        st.markdown(f'<div class="chat-bubble ai-bubble">{answer}</div>', unsafe_allow_html=True)

# ─────────────────────────  SIGN IN / SIGN UP  ───────────────────────────────
def signin_page():
    st.markdown("<h2>🔐 Sign In</h2>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("➡️ Sign In"):
        if not username or not password:
            st.warning("Enter both username and password."); return
        resp = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
        if resp.ok:
            st.session_state.update({
                "token": resp.json()["access_token"],
                "logged_in": True,
                "username": username,
                "page": "chat",
                "chat_history": [],
                "indexes": [],
                "selected_index": None,
            }); _rerun()
        else:
            st.error(resp.json().get("detail", resp.text))

    st.write("Don't have an account?")
    if st.button("📝 Sign Up"):
        st.session_state.page = "signup"; _rerun()
    if st.button("🔙 Back"):
        st.session_state.page = "home"; _rerun()

def signup_page():
    st.markdown("<h2>🔑 Sign Up</h2>", unsafe_allow_html=True)
    email    = st.text_input("📧 Email")
    username = st.text_input("👤 Username")
    pwd1     = st.text_input("🔒 Password", type="password")
    pwd2     = st.text_input("🔒 Confirm Password", type="password")

    if st.button("✅ Register"):
        if not all([email, username, pwd1, pwd2]):
            st.warning("Fill in all fields."); return
        if pwd1 != pwd2:
            st.warning("Passwords do not match."); return
        resp = requests.post(f"{API_URL}/register", json={"email": email, "username": username, "password": pwd1})
        if resp.ok:
            st.success("Registered – please log in."); st.session_state.page = "signin"; _rerun()
        else:
            st.error(resp.json().get("detail", resp.text))

    if st.button("🔙 Back"):
        st.session_state.page = "signin"; _rerun()

# ─────────────────────────  ROUTER  ──────────────────────────────────────────
def main():
    if st.session_state.page == "home":
        col1, col2 = st.columns([8,1])
        with col2:
            if st.session_state.logged_in:
                if st.button("🚪 Logout"): _reset_session(); _rerun()
            else:
                if st.button("🔒 Login"): st.session_state.page = "signin"; _rerun()
        public_home()

    elif st.session_state.page == "signin":
        signin_page()

    elif st.session_state.page == "signup":
        signup_page()

    elif st.session_state.page == "chat":
        if not st.session_state.logged_in:
            st.session_state.page = "signin"; _rerun()
        chat_page()

    else:
        st.error("Unknown page")

if __name__ == "__main__":
    main()