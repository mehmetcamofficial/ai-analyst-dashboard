import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

from db import get_user, increment_usage, set_plan
from auth import login_system
from pdf_report import generate_pdf

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Analyst Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# BACKGROUND + GLASS UI
# =========================

st.markdown("""
<style>

/* FULL BACKGROUND */
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
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(10, 12, 20, 0.75);
    z-index: 0;
}

/* MAIN CONTAINER */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    position: relative;
    z-index: 2;
}

/* GLASS CARD */
.glass {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* TEXT */
h1, h2, h3, p, label {
    color: white !important;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #6a11cb, #2575fc);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem 1rem;
}

.stButton > button:hover {
    transform: scale(1.02);
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================

user = login_system()

if not user:
    st.stop()

user_data = get_user(user)

plan = user_data[2]
usage = user_data[3]

FREE_LIMIT = 20

# =========================
# AI ENGINE
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

    return "⚠️ AI temporarily unavailable"

def run_ai(prompt):

    if plan == "free" and usage >= FREE_LIMIT:
        return "🚫 Limit reached. Upgrade Pro."

    increment_usage(user)

    return call_ai(prompt)

# =========================
# HEADER
# =========================

st.markdown("<h1 style='text-align:center;'>🧠 AI Analyst Pro SaaS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Modern AI Dashboard • Analytics • Reports • Agent Mode</p>", unsafe_allow_html=True)

st.markdown("---")

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("### 💰 SaaS Panel")

st.sidebar.write("👤 User:", user)
st.sidebar.write("📦 Plan:", plan)
st.sidebar.write("📊 Usage:", f"{usage}/{FREE_LIMIT if plan=='free' else '∞'}")

if plan == "free":
    if st.sidebar.button("⚡ Upgrade Pro"):
        set_plan(user, "pro")
        st.rerun()

# =========================
# TABS
# =========================

tab1, tab2, tab3 = st.tabs(["🧠 AI ANALYST", "📊 DASHBOARD", "📄 REPORTS"])

# =========================
# TAB 1
# =========================

with tab1:

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.subheader("AI Analysis Engine")

    text = st.text_area("Enter your data / question", height=150)

    if st.button("🚀 Run AI") and text:

        with st.spinner("Analyzing..."):

            result = run_ai(f"Analyze professionally:\n{text}")

        st.success("Done")

        st.write(result)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TAB 2
# =========================

with tab2:

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.subheader("📊 Data Dashboard")

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

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TAB 3
# =========================

with tab3:

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.subheader("📄 Smart Reports")

    text = st.text_area("Generate business report")

    if st.button("Generate Report"):

        report = run_ai(f"Create professional report:\n{text}")

        st.write(report)

    st.markdown('</div>', unsafe_allow_html=True)
