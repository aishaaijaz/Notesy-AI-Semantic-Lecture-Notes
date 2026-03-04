import streamlit as st
import json
import os
import bcrypt
from datetime import datetime
from speech import transcribe_audio
from notes_generator_llama import generate_notes, generate_topic_explanation, viva_chatbot
# from notes_generator import generate_notes, generate_topic_explanation, viva_chatbot
from fpdf import FPDF
import re

# ================= CONFIG =================
st.set_page_config(
    page_title="Notesy AI",
    page_icon="💛",
    layout="wide",
)

HISTORY_FILE = "history.json"
USERS_FILE = "users.json"

# ================= UTIL =================
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def save_to_history(user, section, title, content, extra=None):
    history = load_json(HISTORY_FILE)
    if user not in history:
        history[user] = []
    
    entry = {
        "id": len(history[user]),
        "section": section,
        "title": title,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "extra": extra
    }
    history[user].append(entry)
    save_json(HISTORY_FILE, history)
    return entry["id"]

def get_user_history(user):
    history = load_json(HISTORY_FILE)
    return history.get(user, [])

# ================= AUTH FUNCTIONS =================
def signup(username, password):
    users = load_json(USERS_FILE)
    if username in users:
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users[username] = hashed.decode()
    save_json(USERS_FILE, users)
    return True

def login(username, password):
    users = load_json(USERS_FILE)
    if username not in users:
        return False
    return bcrypt.checkpw(password.encode(), users[username].encode())

