import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import time

from db import (
    get_user,
    increment_usage,
    set_plan
)

from auth import login_system
from pdf_report import generate_pdf

# =========================
# PAGE CONFIG
# =========================

st.set_page_config("AI Analyst SaaS", layout="wide")

# =========================
# LOGIN
# =========================

user = login_system()

if not user:
    st.stop()

user_data = get_user(user)

if not user_data:
    st.error("User not found")
    st.stop()

plan = user_data[2]
usage = user_data[3]

FREE_LIMIT = 20

# =========================
# LIMIT CHECK
# =========================

def can_use():
    return plan == "pro" or usage < FREE_LIMIT

# =========================
# AI ENGINE (SAFE)
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

    return "⚠️ AI unavailable"

def run_ai(prompt):

    if not can_use():
        return "🚫 Limit reached. Upgrade to Pro."

    increment_usage(user)

    return call_ai(prompt)

# =========================
# UI HEADER
# =========================

st.title("🧠 AI Analyst SaaS Pro")
st.caption("Clean, stable, production-ready SaaS architecture")

# =========================
# SIDEBAR
# =========================

st.sidebar.title("💰 SaaS Panel")

st.sidebar.write("User:", user)
st.sidebar.write("Plan:", plan)
st.sidebar.write("Usage:", f"{usage}/{FREE_LIMIT}" if plan=="free" else "∞")

if plan == "free":
    if st.sidebar.button("Upgrade Pro"):
        set_plan(user, "pro")
        st.rerun()

# =========================
# TABS
# =========================

tab1, tab2, tab3 = st.tabs(["🧠 AI", "📊 CSV", "📄 Reports"])

# =========================
# TAB 1 - AI
# =========================

with tab1:

    text = st.text_area("Enter data")

    if st.button("Run AI") and text:

        result = run_ai(f"Analyze:\n{text}")

        st.write(result)

        if st.button("Download PDF"):

            file = generate_pdf(result)

            with open(file, "rb") as f:
                st.download_button("Download", f, file_name="report.pdf")

# =========================
# TAB 2 - CSV
# =========================

with tab2:

    file = st.file_uploader("Upload CSV")

    if file:

        df = pd.read_csv(file)

        st.dataframe(df)

        numeric = df.select_dtypes(include=np.number).columns

        if len(numeric) > 0:

            col = st.selectbox("Metric", numeric)

            st.line_chart(df[col])

            if st.button("AI Insight"):

                result = run_ai(f"Analyze column:\n{df[col].to_string()}")

                st.write(result)

# =========================
# TAB 3 - REPORTS
# =========================

with tab3:

    text = st.text_area("Generate report")

    if st.button("Generate"):

        report = run_ai(f"Create report:\n{text}")

        st.write(report)

        file = generate_pdf(report)

        with open(file, "rb") as f:
            st.download_button("Download Report", f, file_name="report.pdf")
