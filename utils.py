import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
import docx
import google.generativeai as genai

# Load variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable in your .env file.")

genai.configure(api_key=api_key)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(file, filetype):
    if filetype == "pdf":
        return extract_text_from_pdf(file)
    elif filetype == "docx":
        return extract_text_from_docx(file)
    return ""

def get_gemini_response(job_desc, resume_text):
    prompt = f"""
You are a resume screening assistant. Compare the following resume to the job description.

Instructions:
- Identify matching skills between job description and resume.
- Consider alternative skills as relevant (e.g., Azure for AWS, Java for Python).
- If job description says "strong knowledge in X", prioritize checking that explicitly.
- Provide the result as plain text with labeled sections exactly like this:

Matching Percentage: <integer 0-100>%
Recommendation: <Hire/Reject/Redirect>
Matching Skills:
- <Skill1>: <integer 0-100>%
- <Skill2>: <integer 0-100>%
- <Skill3>: <integer 0-100>%
- <Skill4>: <integer 0-100>%
Summary:
<10 lines explaining why to hire/reject/redirect>

Job Description:
{job_desc}

Resume:
{resume_text}

Return ONLY the above text format, nothing else.
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()