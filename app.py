import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import numpy as np

from db import (
    create_user,
    check_login,
    get_user,
    increment_usage,
    set_plan
)

from pdf_report import generate_pdf

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="AI Analyst Pro SaaS", layout="wide")

API_KEY = st.secrets.get("POLLINATIONS_API_KEY", "")

FREE_LIMIT = 20

# =========================
# AUTH SYSTEM
# =========================

st.sidebar.title("🔐 AI SaaS Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

mode = st.sidebar.radio("Mode", ["Login", "Register"])

user = None

if username and password:

    if mode == "Register":
        create_user(username, password)
        st.sidebar.success("Account created")

    if mode == "Login":
        if check_login(username, password):
            st.session_state["user"] = username
            user = username
            st.sidebar.success("Logged in")
        else:
            st.sidebar.error("Invalid credentials")

if "user" in st.session_state:
    user = st.session_state["user"]

if not user:
    st.warning("Please login to continue")
    st.stop()

# =========================
# USER DATA
# =========================

create_user(user, password="")  # safe ignore if exists

user_data = get_user(user)

plan = user_data[2]
usage = user_data[3]

# =========================
# SIDEBAR SAAS PANEL
# =========================

st.sidebar.divider()
st.sidebar.subheader("💰 SaaS Panel")

st.sidebar.write("User:", user)
st.sidebar.write("Plan:", plan)
st.sidebar.write("Usage:", f"{usage}/{FREE_LIMIT}" if plan == "free" else "∞")

if plan == "free":
    if st.sidebar.button("💳 Upgrade to Pro"):
        set_plan(user, "pro")
        st.rerun()

# =========================
# LIMIT CONTROL
# =========================

def can_use():
    return plan == "pro" or usage < FREE_LIMIT

# =========================
# AI ENGINE
# =========================

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

    return "⚠️ AI temporarily unavailable"

def run_ai(prompt):

    if not can_use():
        return "🚫 Free limit reached. Upgrade to Pro."

    increment_usage(user)

    return call_ai(prompt)

# =========================
# UI
# =========================

st.title("🧠 AI Analyst Pro SaaS")
st.caption("Login + AI + CSV + Agent + Dashboard")

task = st.selectbox(
    "Mode",
    ["Single Analysis", "AI Agent Mode", "CSV Dashboard"]
)

input_text = st.text_area("Enter your data")

# =========================
# SINGLE ANALYSIS
# =========================

if task == "Single Analysis":

    if st.button("Run AI") and input_text:

        prompt = f"Analyze:\n{input_text}"

        with st.spinner("Thinking..."):

            result = run_ai(prompt)

        st.subheader("📊 Result")
        st.write(result)

        # PDF EXPORT
        if st.button("📄 Export PDF"):

            file = generate_pdf(result, "report.pdf")

            with open(file, "rb") as f:
                st.download_button("Download Report", f, file_name="report.pdf")

# =========================
# AI AGENT MODE
# =========================

if task == "AI Agent Mode":

    def agent_loop(text, rounds=3):

        output = []

        for i in range(rounds):

            prompt = f"""
You are an AI analyst agent.

Iteration {i+1}
Analyze:
{text}
Improve insights.
"""

            res = run_ai(prompt)
            output.append(res)

            time.sleep(1)

        return "\n\n".join(output)

    if st.button("Run Agent") and input_text:

        result = agent_loop(input_text)

        st.subheader("🧠 Agent Output")
        st.write(result)

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

                prompt = f"Analyze dataset column: {df[col].to_string()}"

                result = run_ai(prompt)

                st.write(result)

                file = generate_pdf(result, "csv_report.pdf")

                with open(file, "rb") as f:
                    st.download_button("Download Report", f, file_name="csv_report.pdf")

# =========================
# FOOTER
# =========================

st.sidebar.divider()
st.sidebar.write("⚡ SaaS Mode Active")
st.sidebar.write("🧠 AI Analyst Pro v3")
