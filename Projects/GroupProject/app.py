import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import matplotlib.pyplot as plt
from fpdf import FPDF
from ai_engine import screen_resume

import pdfplumber

def load_demo_resumes():

    resumes = []

    with pdfplumber.open("demo_resumes/nighitha_cv.pdf") as pdf:

        text = ""

        for page in pdf.pages:
            text += page.extract_text()

    resumes.append({
        "Resume_str": text,
        "Category": "DATA-SCIENCE"
    })

    return pd.DataFrame(resumes)

def generate_pdf(candidate_id, score, evaluation):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200,10, txt="AI Resume Screening Report", ln=True)

    pdf.ln(5)

    pdf.cell(200,10, txt=f"Candidate ID: {candidate_id}", ln=True)
    pdf.cell(200,10, txt=f"Match Score: {score}%", ln=True)

    pdf.ln(10)

    pdf.multi_cell(0,10, txt=evaluation)

    file_name = "candidate_report.pdf"

    pdf.output(file_name)

    return file_name

import os
os.environ["GROQ_API_KEY"] = "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"

st.set_page_config(page_title="AI Resume Screening", layout="wide")

st.title("AI Resume Screening & Talent Match System (RAG + GenAI)")

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_dataset():
    df = pd.read_csv("resume_dataset.csv")

    # clean dataset
    df = df.dropna(subset=["Category"])
    df["Category"] = df["Category"].str.upper()

    # keep categories with shorter names (remove corrupted entries)
    df = df[df["Category"].str.len() < 40]

    return df

df = load_dataset()

# -----------------------------
# Domain Selection
# -----------------------------
valid_domains = [
    "INFORMATION-TECHNOLOGY",
    "HR",
    "DATA-SCIENCE",
    "HEALTHCARE",
    "SALES",
    "TEACHER",
    "ADVOCATE",
    "DIGITAL-MEDIA"
]

df = df[df["Category"].isin(valid_domains)]

domains = valid_domains

selected_domain = st.selectbox(
    "Select Job Domain",
    domains
)

