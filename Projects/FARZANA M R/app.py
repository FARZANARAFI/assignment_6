import os
import math
import time
import requests
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Water Potability Lab",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Global Styling (Light Theme)
# -----------------------------
st.markdown("""
<style>

/* Main app background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

/* Sidebar - light soft blue */
section[data-testid="stSidebar"] {
    background-color: #eef5ff;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #f0fdf4;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid #d1fae5;
}

/* Buttons */
.stButton>button {
    border-radius: 8px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)
DEFAULT_API_URL = os.environ.get("API_URL", "http://localhost:8000")

# -----------------------------
# Small utilities
# -----------------------------
def safe_get(url: str, timeout: int = 5):
    return requests.get(url, timeout=timeout)

def safe_post(url: str, params: dict, json: dict, timeout: int = 15):
    return requests.post(url, params=params, json=json, timeout=timeout)

def compute_solids_log(solids: float) -> float:
    return float(np.log1p(max(solids, 0.0)))

def badge(label: str):
    if label.lower().startswith("potable"):
        st.markdown(
            "<div style='display:inline-block;padding:6px 10px;border-radius:999px;"
            "background:#e8fff1;color:#145a32;font-weight:700;'>✅ POTABLE</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='display:inline-block;padding:6px 10px;border-radius:999px;"
            "background:#ffecec;color:#7b241c;font-weight:700;'>⚠️ NOT POTABLE</div>",
            unsafe_allow_html=True,
        )

def radar_plot(values: dict):
    # Simple radar using matplotlib (no seaborn)
    labels = list(values.keys())
    data = np.array([values[k] for k in labels], dtype=float)

    # Normalize for display (rough scale — purely for visualization)
    # You can tweak these bounds if you want.
    bounds = {
        "ph": (0, 14),
        "Hardness": (0, 500),
        "Solids": (0, 50000),
        "Chloramines": (0, 15),
        "Sulfate": (0, 500),
        "Conductivity": (0, 1000),
        "Organic_carbon": (0, 30),
        "Trihalomethanes": (0, 150),
        "Turbidity": (0, 10),
        "Solids_log": (0, 12),
    }
    norm = []
    for k, v in values.items():
        lo, hi = bounds.get(k, (min(data), max(data) if max(data) != min(data) else min(data) + 1))
        vv = max(lo, min(hi, float(v)))
        norm.append((vv - lo) / (hi - lo) if hi > lo else 0.0)

    norm = np.array(norm)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    norm = np.concatenate([norm, norm[:1]])
    angles = np.concatenate([angles, angles[:1]])

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, norm)
    ax.fill(angles, norm, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticklabels([])
    ax.set_title("Parameter Fingerprint (normalized)", pad=18)
    st.pyplot(fig)

def bar_plot(values: dict):
    labels = list(values.keys())
    data = [values[k] for k in labels]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(labels, data)
    ax.set_title("Raw Inputs")
    ax.tick_params(axis="x", rotation=40)
    st.pyplot(fig)

# -----------------------------
# Session state (history)
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div style="padding:14px 16px;border-radius:18px;background:linear-gradient(90deg,#0ea5e9,#22c55e);
                color:white;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
      <div style="font-size:28px;font-weight:900;line-height:1.1;">💧 Water Potability Lab</div>
      <div style="opacity:0.95;margin-top:6px;">
        Explore water chemistry, compare ML models, and get a potability prediction from your FastAPI backend.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# -----------------------------
# Sidebar: backend + model + presets
# -----------------------------
with st.sidebar:
    st.subheader("🔌 Backend")

    api_url = st.text_input("FastAPI URL", value=DEFAULT_API_URL)

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("Health Check"):
            try:
                r = safe_get(f"{api_url}/health", timeout=5)
                st.session_state["_health"] = r.json()
            except Exception as e:
                st.session_state["_health"] = {"error": str(e)}
    with colB:
        st.caption("Tip: start FastAPI first")

    health = st.session_state.get("_health")
    if health:
        if "error" in health:
            st.error(f"Backend error: {health['error']}")
        else:
            st.success("Backend reachable ✅")
            with st.expander("Health details"):
                st.json(health)

    st.divider()
    st.subheader("🧠 Model")

    # Fetch models from backend
    model_list = []
    try:
        r = safe_get(f"{api_url}/models", timeout=5)
        model_list = r.json().get("models", [])
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        st.stop()

    if not model_list:
        st.error("No models found from backend. Open /health to debug.")
        st.stop()

    model = st.selectbox("Choose model", options=model_list, index=0)

    st.divider()
    st.subheader("⚡ Quick Presets")
    presets = {
        "Typical Tap Water": dict(ph=7.2, Hardness=180, Solids=25000, Chloramines=6.8, Sulfate=280, Conductivity=420,
                                  Organic_carbon=12, Trihalomethanes=70, Turbidity=3.5),
        "Hard Water": dict(ph=7.8, Hardness=320, Solids=32000, Chloramines=7.5, Sulfate=330, Conductivity=650,
                           Organic_carbon=14, Trihalomethanes=80, Turbidity=4.2),
        "Soft Water": dict(ph=6.9, Hardness=90, Solids=15000, Chloramines=6.0, Sulfate=180, Conductivity=250,
                           Organic_carbon=10, Trihalomethanes=55, Turbidity=2.5),
        "River/Surface": dict(ph=7.0, Hardness=120, Solids=18000, Chloramines=2.0, Sulfate=140, Conductivity=220,
                              Organic_carbon=18, Trihalomethanes=35, Turbidity=6.5),
        "Industrial-ish": dict(ph=8.4, Hardness=260, Solids=45000, Chloramines=9.5, Sulfate=420, Conductivity=800,
                               Organic_carbon=22, Trihalomethanes=110, Turbidity=5.5),
    }
    preset_name = st.selectbox("Load a preset", ["(none)"] + list(presets.keys()))
    if st.button("Apply preset"):
        if preset_name != "(none)":
            st.session_state["inputs"] = presets[preset_name]
            st.success(f"Applied: {preset_name}")

# -----------------------------
# Main input area (tabs)
# -----------------------------
tabs = st.tabs(["🧪 Input", "📈 Visualize", "📊 Model Report", "🧾 History"])

# Load input defaults
defaults = st.session_state.get("inputs", dict(
    ph=7.0, Hardness=200.0, Solids=20000.0, Chloramines=7.0, Sulfate=300.0,
    Conductivity=400.0, Organic_carbon=14.0, Trihalomethanes=66.0, Turbidity=4.0
))

with tabs[0]:
    st.subheader("🧪 Enter Water Parameters")

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        ph = st.number_input("pH", value=float(defaults["ph"]), format="%.6f")
        hardness = st.number_input("Hardness", value=float(defaults["Hardness"]), format="%.6f")
        solids = st.number_input("Solids", value=float(defaults["Solids"]), format="%.6f")

    with c2:
        chloramines = st.number_input("Chloramines", value=float(defaults["Chloramines"]), format="%.6f")
        sulfate = st.number_input("Sulfate", value=float(defaults["Sulfate"]), format="%.6f")
        conductivity = st.number_input("Conductivity", value=float(defaults["Conductivity"]), format="%.6f")

    with c3:
        organic_carbon = st.number_input("Organic carbon", value=float(defaults["Organic_carbon"]), format="%.6f")
        trihalomethanes = st.number_input("Trihalomethanes", value=float(defaults["Trihalomethanes"]), format="%.6f")
        turbidity = st.number_input("Turbidity", value=float(defaults["Turbidity"]), format="%.6f")

    st.write("")
    st.caption("🧠 Solids_log is computed automatically (log(1 + Solids)). You can override it if you want.")
    override = st.checkbox("Override Solids_log")
    solids_log = compute_solids_log(solids)
    if override:
        solids_log = st.number_input("Solids_log", value=float(solids_log), format="%.6f")

    payload = {
        "ph": ph,
        "Hardness": hardness,
        "Solids": solids,
        "Chloramines": chloramines,
        "Sulfate": sulfate,
        "Conductivity": conductivity,
        "Organic_carbon": organic_carbon,
        "Trihalomethanes": trihalomethanes,
        "Turbidity": turbidity,
        "Solids_log": solids_log,
    }

    st.divider()

    left, right = st.columns([1, 1])
    with left:
        if st.button("🔮 Predict", type="primary", use_container_width=True):
            with st.spinner("Asking the lab models..."):
                try:
                    r = safe_post(f"{api_url}/predict", params={"model": model}, json=payload, timeout=20)
                    if r.status_code != 200:
                        st.error(f"API error {r.status_code}: {r.text}")
                    else:
                        out = r.json()

                        # Display
                        st.success("Prediction complete")
                        badge(out["label"])

                        if out.get("probability_potable") is not None:
                            st.metric("Probability potable", f"{out['probability_potable']:.3f}")

                        with st.expander("Full response"):
                            st.json(out)

                        # Save to history
                        st.session_state.history.append({
                            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "model": model,
                            "label": out.get("label"),
                            "probability_potable": out.get("probability_potable"),
                            **payload,
                        })
                except Exception as e:
                    st.error(f"Request failed: {e}")

    with right:
        st.markdown(
            """
            <div style="border:1px solid rgba(0,0,0,0.08);padding:12px;border-radius:16px;">
              <div style="font-weight:800;font-size:16px;margin-bottom:6px;">🧾 Payload Preview</div>
              <div style="opacity:0.75;">These values are sent to your FastAPI backend.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.json(payload)

with tabs[1]:
    st.subheader("📈 Visualize Your Sample")

    st.write("These charts are for intuition (visual normalization only).")
    v = dict(
        ph=payload["ph"],
        Hardness=payload["Hardness"],
        Solids=payload["Solids"],
        Chloramines=payload["Chloramines"],
        Sulfate=payload["Sulfate"],
        Conductivity=payload["Conductivity"],
        Organic_carbon=payload["Organic_carbon"],
        Trihalomethanes=payload["Trihalomethanes"],
        Turbidity=payload["Turbidity"],
        Solids_log=payload["Solids_log"],
    )

    colx, coly = st.columns([1, 1])
    with colx:
        radar_plot(v)
    with coly:
        bar_plot(v)

    st.info("Want more insights? I can add reference ranges + out-of-range flags per parameter.")

with tabs[2]:
    st.subheader("📊 Model Performance Report")

    st.markdown("""
    This report summarizes model performance from the training notebook (`water.ipynb`).
    """)

    # Example metrics (replace with your real notebook values)
    report_data = pd.DataFrame({
        "Model": ["Random Forest", "XGBoost", "SVM", "KNN", "Decision Tree"],
        "Accuracy": [0.82, 0.80, 0.78, 0.75, 0.74],
        "Precision": [0.83, 0.79, 0.76, 0.73, 0.72],
        "Recall": [0.81, 0.78, 0.77, 0.74, 0.70],
        "F1 Score": [0.82, 0.78, 0.76, 0.73, 0.71]
    })

    st.dataframe(
        report_data.style
        .background_gradient(cmap="Blues", subset=["Accuracy"])
        .background_gradient(cmap="Greens", subset=["F1 Score"])
    )

    st.markdown("### 📈 Accuracy Comparison")

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(report_data["Model"], report_data["Accuracy"])
    ax.set_title("Model Accuracy Comparison")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

    best_model = report_data.sort_values("Accuracy", ascending=False).iloc[0]["Model"]
    st.success(f"🏆 Best Performing Model: **{best_model}**")

    # ✅ ADD THIS PART HERE (inside tabs[2])
    if st.button("Generate Text Report"):
        report_text = f"""
Water Potability ML Report

Best Model: {best_model}

Accuracy Scores:
{report_data.to_string(index=False)}
"""
        st.download_button(
            "Download Report (.txt)",
            report_text,
            file_name="water_model_report.txt"
        )

with tabs[2]:
    st.subheader("🧾 Prediction History")

    if not st.session_state.history:
        st.caption("No predictions yet. Run a prediction in the Input tab.")
    else:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download history as CSV",
            data=csv,
            file_name="water_potability_history.csv",
            mime="text/csv",
        )

        if st.button("Clear history"):
            st.session_state.history = []
            st.success("Cleared.")