import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from joblib import load
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime
import io
import csv
# ---------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------
MODEL_PATH = "sentiment_model.h5"
TOKENIZER_PATH = "tokenizer.joblib"
MAX_SEQUENCE_LENGTH = 40
ID_TO_LABEL = {0: "Negative", 1: "Neutral", 2: "Positive"}
# ---------------------------------------------------------
# Load model & tokenizer ONCE
# ---------------------------------------------------------
model = tf.keras.models.load_model(MODEL_PATH)
tokenizer = load(TOKENIZER_PATH)
# ---------------------------------------------------------
# Cleaning function (must match training)
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"@[A-Za-z0-9_]+", " ", text)
    text = re.sub(r"[^a-zA-Z\s!?]", " ", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text
# ---------------------------------------------------------
# Prediction helper
# ---------------------------------------------------------
def predict_sentiment(raw_text: str):
    cleaned = clean_text(raw_text)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(
        seq,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )

    proba = model.predict(padded, verbose=0)[0]
    pred_id = int(np.argmax(proba))
    pred_label = ID_TO_LABEL[pred_id]

    return pred_label, proba

def generate_summary(history):
    if not history:
        return None

    total = len(history)
    pos = sum(1 for h in history if h["sentiment"] == "Positive")
    neu = sum(1 for h in history if h["sentiment"] == "Neutral")
    neg = sum(1 for h in history if h["sentiment"] == "Negative")

    avg_conf = round(sum(h["confidence"] for h in history) / total, 2)

    dominant = max(
        [("Positive", pos), ("Neutral", neu), ("Negative", neg)],
        key=lambda x: x[1]
    )[0]

    return {
        "total": total,
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "average_confidence": avg_conf,
        "dominant": dominant,
        "last_updated": history[-1]["timestamp"]
    }
# ---------------------------------------------------------
# FastAPI setup
# ---------------------------------------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Store prediction history (session)
prediction_history = []
# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sentiment": None,
            "probabilities": None,
            "stats": None,
            "user_input": "",
            "history": prediction_history,
            "summary": generate_summary(prediction_history)
        }
    )

@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request, tweet: str = Form(...)):
    sentiment = None
    probabilities = None
    stats = None

    if tweet.strip():
        sentiment, proba = predict_sentiment(tweet)
        probabilities = {
            "Negative": round(float(proba[0]), 4),
            "Neutral": round(float(proba[1]), 4),
            "Positive": round(float(proba[2]), 4),
        }

        stats = {
            "word_count": len(tweet.split()),
            "confidence": round(max(probabilities.values()) * 100, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to history
        prediction_history.append({
            "tweet": tweet,
            "sentiment": sentiment,
            "negative": probabilities["Negative"],
            "neutral": probabilities["Neutral"],
            "positive": probabilities["Positive"],
            "word_count": stats["word_count"],
            "confidence": stats["confidence"],
            "timestamp": stats["timestamp"]
        })

    return templates.TemplateResponse(
    "index.html",
    {
        "request": request,
        "sentiment": sentiment,
        "probabilities": probabilities,
        "stats": stats,
        "user_input": tweet,
        "history": prediction_history,
        "summary": generate_summary(prediction_history)
    }
)
# ---------------------------------------------------------
# Download CSV report
# ---------------------------------------------------------
@app.get("/download")
def download_report():
    if not prediction_history:
        return HTMLResponse("<h3>No predictions to download!</h3>")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "timestamp", "tweet", "sentiment", "negative", "neutral", "positive", "word_count", "confidence"
    ])
    writer.writeheader()
    for row in prediction_history:
        writer.writerow(row)
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.csv"}
    )

@app.get("/download-pdf")
def download_pdf_report():
    if not prediction_history:
        return HTMLResponse("<h3>No predictions to download!</h3>")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Twitter Sentiment Analysis Report")

    y -= 30
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 40
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Time")
    pdf.drawString(160, y, "Sentiment")
    pdf.drawString(260, y, "Confidence")
    pdf.drawString(360, y, "Tweet")

    y -= 15
    pdf.setFont("Helvetica", 10)

    for item in prediction_history:
        if y < 80:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, item["timestamp"])
        pdf.drawString(160, y, item["sentiment"])
        pdf.drawString(260, y, f'{item["confidence"]}%')

        tweet_text = item["tweet"][:60] + "..." if len(item["tweet"]) > 60 else item["tweet"]
        pdf.drawString(360, y, tweet_text)

        y -= 15

    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.pdf"}
    )
# ---------------------------------------------------------
# Run locally
# ---------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("twitter_sentiment_app:app", host="127.0.0.1", port=8080, reload=True)
