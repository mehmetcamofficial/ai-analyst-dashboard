import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

from db import create_user, check_login, get_user, increment_usage, set_plan

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Analyst Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# BACKGROUND UI (MODERN)
# =========================

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1557682250-33bd709cbe85");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.main {
    background-color: rgba(0,0,0,0.65);
    padding: 20px;
    border-radius: 20px;
}

div.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, p {
    color: white !important;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# =========================
# SESSION INIT
# =========================

if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN UI (MODERN CARD)
# =========================

st.title("🧠 AI Analyst Pro SaaS")

st.markdown("### Login / Register")

col1, col2 = st.columns(2)

with col1:
    username = st.text_input("Username")

with col2:
    password = st.text_input("Password", type="password")

mode = st.radio("Mode", ["Login", "Register"])

if st.button("Continue"):

    if username and password:

        if mode == "Register":
            create_user(username, password)
            st.success("Account created! Now login.")

        elif mode == "Login":
            if check_login(username, password):
                st.session_state.user = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# =========================
# BLOCK IF NOT LOGGED IN
# =========================

if not st.session_state.user:
    st.stop()

user = st.session_state.user

# =========================
# USER DATA
# =========================

user_data = get_user(user)

plan = user_data[2]
usage = user_data[3]

FREE_LIMIT = 20

# =========================
# SIDEBAR (SAAS PANEL)
# =========================

st.sidebar.title("💰 AI SaaS Panel")

st.sidebar.markdown(f"""
👤 **User:** {user}  
📦 **Plan:** {plan}  
📊 **Usage:** {usage}/{FREE_LIMIT if plan=='free' else '∞'}
""")

if plan == "free":
    if st.sidebar.button("⚡ Upgrade to Pro"):
        set_plan(user, "pro")
        st.rerun()

st.sidebar.divider()

# =========================
# LIMIT CONTROL
# =========================

def can_use():
    return plan == "pro" or usage < FREE_LIMIT

# =========================
# AI ENGINE (SAFE MOCK)
# =========================

def call_ai(prompt):
    try:
        r = requests.post(
            "https://text.pollinations.ai/",
            json={"prompt": prompt},
            timeout=30
        )
        if r.status_code == 200:
            return r.text
    except:
        pass

    return "⚠️ AI service temporarily unavailable"

def run_ai(prompt):

    if not can_use():
        return "🚫 Free limit reached. Upgrade to Pro."

    increment_usage(user)

    return call_ai(prompt)

# =========================
# MAIN DASHBOARD
# =========================

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🧠 AI Analyst", "📊 CSV Dashboard", "📄 Reports"])

# =========================
# TAB 1 - AI ANALYST
# =========================

with tab1:

    st.subheader("AI Analysis Engine")

    input_text = st.text_area("Enter your data / question", height=150)

    if st.button("🚀 Run AI Analysis") and input_text:

        with st.spinner("Analyzing..."):

            prompt = f"Analyze this professionally:\n{input_text}"

            result = run_ai(prompt)

        st.success("Done")

        st.markdown("### 📊 Result")
        st.write(result)

# =========================
# TAB 2 - CSV DASHBOARD
# =========================

with tab2:

    st.subheader("📊 Data Dashboard")

    file = st.file_uploader("Upload CSV")

    if file:

        df = pd.read_csv(file)

        st.dataframe(df)

        numeric = df.select_dtypes(include=np.number).columns

        if len(numeric) > 0:

            col = st.selectbox("Select metric", numeric)

            st.line_chart(df[col])

            if st.button("🧠 AI Insight"):

                prompt = f"Analyze this dataset column:\n{df[col].to_string()}"

                result = run_ai(prompt)

                st.write(result)

# =========================
# TAB 3 - REPORTS
# =========================

with tab3:

    st.subheader("📄 Auto Reports")

    text = st.text_area("Generate report from data")

    if st.button("Generate Report") and text:

        prompt = f"""
Create a professional business report:

{text}
"""

        report = run_ai(prompt)

        st.markdown("### Report")
        st.write(report)

# =========================
# FOOTER
# =========================

st.markdown("---")
st.caption("🧠 AI Analyst Pro SaaS • Modern Dashboard UI")
