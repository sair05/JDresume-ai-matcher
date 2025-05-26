import streamlit as st
import re
from utils import extract_text, get_gemini_response
import matplotlib.pyplot as plt

st.set_page_config(page_title="Resume Matcher", layout="centered")
st.title("🧠 Resume Matcher using Gemini AI")

st.markdown("### 📌 Upload Job Description")
job_desc_mode = st.radio("Choose input type:", ["Text", "File"], horizontal=True)

job_description = ""
if job_desc_mode == "Text":
    job_description = st.text_area("Enter Job Description")
else:
    job_file = st.file_uploader("Upload Job Description File (PDF/DOCX)", type=["pdf", "docx"])
    if job_file:
        filetype = job_file.name.split(".")[-1].lower()
        job_description = extract_text(job_file, filetype)

st.markdown("---")
st.markdown("### 👤 Upload Candidate Resume")
resume_file = st.file_uploader("Upload Resume File (PDF/DOCX)", type=["pdf", "docx"])

def parse_response(text):
    # Extract matching percentage
    match_pct = re.search(r"Matching Percentage:\s*(\d+)%", text)
    matching_percentage = int(match_pct.group(1)) if match_pct else 0

    # Extract recommendation
    rec = re.search(r"Recommendation:\s*(\w+)", text)
    recommendation = rec.group(1) if rec else "N/A"

    # Extract skills (up to 4)
    skills_section = re.search(r"Matching Skills:\s*((?:- .+\n)+)", text)
    matching_skills = []
    if skills_section:
        skills_lines = skills_section.group(1).strip().split("\n")
        for line in skills_lines:
            skill_match = re.match(r"- (.+): (\d+)%", line.strip())
            if skill_match:
                matching_skills.append({
                    "name": skill_match.group(1),
                    "percentage": int(skill_match.group(2))
                })

    # Extract summary (everything after "Summary:")
    summary_match = re.search(r"Summary:\s*(.+)", text, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""

    return matching_percentage, recommendation, matching_skills, summary

if st.button("🔍 Analyze Resume"):
    if not job_description:
        st.warning("Please provide a job description.")
    elif not resume_file:
        st.warning("Please upload a resume.")
    else:
        resume_text = extract_text(resume_file, resume_file.name.split(".")[-1].lower())
        response_text = get_gemini_response(job_description, resume_text)

        st.markdown("---")
        st.subheader("✅ Analysis Result")

        matching_percentage, recommendation, matching_skills, summary = parse_response(response_text)

        # Pie chart for matching percentage
        fig1, ax1 = plt.subplots()
        sizes = [matching_percentage, 100 - matching_percentage]
        labels = ['Match %', 'Mismatch %']
        colors = ['#4CAF50', '#D3D3D3']
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        st.pyplot(fig1)

        st.markdown(f"### Recommendation: **{recommendation}**")

        # Bar chart for top 4 matching skills by percentage
        top_skills = sorted(matching_skills, key=lambda x: x['percentage'], reverse=True)[:4]
        if top_skills:
            skill_names = [s['name'] for s in top_skills]
            skill_percents = [s['percentage'] for s in top_skills]

            fig2, ax2 = plt.subplots()
            bars = ax2.bar(skill_names, skill_percents, color='#2196F3')
            ax2.set_ylim(0, 100)
            ax2.set_ylabel('Matching %')
            ax2.set_title('Top 4 Matching Skills')

            for bar in bars:
                height = bar.get_height()
                ax2.annotate(f'{height}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3), textcoords="offset points",
                             ha='center', va='bottom')

            st.pyplot(fig2)
        else:
            st.write("No matching skills data available.")

        st.markdown("### Summary")
        st.write(summary)