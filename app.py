import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import time

from db import get_user, create_user, increment_usage, set_plan
from auth import login
from pdf_report import generate_pdf

st.set_page_config(page_title="AI Analyst Pro SaaS", layout="wide")

# =========================
# AUTH
# =========================

user = login()

if not user:
    st.warning("Login required")
    st.stop()

create_user(user)

user_data = get_user(user)
plan = user_data[1]
usage = user_data[2]

FREE_LIMIT = 20

# =========================
# SIDEBAR SAAS PANEL
# =========================

st.sidebar.title("💰 SaaS Panel")
st.sidebar.write("User:", user)
st.sidebar.write("Plan:", plan)
st.sidebar.write("Usage:", usage, "/", FREE_LIMIT if plan=="free" else "∞")

if plan == "free":
    if st.sidebar.button("💳 Upgrade Pro"):
        set_plan(user, "pro")
        st.rerun()

# =========================
# LIMIT CONTROL
# =========================

def can_use():
    return plan == "pro" or usage < FREE_LIMIT

# =========================
# AI ENGINE (AGENT MODE)
# =========================

API_KEY = st.secrets.get("POLLINATIONS_API_KEY", "")

def call_ai(prompt):

    try:
        r = requests.post(
            "https://api.pollinations.ai/text",
            json={
                "prompt": prompt,
                "model": "gpt-4o-mini",
                "api_key": API_KEY
            },
            timeout=20
        )

        if r.status_code == 200:
            return r.text
    except:
        pass

    return "AI unavailable"

# =========================
# AGENT MODE ENGINE
# =========================

def ai_agent_loop(data, iterations=2):

    insights = []

    for i in range(iterations):

        prompt = f"""
You are an AI data analyst agent.

Iteration {i+1}

Analyze dataset:
{data}

Improve previous insights and refine understanding.
Return new insights only.
"""

        result = call_ai(prompt)
        insights.append(result)

        time.sleep(1)

    return "\n\n".join(insights)

# =========================
# MAIN UI
# =========================

st.title("🧠 AI Analyst Pro SaaS (Agent + PDF + Dashboard)")
st.caption("Next-gen AI analytics platform")

task = st.selectbox(
    "Mode",
    ["Single Analysis", "AI Agent Mode", "CSV Dashboard"]
)

input_text = st.text_area("Input data")

# =========================
# SINGLE ANALYSIS
# =========================

if task == "Single Analysis":

    if st.button("Run") and input_text:

        if not can_use():
            st.error("Limit reached")
            st.stop()

        increment_usage(user)

        res = call_ai(input_text)

        st.write(res)

        # PDF EXPORT
        if st.button("📄 Export PDF"):

            file = generate_pdf(res, "report.pdf")

            with open(file, "rb") as f:
                st.download_button("Download Report", f, file_name="report.pdf")

# =========================
# AI AGENT MODE
# =========================

if task == "AI Agent Mode":

    if st.button("Run Agent") and input_text:

        if not can_use():
            st.error("Limit reached")
            st.stop()

        increment_usage(user)

        result = ai_agent_loop(input_text, iterations=3)

        st.subheader("🧠 Agent Output")
        st.write(result)

        # PDF EXPORT
        file = generate_pdf(result, "agent_report.pdf")

        with open(file, "rb") as f:
            st.download_button("Download Agent Report", f, file_name="agent_report.pdf")

# =========================
# CSV DASHBOARD
# =========================

if task == "CSV Dashboard":

    file = st.file_uploader("Upload CSV")

    if file:

        df = pd.read_csv(file)

        st.dataframe(df)

        numeric = df.select_dtypes(include=np.number).columns

        if len(numeric) > 0:

            col = st.selectbox("Metric", numeric)

            fig = px.line(df, y=col, title=f"{col} Trend")

            st.plotly_chart(fig)

            if st.button("AI Insight"):

                prompt = f"Analyze this metric: {df[col].to_string()}"

                res = call_ai(prompt)

                st.write(res)

                file = generate_pdf(res, "csv_report.pdf")

                with open(file, "rb") as f:
                    st.download_button("Download Report", f, file_name="csv_report.pdf")

# =========================
# FOOTER
# =========================

st.sidebar.write("⚡ SaaS Mode Active")
