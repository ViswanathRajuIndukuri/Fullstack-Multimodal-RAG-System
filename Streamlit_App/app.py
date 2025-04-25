import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = "home"

def initial_home():
    # Set page layout to wide only on the home page
    st.set_page_config(page_title="Multimodal RAG", page_icon="📄", layout="wide")

    # Apply custom CSS to center the content
    st.markdown(
        """
        <style>
        /* Center the main content */
        .main .block-container {
            max-width: 80%;
            padding-top: 1rem; /* Reduced padding */
            padding-left: 5%;
            padding-right: 5%;
            margin-left: auto;
            margin-right: auto;
        }
        /* Style for features list */
        .features {
            font-size: 1rem; /* Reduced from 1.2rem */
            margin-left: 1.5rem; /* Reduced margin */
        }
        .features li {
            margin-bottom: 0.3rem; /* Reduced spacing */
        }
        /* Style for the footer */
        .footer {
            text-align: center;
            font-size: 0.9rem; /* Reduced font size */
            color: #888888;
            margin-top: 1.5rem; /* Reduced margin */
        }
        /* Style for buttons */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            padding: 0.4rem 0.8rem; /* Reduced padding */
            margin: 0.4rem 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Create columns to position the login button at the top right
    col1, col2 = st.columns([8, 1])  # Adjusted column widths

    def go_to_signin():
        st.session_state.page = "signin"

    def logout():
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.page = "home"

    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.session_state.logged_in:
            st.button("🚪 Logout", key="logout_button", on_click=logout)
        else:
            st.button("🔒 Login", key="login_button", on_click=go_to_signin)

    # Display the application information with adjusted font sizes
    if st.session_state.logged_in:
        st.markdown(
            f'<div style="text-align: center; font-size: 2.5rem;">Welcome, {st.session_state.username}!</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center; font-size: 2.5rem;">You are now logged in.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 3.5rem; font-weight: bold;">Research Assistant Using LangGraph</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center; font-size: 2.5rem;">Your AI-powered Research Assistant</div>',
            unsafe_allow_html=True)
        st.write("---")
        st.markdown('''
                <div style="text-align: center;">
                    <div style="margin-bottom: 1rem;">
                        📚 <strong>Document Selection</strong>: Choose from pre-processed documents for research.
                    </div>
                    <div style="margin-bottom: 1rem;">
                        🔬 <strong>Arxiv Agent</strong>: Search and retrieve relevant research papers.
                    </div>
                    <div style="margin-bottom: 1rem;">
                        🌐 <strong>Web Search Agent</strong>: Conduct online research for broader context.
                    </div>
                    <div style="margin-bottom: 1rem;">
                        💡 <strong>RAG Agent</strong>: Answer queries based on document content using Pinecone and Langraph.
                    </div>
                    <div style="margin-bottom: 1rem;">
                        📝 <strong>User Interaction Interface</strong>: Ask questions and interact with research findings.
                    </div>
                    <div style="margin-bottom: 1rem;">
                        📄 <strong>Export Results</strong>: Export findings as professional PDF reports or in Codelabs format.
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        st.write("---")
        st.markdown(
            '<div style="text-align: center; font-size: 2.5rem;">🚀 Get Started</div>',
            unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;">Click the <strong>🔒 Login</strong> button at the top right to sign in or create a new account.</p>', unsafe_allow_html=True)
        st.markdown('<div class="footer">© 2024 Multi-modal RAG. All rights reserved.</div>', unsafe_allow_html=True)

def register():
    # Set default page layout
    st.set_page_config(page_title="Sign Up", page_icon="🔑")

    # Add a "Back" button at the top right to return to the sign-in page
    col1, col2 = st.columns([8, 1.5])  # Adjusted column widths

    with col1:
        st.markdown(
            '<div style="text-align: left; font-size: 3rem; font-weight: bold; margin-top: 1rem; margin-bottom: 1rem;">🔑 Sign Up</div>',
            unsafe_allow_html=True)
    with col2:
        st.button("🔙 Back", on_click=lambda: st.session_state.update(page="signin"))

    # Use unique keys for input fields
    st.write("Please fill in the details below to create a new account.")
    email = st.text_input("📧 Email", key="signup_email")
    username = st.text_input("👤 Username", key="signup_username")
    password = st.text_input("🔒 Password", type="password", key="signup_password")
    password_confirm = st.text_input("🔒 Confirm Password", type="password", key="signup_password_confirm")

    # Define callback functions
    def handle_register():
        if not email or not username or not password or not password_confirm:
            st.warning("⚠️ Please fill in all fields")
        elif password != password_confirm:
            st.warning("⚠️ Passwords do not match")
        else:
            response = requests.post(
                f"{API_URL}/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password
                }
            )
            if response.status_code == 200:
                st.success("🎉 Registration successful! Please sign in.")
                # Clear the input fields
                st.session_state.signup_email = ''
                st.session_state.signup_username = ''
                st.session_state.signup_password = ''
                st.session_state.signup_password_confirm = ''
                st.session_state.page = "signin"
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"❌ Registration failed: {error_detail}")

    # Registration button
    st.button("✅ Register", on_click=handle_register)

def login():
    # Set default page layout
    st.set_page_config(page_title="Sign In", page_icon="🔐")

    # Add a "Back" button at the top right to return to the welcome page
    col1, col2 = st.columns([8, 1.5])  # Adjusted column widths

    with col1:
        st.markdown(
            '<div style="text-align: left; font-size: 3rem; font-weight: bold; margin-top: 1rem; margin-bottom: 1rem;">🔐 Sign In</div>',
            unsafe_allow_html=True)
    with col2:
        st.button("🔙 Back", on_click=lambda: st.session_state.update(page="home"))

    st.write("Please enter your credentials to sign in.")

    # Use unique keys for input fields
    username = st.text_input("👤 Username", key="signin_username")
    password = st.text_input("🔒 Password", type="password", key="signin_password")

    # Define callback functions
    def handle_login():
        if not username or not password:
            st.warning("⚠️ Please enter both username and password")
        else:
            response = requests.post(
                f"{API_URL}/login",
                data={
                    "username": username,
                    "password": password
                }
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.session_state.token = token
                st.session_state.logged_in = True
                st.session_state.username = username
                # Clear the input fields
                st.session_state.signin_username = ''
                st.session_state.signin_password = ''
                st.session_state.page = "home"
                st.success("✅ Logged in successfully!")
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"❌ Login failed: {error_detail}")

    def go_to_signup():
        # Clear the input fields when switching pages
        st.session_state.signin_username = ''
        st.session_state.signin_password = ''
        st.session_state.page = "signup"

    st.button("➡️ Sign In", on_click=handle_login)
    st.write("Don't have an account?")
    st.button("📝 Sign Up", on_click=go_to_signup)

def main():
    if st.session_state.page == "home":
        initial_home()
    elif st.session_state.page == "signin":
        login()
    elif st.session_state.page == "signup":
        register()

if __name__ == "__main__":
    main()