# ================= THEME =================
def apply_theme(dark: bool):
    if dark:
        colors = {
            "bg": "#0E1117",
            "card": "#1C1F26",
            "card_hover": "#252932",
            "text": "#EAEAEA",
            "subtext": "#B0B3B8",
            "accent": "#FFB703",
            "accent_light": "#FFC933",
            "button_text": "#000000",
            "border": "#2A2F3A",
            "sidebar_bg": "#161922",
            "input_bg": "#1C1F26",
            "success": "#2ECC71",
            "warning": "#F39C12"
        }
    else:
        colors = {
            "bg": "#F4EDD9",
            "card": "#FFFFFF",
            "card_hover": "#151412",
            "text": "#1A1A2E",
            "subtext": "#555555",
            "accent": "#FF9F1C",
            "accent_light": "#FFB347",
            "button_text": "#FFFFFF",
            "border": "#E0DDD5",
            "sidebar_bg": "#FFF5E6",
            "input_bg": "#FFFFFF",
            "success": "#27AE60",
            "warning": "#E67E22"
        }

    st.markdown(f"""
    <style>
    /* ===== GLOBAL ===== */
    .stApp {{
        background-color: {colors["bg"]};
        color: {colors["text"]};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* ===== HEADERS ===== */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {colors["text"]} !important;
        font-weight: 600;
    }}

    p, span, label, .stMarkdown p {{
        color: {colors["text"]} !important;
    }}

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {{
        background-color: {colors["sidebar_bg"]} !important;
        border-right: 2px solid {colors["border"]};
    }}

    section[data-testid="stSidebar"] .stMarkdown {{
        color: {colors["text"]} !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: {colors["text"]} !important;
    }}

    section[data-testid="stSidebar"] .stButton > button {{
        background-color: {colors["card"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border"]} !important;
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {colors["accent"]} !important;
        color: {colors["button_text"]} !important;
        border-color: {colors["accent"]} !important;
        transform: translateX(5px);
    }}

    /* ===== MAIN BUTTONS ===== */
    .stButton > button {{
        background-color: {colors["accent"]} !important;
        color: {colors["button_text"]} !important;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        border: none !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    .stButton > button:hover {{
        background-color: {colors["accent_light"]} !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["text"]} !important;
        border-radius: 10px;
        border: 2px solid {colors["border"]} !important;
        padding: 0.75rem;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {colors["accent"]} !important;
        box-shadow: 0 0 0 2px {colors["accent"]}33;
    }}

    /* ===== FILE UPLOADER ===== */
    .stFileUploader {{
        border-radius: 12px;
        border: 2px dashed {colors["accent"]} !important;
        padding: 1.5rem;
        background-color: {colors["card"]};
    }}

    .stFileUploader label {{
        color: {colors["text"]} !important;
    }}

    /* ===== CARDS ===== */
    .card {{
        background-color: {colors["card"]};
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid {colors["border"]};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }}

    /* ===== HISTORY ITEM ===== */
    .history-item {{
        background-color: {colors["card"]};
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border-left: 4px solid {colors["accent"]};
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .history-item:hover {{
        background-color: {colors["card_hover"]};
        transform: translateX(3px);
    }}

    .history-title {{
        color: {colors["text"]} !important;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0;
    }}

    .history-meta {{
        color: {colors["subtext"]} !important;
        font-size: 0.75rem;
        margin: 0;
    }}

    /* ===== CHAT ===== */
    .stChatMessage {{
        background-color: {colors["card"]} !important;
        border-radius: 12px;
        border: 1px solid {colors["border"]};
    }}

    /* ===== RADIO ===== */
    .stRadio > div {{
        background-color: {colors["card"]};
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border: 1px solid {colors["border"]};
    }}

    .stRadio label {{
        color: {colors["text"]} !important;
    }}

    /* ===== DIVIDER ===== */
    hr {{
        border-color: {colors["border"]} !important;
    }}

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background-color: {colors["card"]} !important;
        color: {colors["text"]} !important;
        border-radius: 10px;
    }}

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {colors["card"]};
        border-radius: 10px;
        padding: 0.25rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {colors["text"]} !important;
        border-radius: 8px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {colors["accent"]} !important;
        color: {colors["button_text"]} !important;
    }}

    /* ===== ALERTS ===== */
    .stAlert {{
        border-radius: 10px;
    }}

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {{
        background-color: {colors["success"]} !important;
        color: white !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# ================= PDF =================
def clean_markdown(text):
    text = re.sub(r'#+\s', '', text)        # remove headings
    text = re.sub(r'\*\*', '', text)        # remove bold **
    text = re.sub(r'\*', '', text)          # remove *
    text = re.sub(r'- ', '• ', text)        # replace dash bullets
    return text


def generate_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    clean_text = clean_markdown(title + "\n\n" + content)
    clean_text = clean_text.encode("latin-1", "replace").decode("latin-1")

    pdf.multi_cell(0, 8, clean_text)

    filename = "notes.pdf"
    pdf.output(filename)
    return filename

# ================= SESSION STATE INIT =================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Default to dark mode

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

if "user" not in st.session_state:
    st.session_state.user = None

if "show_auth" not in st.session_state:
    st.session_state.show_auth = True

# Store generated content to persist after theme switch
if "generated_notes" not in st.session_state:
    st.session_state.generated_notes = None

if "generated_explanation" not in st.session_state:
    st.session_state.generated_explanation = None

if "current_transcript" not in st.session_state:
    st.session_state.current_transcript = None

if "current_topic" not in st.session_state:
    st.session_state.current_topic = None

if "viva_subject" not in st.session_state:
    st.session_state.viva_subject = ""

if "viewing_history" not in st.session_state:
    st.session_state.viewing_history = None

# ================= APPLY THEME =================
apply_theme(st.session_state.dark_mode)

# ================= NAVBAR =================
col1, col2 = st.columns([8, 1])

with col1:
    st.markdown("## 💛 Notesy AI")

with col2:
    theme_icon = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("---")

# ================= AUTH CHECK =================
if st.session_state.user is None:
    # Landing Page Content
    st.markdown(
        """
        <h1 style='text-align:center; font-size:48px;'>
        Transform Your Lectures Into Structured Intelligence
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align:center; font-size:20px;'>
        Notesy AI converts raw lecture audio or transcripts
        into clean, structured, exam-ready semantic notes.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown(" ")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧠 Semantic Structuring")
        st.write("AI understands context, not just keywords.")

    with col2:
        st.markdown("### ⚡ Instant Notes")
        st.write("From 1-hour lecture → structured notes in seconds.")

    with col3:
        st.markdown("### 🎓 Exam Ready")
        st.write("Revision + Prep Buddy mode built-in.")

    st.markdown("---")

    # Authentication Section
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("### 🔐 Get Started")

        option = st.radio("", ["Login", "Sign Up"], horizontal=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if option == "Sign Up":
            if st.button("Create Account", use_container_width=True):
                if username and password:
                    if signup(username, password):
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ User already exists")
                else:
                    st.warning("⚠️ Please enter username and password")

        if option == "Login":
            if st.button("Login", use_container_width=True):
                if username and password:
                    if login(username, password):
                        st.session_state.user = username
                        st.session_state.show_auth = False
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Please enter username and password")

else:
    # ================= SIDEBAR =================
    st.sidebar.markdown("## 📚 Navigation")

    if st.sidebar.button("🏠 Home"):
        st.session_state.page = "Home"
        st.session_state.viewing_history = None
        st.rerun()

    if st.sidebar.button("📤 Lecture Notes"):
        st.session_state.page = "Upload"
        st.session_state.viewing_history = None
        st.rerun()

    if st.sidebar.button("❓ Ask Topic"):
        st.session_state.page = "Ask"
        st.session_state.viewing_history = None
        st.rerun()

    if st.sidebar.button("🧠 Prep Buddy"):  # Renamed from Viva
        st.session_state.page = "PrepBuddy"
        st.session_state.viewing_history = None
        st.rerun()

    st.sidebar.markdown("---")

        # ================= RECENTLY STUDIED =================
    st.sidebar.markdown("## 📖 Recently Studied")
    
    user_history = get_user_history(st.session_state.user)
    
    # Filter out invalid history items (missing required keys)
    valid_history = [
        h for h in user_history 
        if isinstance(h, dict) and "section" in h and "title" in h and "id" in h
    ]
    
    if valid_history:
        # Group by section
        tabs = st.sidebar.tabs(["📤 Notes", "❓ Topics", "🧠 Prep"])
        
        notes_history = [h for h in valid_history if h.get("section") == "notes"]
        topics_history = [h for h in valid_history if h.get("section") == "topic"]
        prep_history = [h for h in valid_history if h.get("section") == "prep"]
        
        with tabs[0]:
            if notes_history:
                for item in reversed(notes_history[-5:]):
                    title = item.get("title", "Untitled")[:20]
                    if st.button(f"📄 {title}...", key=f"hist_note_{item['id']}", use_container_width=True):
                        st.session_state.viewing_history = item
                        st.session_state.page = "ViewHistory"
                        st.rerun()
            else:
                st.caption("No notes yet")
        
        with tabs[1]:
            if topics_history:
                for item in reversed(topics_history[-5:]):
                    title = item.get("title", "Untitled")[:20]
                    if st.button(f"💡 {title}...", key=f"hist_topic_{item['id']}", use_container_width=True):
                        st.session_state.viewing_history = item
                        st.session_state.page = "ViewHistory"
                        st.rerun()
            else:
                st.caption("No topics yet")
        
        with tabs[2]:
            if prep_history:
                for item in reversed(prep_history[-5:]):
                    title = item.get("title", "Untitled")[:20]
                    if st.button(f"🎯 {title}...", key=f"hist_prep_{item['id']}", use_container_width=True):
                        st.session_state.viewing_history = item
                        st.session_state.page = "ViewHistory"
                        st.rerun()
            else:
                st.caption("No prep sessions yet")
    else:
        st.sidebar.info("Start studying to see history!")


    # ================= PAGE CONTENT =================
    page = st.session_state.page

        # ================= VIEW HISTORY =================
    if page == "ViewHistory" and st.session_state.viewing_history:
        item = st.session_state.viewing_history
        
        section = item.get("section", "unknown")
        title = item.get("title", "Untitled")
        content = item.get("content", "No content available")
        timestamp = item.get("timestamp", "Unknown date")
        
        section_icons = {"notes": "📤", "topic": "❓", "prep": "🧠"}
        section_names = {"notes": "Lecture Notes", "topic": "Topic Explanation", "prep": "Prep Buddy Session"}
        
        st.markdown(f"### {section_icons.get(section, '📄')} {section_names.get(section, 'History')}")
        st.caption(f"📅 {timestamp}")
        
        st.markdown("---")
        
        st.subheader(f"📌 {title}")
        
        if section == "prep":
            # Display chat history
            chat_lines = content.strip().split("\n")
            for line in chat_lines:
                if line.startswith("AI:"):
                    st.chat_message("assistant").write(line[4:])
                elif line.startswith("User:"):
                    st.chat_message("user").write(line[6:])
        else:
            st.markdown(content)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to History"):
                st.session_state.viewing_history = None
                st.session_state.page = "Home"
                st.rerun()
        
        if section == "notes":
            with col2:
                pdf_file = generate_pdf(title, content)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        f,
                        file_name=f"{title[:20]}_notes.pdf"
                    )

        # ================= HOME =================
    elif page == "Home":
        st.title("🏠 Dashboard")
        st.write(f"Welcome back, **{st.session_state.user}**! 👋")

        st.markdown("---")

        # Quick Stats - Fixed with .get() method
        user_history = get_user_history(st.session_state.user)
        
        # Safe counting with .get() to avoid KeyError
        notes_count = len([h for h in user_history if isinstance(h, dict) and h.get("section") == "notes"])
        topics_count = len([h for h in user_history if isinstance(h, dict) and h.get("section") == "topic"])
        prep_count = len([h for h in user_history if isinstance(h, dict) and h.get("section") == "prep"])

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📤 Notes Generated", notes_count)
        with col2:
            st.metric("❓ Topics Explored", topics_count)
        with col3:
            st.metric("🧠 Prep Sessions", prep_count)
        with col4:
            st.metric("📊 Total Activity", notes_count + topics_count + prep_count)

        st.markdown("---")

        st.markdown(
            """
            <h2 style='text-align:center;'>
            What would you like to do today?
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.markdown("")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📤 Lecture Notes")
            st.write("Upload transcripts and generate structured study notes.")
            if st.button("Generate Notes →", key="home_notes"):
                st.session_state.page = "Upload"
                st.rerun()

        with col2:
            st.markdown("### ❓ Ask Topic")
            st.write("Get detailed explanations on any topic instantly.")
            if st.button("Ask Question →", key="home_ask"):
                st.session_state.page = "Ask"
                st.rerun()

        with col3:
            st.markdown("### 🧠 Prep Buddy")
            st.write("Interactive Q&A for exam prep and viva practice.")
            if st.button("Start Prep →", key="home_prep"):
                st.session_state.page = "PrepBuddy"
                st.rerun()

        st.divider()

    # ================= UPLOAD / NOTES =================
    elif page == "Upload":
        st.header("📤 Generate Lecture Notes")
        st.write("Upload your lecture transcript and get structured, exam-ready notes.")

        uploaded_file = st.file_uploader("Upload Transcript File (.txt)", type=["txt"])

        if uploaded_file is not None:
            transcript = uploaded_file.read().decode("utf-8")
            st.session_state.current_transcript = transcript

            st.subheader("📝 Transcript Preview")
            st.text_area("Transcript", transcript, height=200, disabled=True)

            if st.button("✨ Generate Study Notes", use_container_width=True):
                with st.spinner("🔄 Generating structured notes..."):
                    notes = generate_notes(transcript)
                    st.session_state.generated_notes = {
                        "title": uploaded_file.name,
                        "content": notes
                    }
                    # Save to history
                    save_to_history(
                        st.session_state.user,
                        "notes",
                        uploaded_file.name,
                        notes
                    )

        # Display generated notes (persists after theme switch)
        if st.session_state.generated_notes:
            st.markdown("---")
            st.subheader("📚 Generated Notes")
            st.markdown(st.session_state.generated_notes["content"])

            pdf_file = generate_pdf(
                st.session_state.generated_notes["title"],
                st.session_state.generated_notes["content"]
            )

            col1, col2 = st.columns(2)
            with col1:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "⬇️ Download as PDF",
                        f,
                        file_name="lecture_notes.pdf",
                        use_container_width=True
                    )
            with col2:
                if st.button("🗑️ Clear Notes", use_container_width=True):
                    st.session_state.generated_notes = None
                    st.rerun()

    # ================= ASK TOPIC =================
    elif page == "Ask":
        st.header("❓ Ask for Topic Explanation")
        st.write("Enter any topic and get a detailed, easy-to-understand explanation.")

        topic = st.text_input("Enter your topic or question", placeholder="e.g., Explain quantum entanglement")
        st.session_state.current_topic = topic

        if st.button("🔍 Generate Explanation", use_container_width=True) and topic:
            with st.spinner("🔄 Generating explanation..."):
                explanation = generate_topic_explanation(topic)
                st.session_state.generated_explanation = {
                    "topic": topic,
                    "content": explanation
                }
                # Save to history
                save_to_history(
                    st.session_state.user,
                    "topic",
                    topic,
                    explanation
                )

        # Display generated explanation (persists after theme switch)
        if st.session_state.generated_explanation:
            st.markdown("---")
            st.subheader(f"💡 {st.session_state.generated_explanation['topic']}")
            st.markdown(st.session_state.generated_explanation["content"])
            
            if st.button("🗑️ Clear Explanation"):
                st.session_state.generated_explanation = None
                st.rerun()

    # ================= PREP BUDDY (formerly Viva) =================
    elif page == "PrepBuddy":
        st.header("🧠 Prep Buddy")
        st.write("Your AI study companion for exam prep, viva practice, and concept revision.")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        subject = st.text_input(
            "What subject would you like to practice?",
            value=st.session_state.viva_subject,
            placeholder="e.g., Machine Learning, Organic Chemistry, History"
        )

        if subject != st.session_state.viva_subject:
            st.session_state.viva_subject = subject
            st.session_state.chat_messages = []

        if subject:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 New Session"):
                    st.session_state.chat_messages = []
                    st.rerun()

            st.markdown("---")

            # First AI question
            if len(st.session_state.chat_messages) == 0:
                with st.spinner("Preparing your first question..."):
                    ai_response = viva_chatbot(subject)
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": ai_response}
                    )

            # Display chat
            for msg in st.session_state.chat_messages:
                if msg["role"] == "assistant":
                    st.chat_message("assistant", avatar="🧠").write(msg["content"])
                else:
                    st.chat_message("user", avatar="👤").write(msg["content"])

            # User input
            user_input = st.chat_input("Type your answer...")

            if user_input:
                # Add user message
                st.session_state.chat_messages.append(
                    {"role": "user", "content": user_input}
                )

                with st.spinner("Thinking..."):
                    ai_response = viva_chatbot(subject, user_input=user_input)

                # Add AI reply
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": ai_response}
                )

                # Auto-save every 3 user responses
                user_count = sum(
                    1 for msg in st.session_state.chat_messages
                    if msg["role"] == "user"
                )

                if user_count % 3 == 0:
                    save_to_history(
                        st.session_state.user,
                        "prep",
                        f"{subject} Session",
                        st.session_state.chat_messages
                    )

                st.rerun()

            st.markdown("---")
            if st.button("💾 Save This Session"):
                save_to_history(
                    st.session_state.user,
                    "prep",
                    f"{subject} Session",
                    st.session_state.chat_messages
                )
                st.success("✅ Session saved to history!")