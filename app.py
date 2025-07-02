import streamlit as st
import pandas as pd
import datetime
import os
import openai

# ✅ Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Data file
DATA_FILE = "job_applications.csv"

# Initialize CSV
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Job Title", "Company", "Application Date", "Platform",
        "Status", "Follow-Up Date", "Notes"
    ]).to_csv(DATA_FILE, index=False)

# Load data
df = pd.read_csv(DATA_FILE)

# Sidebar navigation
st.sidebar.title("JobHound AI 🐾")
menu = st.sidebar.radio("Navigate", ["Dashboard", "Add Job", "AI Resume Match", "AI Cover Letter", "View Jobs"])

# Dashboard
if menu == "Dashboard":
    st.title("📊 Job Application Dashboard")
    st.metric("Total Applications", len(df))
    st.metric("Interviews", len(df[df["Status"] == "Interviewing"]))
    st.metric("Offers", len(df[df["Status"] == "Offer"]))
    st.bar_chart(df["Status"].value_counts())

# Add Job Form
elif menu == "Add Job":
    st.title("➕ Add a New Application")
    with st.form("job_form"):
        job_title = st.text_input("Job Title")
        company = st.text_input("Company")
        app_date = st.date_input("Application Date", datetime.date.today())
        platform = st.selectbox("Platform", ["LinkedIn", "Indeed", "Company Site", "Other"])
        status = st.selectbox("Status", ["Applied", "Interviewing", "Offer", "Rejected", "Ghosted"])
        follow_up = st.date_input("Follow-Up Date", app_date + datetime.timedelta(days=7))
        notes = st.text_area("Notes")

        if st.form_submit_button("Submit"):
            new_row = {
                "Job Title": job_title, "Company": company, "Application Date": app_date,
                "Platform": platform, "Status": status, "Follow-Up Date": follow_up, "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Added job at **{company}**")

# AI Resume Matching
elif menu == "AI Resume Match":
    st.title("🤖 AI Resume Match Score")
    with st.form("match_form"):
        resume = st.text_area("Paste Your Resume")
        job_desc = st.text_area("Paste Job Description")
        if st.form_submit_button("Get Match Score"):
            with st.spinner("Analyzing..."):
                prompt = f"""
You're an expert resume evaluator. Given the resume and job description below, rate the match from 0 to 100, and explain why.

Resume:
{resume}

Job Description:
{job_desc}

Return only a score and a short explanation.
"""
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                )
                st.success("Match Score:")
                st.write(response.choices[0].message.content.strip())

# AI Cover Letter Generator
elif menu == "AI Cover Letter":
    st.title("✍️ AI-Powered Cover Letter Generator")
    with st.form("cover_form"):
        resume = st.text_area("Paste Your Resume")
        job_desc = st.text_area("Paste Job Description")
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Passionate"])
        if st.form_submit_button("Generate Cover Letter"):
            with st.spinner("Generating letter..."):
                prompt = f"""
Write a {tone.lower()} cover letter tailored to the following job description using this resume:

Resume:
{resume}

Job Description:
{job_desc}
"""
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                st.success("Generated Cover Letter:")
                st.write(response.choices[0].message.content.strip())

# View Jobs Table
elif menu == "View Jobs":
    st.title("📁 All Job Applications")
    st.dataframe(df, use_container_width=True)
