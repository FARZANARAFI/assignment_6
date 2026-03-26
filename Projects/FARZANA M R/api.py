from __future__ import annotations

import os
import sys
import pickle
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use FULL pipeline instead of individual model
MODEL_FILES: Dict[str, str] = {
    "Random Forest": os.path.join(BASE_DIR, "pipeline.pkl"),
    "XGBoost": os.path.join(BASE_DIR, "xgboost.pkl"),
    "SVM": os.path.join(BASE_DIR, "svc.pkl"),
    "KNN": os.path.join(BASE_DIR, "knn.pkl"),
    "Decision Tree": os.path.join(BASE_DIR, "decisiontree.pkl"),
}

FEATURE_ORDER = [
    "ph",
    "Hardness",
    "Solids",
    "Chloramines",
    "Sulfate",
    "Conductivity",
    "Organic_carbon",
    "Trihalomethanes",
    "Turbidity",
    "Solids_log",
]

# Engineered features your pipeline expects
ENGINEERED_FEATURES = [
    "Trihalomethanes_log",
    "Cond_Hardness_ratio",
    "Turbidity_norm",
]

# ph_category one-hot columns expected by fit-time feature names
PH_CATEGORY_OHE = [
    "ph_category_alkaline",
    "ph_category_neutral",
    "ph_category_nan",
]

_LOADED: Dict[str, object] = {}


class WaterFeatures(BaseModel):
    ph: float
    Hardness: float
    Solids: float
    Chloramines: float
    Sulfate: float
    Conductivity: float
    Organic_carbon: float
    Trihalomethanes: float
    Turbidity: float
    Solids_log: Optional[float] = None


class PredictResponse(BaseModel):
    model: str
    prediction: int
    label: str
    probability_potable: Optional[float]
    model_file: str


def _safe_log_solids(solids: float) -> float:
    return float(np.log1p(max(solids, 0.0)))


def _load_any(path: str):
    try:
        import joblib
        return joblib.load(path)
    except Exception:
        pass

    with open(path, "rb") as f:
        return pickle.load(f)


def get_or_load_model(model_name: str):
    if model_name in _LOADED:
        return _LOADED[model_name], MODEL_FILES[model_name]

    if model_name not in MODEL_FILES:
        raise HTTPException(status_code=404, detail=f"Unknown model: {model_name}")

    path = MODEL_FILES[model_name]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Model file not found: {path}")

    model_obj = _load_any(path)
    _LOADED[model_name] = model_obj
    return model_obj, path


app = FastAPI(title="Water Potability API", version="3.2")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_found": [k for k, v in MODEL_FILES.items() if os.path.exists(v)],
    }


@app.get("/runtime")
def runtime():
    import sklearn
    return {
        "python": sys.version,
        "numpy": np.__version__,
        "sklearn": sklearn.__version__,
    }


@app.get("/models")
def models():
    return {"models": [k for k, v in MODEL_FILES.items() if os.path.exists(v)]}
@app.post("/predict", response_model=PredictResponse)
def predict(payload: WaterFeatures, model: str = Query(...)):
    features = payload.model_dump()

    # Fill Solids_log if missing
    if features.get("Solids_log") is None:
        features["Solids_log"] = _safe_log_solids(features["Solids"])

    # -----------------------------
    # Engineered numeric features (safe for ALL models)
    # -----------------------------
    features["Trihalomethanes_log"] = float(np.log1p(features["Trihalomethanes"]))

    hardness = float(features["Hardness"])
    conductivity = float(features["Conductivity"])
    features["Cond_Hardness_ratio"] = float(conductivity / hardness) if hardness != 0 else 0.0

    features["Turbidity_norm"] = float(features["Turbidity"]) / 10.0

    # -----------------------------
    # Build ph category info
    # -----------------------------
    ph = float(features["ph"])
    if np.isnan(ph):
        cat = "nan"
    elif 6.5 <= ph <= 8.5:
        cat = "neutral"
    else:
        cat = "alkaline"

    # Always prepare one-hot (numeric) version
    features["ph_category_alkaline"] = 1 if cat == "alkaline" else 0
    features["ph_category_neutral"] = 1 if cat == "neutral" else 0
    features["ph_category_nan"] = 1 if cat == "nan" else 0

    try:
        model_obj, model_path = get_or_load_model(model)
        model_file = os.path.basename(model_path).lower()

        # ✅ Random Forest pipeline expects RAW ph_category
        if model == "Random Forest" and model_file == "pipeline.pkl":
            features["ph_category"] = cat  # raw string column required by pipeline

            required_columns = (
                FEATURE_ORDER
                + ["Trihalomethanes_log", "Cond_Hardness_ratio", "Turbidity_norm", "ph_category"]
            )
            df = pd.DataFrame([{col: features.get(col) for col in required_columns}])

        # ✅ Other models: numeric-only, so use OHE columns and DO NOT include ph_category
        else:
            features.pop("ph_category", None)  # ensure it's not passed

            required_columns = (
                FEATURE_ORDER
                + ["Trihalomethanes_log", "Cond_Hardness_ratio", "Turbidity_norm"]
                + ["ph_category_alkaline", "ph_category_neutral", "ph_category_nan"]
            )
            df = pd.DataFrame([{col: features.get(col, 0) for col in required_columns}])

        # Predict
        pred = int(model_obj.predict(df)[0])

        proba = None
        if hasattr(model_obj, "predict_proba"):
            probs = model_obj.predict_proba(df)[0]
            if hasattr(model_obj, "classes_") and 1 in list(model_obj.classes_):
                classes = list(model_obj.classes_)
                proba = float(probs[classes.index(1)])
            else:
                proba = float(np.max(probs))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {repr(e)}")

    label = "Potable" if pred == 1 else "Not potable"

    return {
        "model": model,
        "prediction": pred,
        "label": label,
        "probability_potable": proba,
        "model_file": os.path.basename(model_path),
    }