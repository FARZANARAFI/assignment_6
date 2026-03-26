# filename: airline_dashboard_full.py
import streamlit as st
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import plotly.graph_objects as go

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title="Airline Passengers Dashboard", layout="wide")
st.title("📈 Airline Passengers Time Series Dashboard")

# -------------------------------
# Load dataset
# -------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
    df = pd.read_csv(url, parse_dates=['Month'], index_col='Month')
    df.columns = ['Passengers']
    return df

data = load_data()

# -------------------------------
# Date range selector
# -------------------------------
st.sidebar.header("Select Date Range")
start_date = st.sidebar.date_input("Start date", data.index.min().date())
end_date = st.sidebar.date_input("End date", data.index.max().date())

# Filter data
data_filtered = data.loc[start_date:end_date]

# -------------------------------
# Decompose time series
# -------------------------------
result = seasonal_decompose(data_filtered['Passengers'], model='multiplicative', period=12)

# -------------------------------
# ARIMA forecast
# -------------------------------
model_arima = ARIMA(data_filtered['Passengers'], order=(2,1,2))
model_fit = model_arima.fit()
forecast_arima = model_fit.forecast(steps=12)
forecast_index = pd.date_range(start=data_filtered.index[-1] + pd.offsets.MonthBegin(),
                               periods=12, freq='M')

# -------------------------------
# Prophet forecast
# -------------------------------
df_prophet = data_filtered.reset_index().rename(columns={'Month':'ds','Passengers':'y'})
model_prophet = Prophet(yearly_seasonality=True, daily_seasonality=False)
model_prophet.fit(df_prophet)
future = model_prophet.make_future_dataframe(periods=12, freq='M')
forecast_prophet = model_prophet.predict(future)

# -------------------------------
# Sidebar toggles
# -------------------------------
st.sidebar.header("Select Components to Display")
show_original = st.sidebar.checkbox("Original Data", value=True)
show_trend = st.sidebar.checkbox("Trend", value=True)
show_seasonality = st.sidebar.checkbox("Seasonality", value=True)
show_residuals = st.sidebar.checkbox("Residuals", value=False)
show_arima = st.sidebar.checkbox("ARIMA Forecast", value=True)
show_prophet = st.sidebar.checkbox("Prophet Forecast", value=True)

# -------------------------------
# Plotly figure
# -------------------------------
fig = go.Figure()

if show_original:
    fig.add_trace(go.Scatter(x=data_filtered.index, y=data_filtered['Passengers'], name='Original'))
if show_trend:
    fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, name='Trend'))
if show_seasonality:
    fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, name='Seasonality'))
if show_residuals:
    fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, name='Residuals'))
if show_arima:
    fig.add_trace(go.Scatter(x=forecast_index, y=forecast_arima, name='ARIMA Forecast'))
if show_prophet:
    fig.add_trace(go.Scatter(x=forecast_prophet['ds'], y=forecast_prophet['yhat'],
                             name='Prophet Forecast', line=dict(dash='dash')))

fig.update_layout(
    title="Airline Passengers Time Series Dashboard",
    xaxis_title="Date",
    yaxis_title="Number of Passengers",
    legend=dict(x=0, y=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Download Buttons
# -------------------------------
st.header("📥 Download Options")

# 1. CSV download
csv = data_filtered.to_csv().encode('utf-8')
st.download_button(
    label="Download Filtered Data (CSV)",
    data=csv,
    file_name="airline_passengers_filtered.csv",
    mime='text/csv'
)

# 2. HTML download
html_bytes = fig.to_html().encode('utf-8')
st.download_button(
    label="Download Plot as HTML",
    data=html_bytes,
    file_name="airline_passengers_dashboard.html",
    mime="text/html"
)

# 3. PNG download
# Make sure 'kaleido' is installed: pip install kaleido
png_bytes = fig.to_image(format="png")
st.download_button(
    label="Download Plot as PNG",
    data=png_bytes,
    file_name="airline_passengers_dashboard.png",
    mime="image/png"
)