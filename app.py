import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

from db import (
    create_user,
    check_login,
    get_user,
    increment_usage,
    set_plan
)

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="AI Analyst Pro SaaS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# UI THEME (MODERN GLASS)
# =========================

st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: url("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* DARK OVERLAY */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(10, 12, 20, 0.78);
}

/* CONTENT */
.block-container {
    position: relative;
    z-index: 2;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: rgba(10, 12, 20, 0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* TEXT */
h1,h2,h3,p,label {
    color: white !important;
}

/* INPUTS */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.08);
    color: white;
    border-radius: 10px;
}

/* BUTTONS */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem;
    font-weight: 600;
}

.stButton > button:hover {
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# =========================
# AUTH (SIDEBAR)
# =========================

st.sidebar.title("🧠 AI SaaS Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

mode = st.sidebar.radio("Mode", ["Login", "Register"])

login_btn = st.sidebar.button("Continue")

user = None

if login_btn:

    if username and password:

        if mode == "Register":
            create_user(username, password)
            st.sidebar.success("Account created")

        elif mode == "Login":
            if check_login(username, password):
                st.session_state["user"] = username
                st.sidebar.success("Login success")
            else:
                st.sidebar.error("Invalid credentials")

if "user" in st.session_state:
    user = st.session_state["user"]

if not user:
    st.stop()

# =========================
# USER DATA
# =========================

user_data = get_user(user)

if not user_data:
    st.error("User not found")
    st.stop()

plan = user_data[2]
usage = user_data[3]

FREE_LIMIT = 20

# =========================
# SIDEBAR SAAS PANEL
# =========================

st.sidebar.markdown("---")

st.sidebar.write("👤 User:", user)
st.sidebar.write("📦 Plan:", plan)
st.sidebar.write("📊 Usage:", f"{usage}/{FREE_LIMIT}" if plan=="free" else "∞")

if plan == "free":
    if st.sidebar.button("⚡ Upgrade Pro"):
        set_plan(user, "pro")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("AI Analyst Pro SaaS")

# =========================
# LIMIT CONTROL
# =========================

def can_use():
    return plan == "pro" or usage < FREE_LIMIT

# =========================
# AI ENGINE (STABLE FALLBACK)
# =========================

def call_ai(prompt):

    endpoints = [
        "https://text.pollinations.ai/",
        "https://api.pollinations.ai/text"
    ]

    for url in endpoints:

        try:
            r = requests.get(
                url,
                params={"prompt": prompt},
                timeout=45
            )

            if r.status_code == 200 and r.text:
                return r.text

        except:
            continue

    return "⚠️ AI service temporarily unavailable"

def run_ai(prompt):

    if not can_use():
        return "🚫 Free limit reached. Upgrade Pro."

    increment_usage(user)

    return call_ai(prompt)

# =========================
# HEADER
# =========================

st.title("🧠 AI Analyst Pro SaaS")
st.caption("Modern AI Dashboard • Analytics • Reports")

st.markdown("---")

# =========================
# TABS
# =========================

tab1, tab2, tab3 = st.tabs(["🧠 AI ANALYST", "📊 DASHBOARD", "📄 REPORTS"])

# =========================
# TAB 1 - AI
# =========================

with tab1:

    st.subheader("AI Analysis Engine")

    text = st.text_area("Enter your data / question", height=150)

    if st.button("🚀 Run AI") and text:

        with st.spinner("Analyzing..."):

            result = run_ai(f"Analyze professionally:\n{text}")

        st.success("Done")

        st.write(result)

# =========================
# TAB 2 - CSV
# =========================

with tab2:

    st.subheader("Data Dashboard")

    file = st.file_uploader("Upload CSV")

    if file:

        df = pd.read_csv(file)

        st.dataframe(df)

        numeric = df.select_dtypes(include=np.number).columns

        if len(numeric) > 0:

            col = st.selectbox("Metric", numeric)

            st.line_chart(df[col])

            if st.button("🧠 AI Insight"):

                result = run_ai(df[col].to_string())

                st.write(result)

# =========================
# TAB 3 - REPORTS
# =========================

with tab3:

    st.subheader("Auto Reports")

    text = st.text_area("Generate report")

    if st.button("Generate Report"):

        report = run_ai(f"Create business report:\n{text}")

        st.write(report)