# -----------------------------
# Job Descriptions
# -----------------------------
job_descriptions = {

"INFORMATION-TECHNOLOGY": """
Software Engineer

Required Skills:
Python
Programming
Algorithms
Software Development
Databases
Cloud Computing
""",

"HR": """
HR Manager

Required Skills:
Recruitment
Employee Relations
HR Operations
Performance Management
Talent Acquisition
""",

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
""",

"HEALTHCARE": """
Healthcare Specialist

Required Skills:
Patient Care
Medical Documentation
Healthcare Regulations
Clinical Procedures
Medical Data Management
""",

"SALES": """
Sales Manager

Required Skills:
Lead Generation
Client Relationship Management
Sales Strategy
Negotiation
Market Research
""",

"TEACHER": """
Teacher

Required Skills:
Lesson Planning
Student Assessment
Classroom Management
Educational Technology
Curriculum Development
""",

"ADVOCATE": """
Legal Advocate

Required Skills:
Legal Research
Case Preparation
Court Representation
Client Counseling
Legal Documentation
""",

"DIGITAL-MEDIA": """
Digital Media Specialist

Required Skills:
Content Creation
Social Media Marketing
SEO
Digital Campaign Management
Analytics Tools
"""
}

jd_text = job_descriptions.get(selected_domain, "")

st.subheader("Job Description")
st.write(jd_text)

# -----------------------------
# Filter Resumes by Domain
# -----------------------------
# Load resumes depending on domain

if selected_domain == "DATA-SCIENCE":
    filtered_df = load_demo_resumes()
else:
    filtered_df = df[df["Category"] == selected_domain]

# Stop if no resumes exist

if filtered_df.empty:
    st.warning("No resumes available for this domain.")
    st.stop()

# limit resumes for demo
if selected_domain != "DATA-SCIENCE":
    filtered_df = filtered_df.head(50)

st.write("Total resumes in this domain:", len(filtered_df))

# -----------------------------
# Load Embedding Model
# -----------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# -----------------------------
# Run Screening
# -----------------------------
if st.button("Run Resume Screening"):

    jd_embedding = model.encode([jd_text])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    scores = []

    for i, row in filtered_df.iterrows():

        resume_text = row["Resume_str"]

        chunks = splitter.split_text(resume_text)

        chunk_embeddings = model.encode(chunks)

        similarities = cosine_similarity(jd_embedding, chunk_embeddings)[0]

        score = max(similarities)*100

        scores.append((i, score))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # -----------------------------
    # Show Top Candidates
    # -----------------------------
    st.subheader("Top Candidates")

    for rank, (idx, score) in enumerate(scores[:5], start=1):

        st.write(
            f"Rank {rank} — Match Score: {round(score,2)}%"
        )
    # -----------------------------
    # Score Visualization
    # -----------------------------

    names = []
    values = []

    for rank, (idx, score) in enumerate(scores[:5], start=1):
     names.append(f"Candidate {rank}")
     values.append(score)

    fig, ax = plt.subplots()

    ax.bar(names, values)

    ax.set_ylabel("Match Score (%)")
    ax.set_title("Top Candidate Match Scores")

    st.subheader("Candidate Score Visualization")

    st.pyplot(fig)

    # -----------------------------
    # Candidate Comparison
    # -----------------------------
    comparison_data = []

    for rank, (idx, score) in enumerate(scores[:3], start=1):

        comparison_data.append({
            "Rank": rank,
            "Resume ID": idx,
            "Match Score (%)": round(score,2)
        })

    comparison_df = pd.DataFrame(comparison_data)

    st.subheader("Top Candidate Comparison")

    st.table(comparison_df)

# -----------------------------
    # Load LLM
    # -----------------------------
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    st.session_state["llm"] = llm

    # -----------------------------

    # -----------------------------
    # RAG Retrieval
    # -----------------------------
    top_idx = scores[0][0]

    top_resume = filtered_df.loc[top_idx]["Resume_str"]

    st.session_state["top_resume"] = top_resume

    score, context = screen_resume(top_resume, jd_text)

    st.write(f"Match Score: {round(score,2)}%")

    top_indices = np.argsort(similarities)[-3:]

    top_chunks = [chunks[i] for i in top_indices]

    context = "\n\n".join(top_chunks)

    st.session_state["context"] = context

    # -----------------------------
    # GenAI Candidate Evaluation
    # -----------------------------
    prompt = f"""
You are an expert HR recruiter.

Job Description:
{jd_text}

Candidate Resume Sections:
{context}

Evaluate the candidate and provide:

1. Match Score (0-100)
2. Matching Skills
3. Missing Skills
4. Hiring Recommendation
"""

    response = llm.invoke(prompt)

    st.subheader("AI Candidate Evaluation")

    st.write(response.content)

    pdf_file = generate_pdf(top_idx, round(scores[0][1],2), response.content)

    with open(pdf_file, "rb") as file:
     st.download_button(
        label="Download Candidate Report",
        data=file,
        file_name="candidate_report.pdf",
        mime="application/pdf"
    )

    # -----------------------------
    # Skill Extraction
    # -----------------------------
    skill_prompt = f"""
Extract the key technical skills from the following resume:

{top_resume}

Return the skills as a list.
"""

    skills = llm.invoke(skill_prompt)

    st.subheader("Extracted Skills")

    st.write(skills.content)

    # -----------------------------
    # Recruiter Chatbot
    # -----------------------------
    st.divider()
st.subheader("Recruiter AI Assistant")

question = st.text_input("Ask about the candidate")

if question:

    if "context" not in st.session_state:
        st.warning("Please run resume screening first.")

    else:

        context = st.session_state["context"]
        llm = st.session_state["llm"]

        prompt = f"""
You are an AI recruitment assistant.

Job Description:
{jd_text}

Relevant Resume Sections:
{context}

Recruiter Question:
{question}

Answer clearly based on the resume information.
"""

        response = llm.invoke(prompt)

        st.write(response.content)

def generate_pdf(candidate_id, score, evaluation):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200,10, txt="AI Resume Screening Report", ln=True)

    pdf.ln(5)

    pdf.cell(200,10, txt=f"Candidate ID: {candidate_id}", ln=True)

    pdf.cell(200,10, txt=f"Match Score: {score}%", ln=True)

    pdf.ln(10)

    pdf.multi_cell(0,10, txt=evaluation)

    file_name = "candidate_report.pdf"

    pdf.output(file_name)

    return file_name