import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from joblib import load
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# ===============================
# Page config
# ===============================
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📉",
    layout="wide"
)

# ===============================
# Load artifacts
# ===============================
@st.cache_resource
def load_artifacts():
    scaler = load("churn_scaler.joblib")
    le = load("churn_label_encoder.joblib")
    ohe = load("churn_onehot_encoder.joblib")

    models = {
        "Logistic Regression": load("churn_lr_model.joblib"),
        "KNN": load("churn_knn_model.joblib"),
        "SVM": load("churn_svm_model.joblib"),
        "Random Forest": load("churn_rf_model.joblib"),
        "Gradient Boosting": load("churn_gb_model.joblib"),
        "Decision Tree": load("churn_dt_model.joblib"),
        "XGBoost": load("churn_xgb_model.joblib"),
        "AdaBoost": load("churn_ada_model.joblib"),
    }
    return scaler, le, ohe, models


scaler, le, ohe, models = load_artifacts()

# ===============================
# Helper functions
# ===============================
def safe_label_encode(series, le):
    default = le.transform([le.classes_[0]])[0]
    return [
        le.transform([v])[0] if v in le.classes_ else default
        for v in series
    ]


def clean_numeric(df, num_cols):
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def preprocess(df, model):
    binary_columns = ["gender", "Partner", "Dependents", "PhoneService", "PaperlessBilling"]
    cat_cols = ohe.feature_names_in_.tolist()
    num_cols = scaler.feature_names_in_.tolist()

    # -------------------------------
    # Binary encoding
    # -------------------------------
    for col in binary_columns:
        if col in df.columns:
            df[col] = safe_label_encode(df[col], le)

    # -------------------------------
    # One-hot encoding (SAFE)
    # -------------------------------
    cat_cols_in_df = [c for c in cat_cols if c in df.columns]
    if cat_cols_in_df:
        encoded = ohe.transform(df[cat_cols_in_df])
        encoded_df = pd.DataFrame(
            encoded,
            columns=ohe.get_feature_names_out(cat_cols_in_df),
            index=df.index
        )
        df = pd.concat([df.drop(columns=cat_cols_in_df), encoded_df], axis=1)

    # -------------------------------
    # Numeric cleaning + scaling (SAFE)
    # -------------------------------
    num_cols_in_df = [c for c in num_cols if c in df.columns]
    df = clean_numeric(df, num_cols_in_df)

    # 🔥 THIS IS THE FIX — scale ONLY existing columns
    df[num_cols_in_df] = scaler.transform(df[num_cols_in_df])

    # -------------------------------
    # Align with model features
    # -------------------------------
    if hasattr(model, "feature_names_in_"):
        df = df.reindex(columns=model.feature_names_in_, fill_value=0)

    return df




# ===============================
# Sidebar
# ===============================
st.sidebar.title("⚙️ Settings")
selected_model_name = st.sidebar.selectbox("Select Model", list(models.keys()))
model = models[selected_model_name]

st.sidebar.markdown("---")
st.sidebar.info("Upload data or predict a single customer")

# ===============================
# Main UI
# ===============================
st.title("📉 Customer Churn Prediction")
st.markdown("Predict whether a customer is likely to **churn** using multiple ML models.")

tab1, tab2 = st.tabs(["🔮 Single Prediction", "📊 Batch Evaluation"])

# ===============================
# Single Prediction
# ===============================
with tab1:
    st.subheader("Single Customer Prediction")

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        Partner = st.selectbox("Partner", ["Yes", "No"])
        Dependents = st.selectbox("Dependents", ["Yes", "No"])

    with col2:
        PhoneService = st.selectbox("Phone Service", ["Yes", "No"])
        PaperlessBilling = st.selectbox("Paperless Billing", ["Yes", "No"])

    with col3:
        MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0)
        tenure = st.number_input("Tenure", min_value=0)

    if st.button("Predict Churn"):
        input_df = pd.DataFrame([{
            "gender": gender,
            "Partner": Partner,
            "Dependents": Dependents,
            "PhoneService": PhoneService,
            "PaperlessBilling": PaperlessBilling,
            "MonthlyCharges": MonthlyCharges,
            "tenure": tenure,
        }])

        X = preprocess(input_df, model)
        pred = model.predict(X)[0]

        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(X)[0][1]
            msg = f"Probability of churn: **{prob:.2f}**"
        else:
            msg = None

        if pred == 1:
            st.error("⚠️ Customer is likely to churn")
        else:
            st.success("✅ Customer is unlikely to churn")

        if msg:
            st.caption(msg)

# ===============================
# Batch Evaluation
# ===============================
with tab2:
    st.subheader("Batch Evaluation & Confusion Matrix")

    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if "Churn" not in df.columns:
            st.warning("Dataset must contain a **Churn** column.")
        else:
            X = df.drop("Churn", axis=1)
            y = df["Churn"]

            Xp = preprocess(X, model)
            y_pred = model.predict(Xp)

            cm = confusion_matrix(y, y_pred)
            fig, ax = plt.subplots()
            ConfusionMatrixDisplay(cm, display_labels=model.classes_).plot(ax=ax)
            st.pyplot(fig)
