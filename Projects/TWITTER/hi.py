import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from joblib import load

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
            "history": prediction_history
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
            "Negative": float(proba[0]),
            "Neutral": float(proba[1]),
            "Positive": float(proba[2]),
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
            "history": prediction_history
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

# ---------------------------------------------------------
# Run locally
# ---------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
