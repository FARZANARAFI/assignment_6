from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

def screen_resume(resume_text, jd_text):

    jd_embedding = model.encode([jd_text])

    chunks = splitter.split_text(resume_text)

    chunk_embeddings = model.encode(chunks)

    similarities = cosine_similarity(jd_embedding, chunk_embeddings)[0]

    score = max(similarities) * 100

    top_indices = np.argsort(similarities)[-3:]

    top_chunks = [chunks[i] for i in top_indices]

    context = "\n\n".join(top_chunks)

    return score, context