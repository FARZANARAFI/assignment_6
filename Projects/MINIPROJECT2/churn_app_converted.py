import streamlit as st
import pandas as pd
from joblib import load
import numpy as np

# ===============================
# Load artifacts
# ===============================
scaler = load("churn_scaler.joblib")
le = load("churn_label_encoder.joblib")
ohe = load("churn_onehot_encoder.joblib")

# Load models
models = {
    "Logistic Regression": load('churn_lr_model.joblib'),
    "KNN": load('churn_knn_model.joblib'),
    "SVM": load('churn_svm_model.joblib'),
    "Random Forest": load('churn_rf_model.joblib'),
    "Gradient Boosting": load('churn_gb_model.joblib'),
    "Decision Tree": load('churn_dt_model.joblib'),
    "XGBoost": load('churn_xgb_model.joblib'),
    "AdaBoost": load('churn_ada_model.joblib')
}

# ===============================
# Model Selector
# ===============================
selected_model_name = st.selectbox("Select Model", list(models.keys()))
model = models[selected_model_name]

# Get model features if available
model_features = getattr(model, 'feature_names_in_', None)

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="Customer Churn Prediction", layout="centered")
st.title("📉 Customer Churn Prediction App")
st.write("Enter customer details to predict churn")


# ===============================
# Dynamic input fields
# ===============================
# Binary columns from LabelEncoder
bin_cols = le.classes_.tolist()
bin_inputs = {}
for col in bin_cols:
    bin_inputs[col] = st.selectbox(col, ["Yes", "No"])

# One-hot categorical columns from OneHotEncoder
cat_cols = ohe.feature_names_in_.tolist()  # original categorical columns
cat_inputs = {}
for col in cat_cols:
    # Get unique categories from encoder
    categories = ohe.categories_[ohe.feature_names_in_.tolist().index(col)]
    cat_inputs[col] = st.selectbox(col, categories)

# Numeric columns from scaler
num_cols = scaler.feature_names_in_.tolist()
num_inputs = {}
for col in num_cols:
    min_val = 0
    max_val = 10000  # arbitrary large number
    if col.lower().find("charge") != -1:
        num_inputs[col] = st.number_input(col, min_value=0.0)
    else:
        num_inputs[col] = st.number_input(col, min_value=0, max_value=1000)

# ===============================
# Prediction Logic
# ===============================
if st.button("Predict Churn"):
    # Combine inputs into dataframe
    input_df = pd.DataFrame([{**num_inputs, **bin_inputs, **cat_inputs}])

    # Binary encoding
    for col in bin_cols:
        input_df[col] = le.transform(input_df[col])

    # One-hot encoding
    encoded = ohe.transform(input_df[cat_cols])
    encoded_df = pd.DataFrame(encoded, columns=ohe.get_feature_names_out(cat_cols))
    input_df = pd.concat([input_df.drop(columns=cat_cols), encoded_df], axis=1)

    # Scale numeric features
    input_df[num_cols] = scaler.transform(input_df[num_cols])

    # Align with model features
    if model_features is not None:
        input_df = input_df.reindex(columns=model_features, fill_value=0)

    # Prediction
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1] if hasattr(model, "predict_proba") else None

    # Output
    if prediction == 1:
        if probability is not None:
            st.error(f"⚠️ Customer is likely to churn (Probability: {probability:.2f})")
        else:
            st.error("⚠️ Customer is likely to churn")
    else:
        if probability is not None:
            st.success(f"✅ Customer is unlikely to churn (Probability: {probability:.2f})")
        else:
            st.success("✅ Customer is unlikely to churn")
# Add any additional Streamlit components or UI elements as needed. 

# ===============================
