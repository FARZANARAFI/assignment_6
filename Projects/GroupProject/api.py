from fastapi import FastAPI, UploadFile, File, Form
import pdfplumber
from ai_engine import screen_resume


# --------------------------------------------------
# FastAPI App Metadata (Swagger Title)
# --------------------------------------------------

app = FastAPI(
    title="TalentLens AI",
    description="GenAI + RAG based Resume Screening System. Upload a resume and evaluate candidate-job match using semantic similarity and ATS scoring.",
    version="1.0"
)


# --------------------------------------------------
# Job Descriptions
# --------------------------------------------------

job_descriptions = {

    "DATA-SCIENCE": """
    Data Scientist

    Required Skills:
    Python
    Machine Learning
    Deep Learning
    Data Analysis
    Statistics
    SQL
    Data Visualization
    Natural Language Processing
    Predictive Modeling
    """,

    "HR": """
    HR Manager

    Required Skills:
    Recruitment
    Employee Relations
    HR Operations
    Performance Management
    Talent Acquisition
    Organizational Development
    """,

    "INFORMATION-TECHNOLOGY": """
    Software Engineer

    Required Skills:
    Python
    Programming
    Algorithms
    Software Development
    Databases
    Cloud Computing
    System Design
    """
}


# --------------------------------------------------
# Resume Text Extraction
# --------------------------------------------------

def extract_text_from_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

    return text


# --------------------------------------------------
# ATS Score Calculation
# --------------------------------------------------

def calculate_ats_score(resume_text, jd_text):

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    common_words = resume_words.intersection(jd_words)

    ats_score = (len(common_words) / len(jd_words)) * 100

    return round(ats_score, 2)


# --------------------------------------------------
# Resume Screening API
# --------------------------------------------------

@app.post("/screen-resume")

async def screen_resume_api(
        domain: str = Form(...),
        resume: UploadFile = File(...)
):

    # Get job description
    jd_text = job_descriptions.get(domain)

    if jd_text is None:
        return {"error": "Invalid domain selected"}

    # Extract resume text
    resume_text = extract_text_from_pdf(resume.file)

    # AI semantic similarity score
    match_score, context = screen_resume(resume_text, jd_text)

    # ATS keyword score
    ats_score = calculate_ats_score(resume_text, jd_text)

    # API response
    return {

        "domain": domain,

        "match_score (%)": round(match_score, 2),

        "ats_score (%)": ats_score,

        "analysis": context

    }