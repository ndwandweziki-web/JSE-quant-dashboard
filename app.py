import pandas as pd
import streamlit as st
import yfinance as yf
import numpy as np  # NEW
from sklearn.ensemble import RandomForestClassifier  # NEW
from sklearn.model_selection import TimeSeriesSplit  # NEW
from sklearn.metrics import accuracy_score  # NEW

# 1. Page Configurations
st.set_page_config(page_title="Stats Analysis", layout="wide")
st.title("📈 BCom Statistics: Live Market Dashboard")

# 2.  Welcome Banner TO SHOWCASE my Massive EGO
st.success(
    "🎉 Welcome to MR NDWANDWE's FIRST SUCCESSFUL STATS ANALYSIS WEBSITE!"
)

# 3. Comprehensive Asset Repository
asset_dict = {
    "Capitec Bank (JSE)": "CPI.JO",
    "Standard Bank (JSE)": "SBK.JO",
    "FirstRand / FNB (JSE)": "FSR.JO",
    "TymeBank Proxy (ARC Investments - JSE)": "AIL.JO",
    "MTN Group (JSE)": "MTN.JO",
    "Vodacom Group (JSE)": "VOD.JO",
    "Gold Futures (USD)": "GC=F",
    "Platinum Futures (USD)": "PL=F",
    "USD / ZAR Exchange Rate": "USDZAR=X",
}

# 4. Sidebar Controller (Allows user-driven multi-series selection)
selected_assets = st.sidebar.multiselect(
    "Select Assets to Compare",
    options=list(asset_dict.keys()),
    default=[
        "Capitec Bank (JSE)",
        "Standard Bank (JSE)",
        "FirstRand / FNB (JSE)",
    ],  # Preselectig the big three banking competitors in SA
)

# 5. Core Data Sourcing & Analysis Pipeline
if selected_assets:
    raw_price_df = pd.DataFrame()

    # Loop through selections and download data frames from Yahoo Finance
    for asset in selected_assets:
        ticker = asset_dict[asset]
        df = yf.download(
            ticker, start="2024-01-01", progress=False, multi_level_index=False
        )

        if not df.empty:
            raw_price_df[asset] = df["Close"]

    # Drop incomplete/nonoverlapping rows to keep the data frames perfectly synchronized
    raw_price_df = raw_price_df.dropna()

    if not raw_price_df.empty:
        # QUANT ENGIn: Price Normalization to Base 100 for true comparative percentage growth
        normalized_df = (raw_price_df / raw_price_df.iloc[0]) * 100

        # Comparative Visualization Frame
        st.subheader("Interactive Performance Comparison (Base 100)")
        st.markdown(
            "*All asset time series normalized to a baseline of 100 at the starting index to evaluate relative performance.*"
        )
        st.line_chart(normalized_df)

        # Dataset Export Infrastructure
        st.subheader("📥 Export Dataset")
        csv_data = raw_price_df.to_csv().encode("utf-8")
        st.download_button(
            label="Download Raw Closing Price CSV Data",
            data=csv_data,
            file_name="jse_market_comparison.csv",
            mime="text/csv",
        )

        # Comparative RiskReturn Matrix Table
        st.subheader("Statistical Analysis Summary")
        returns_df = raw_price_df.pct_change().dropna()

        stats_summary = pd.DataFrame(
            {
                "Mean Daily Return": returns_df.mean().map(lambda x: f"{x:.4%}"),
                "Volatility (Std Dev)": returns_df.std().map(lambda x: f"{x:.4%}"),
            }
        )
        st.table(stats_summary)

        # Expanded Data Matrix View
        with st.expander("Preview Raw Data Matrix"):
            st.dataframe(raw_price_df)

        # =====================================================================
        # 6. NEW FEATURE: MACHINE LEARNING & STRATEGY BACKTESTER
        # =====================================================================
        st.markdown("---")
        st.subheader("🤖 Machine Learning Predictive Engine & Backtester")
        st.markdown(
            "Predicting next-day directional asset movement using rolling statistical features."
        )

        # User chooses which of their active sidebar assets to build an ML model for
        ml_asset = st.selectbox(
            "Select Target Asset for ML Training", options=selected_assets
        )

        if ml_asset:
            # Create a separate dataframe to process the single target asset
            ml_df = pd.DataFrame(index=raw_price_df.index)
            ml_df["Price"] = raw_price_df[ml_asset]

            # Enforce Stationarity via Log Returns
            ml_df["Log_Returns"] = np.log(ml_df["Price"] / ml_df["Price"].shift(1))

            # Outlier Mitigation: Clip anomalies beyond 3 standard deviations (fixes extreme variance drops)
            mean_ret = ml_df["Log_Returns"].mean()
            std_ret = ml_df["Log_Returns"].std()
            ml_df["Cleaned_Returns"] = ml_df["Log_Returns"].clip(
                lower=mean_ret - 3 * std_ret, upper=mean_ret + 3 * std_ret
            )

            # Feature Engineering: Statistical indicators
            ml_df["Lag_1"] = ml_df["Cleaned_Returns"].shift(1)
            ml_df["Lag_2"] = ml_df["Cleaned_Returns"].shift(2)
            ml_df["Rolling_Mean_5"] = (
                ml_df["Cleaned_Returns"].rolling(window=5).mean()
            )
            ml_df["Rolling_Std_5"] = (
                ml_df["Cleaned_Returns"].rolling(window=5).std()
            )

            # Target Assignment: 1 if tomorrow's return is positive, 0 if negative
            ml_df["Target"] = (ml_df["Cleaned_Returns"].shift(-1) > 0).astype(int)

            # Clear out boundary rows containing NaNs
            ml_data = ml_df.dropna()

            feature_columns = ["Lag_1", "Lag_2", "Rolling_Mean_5", "Rolling_Std_5"]

            # Confirm dataset has minimum viable records for processing
            if len(ml_data) > 40:
                X = ml_data[feature_columns]
                y = ml_data["Target"]

                # Chronological Time Series Cross-Validation Split
                tscv = TimeSeriesSplit(n_splits=3)
                model = RandomForestClassifier(
                    n_estimators=100, max_depth=5, random_state=42
                )

                # Iterate segments to simulate reality (no lookahead bias)
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                # Fit model using final historical partition training fold
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                accuracy = accuracy_score(y_test, preds)

                # Output Model Performance Metrics
                st.metric(
                    label=f"Out-of-Sample Predictive Directional Accuracy ({ml_asset})",
                    value=f"{accuracy * 100:.2f}%",
                )

                # Algorithmic Backtester Logic
                backtest_df = pd.DataFrame(index=X_test.index)
                backtest_df["Market_Returns"] = ml_data["Cleaned_Returns"].loc[
                    X_test.index
                ]

                # Map predictions: 1 = Long (+1), 0 = Short (-1)
                backtest_df["Position"] = np.where(preds == 1, 1, -1)
                backtest_df["Strategy_Returns"] = (
                    backtest_df["Position"] * backtest_df["Market_Returns"]
                )

                # Compound returns from base 100 benchmark initialization
                backtest_df["Buy & Hold (Market)"] = (
                    1 + backtest_df["Market_Returns"]
                ).cumprod() * 100
                backtest_df["ML Algorithmic Strategy"] = (
                    1 + backtest_df["Strategy_Returns"]
                ).cumprod() * 100

                # Render performance chart natively matching your UI design style
                st.write("#### Historical Strategy Returns vs. Benchmark")
                st.line_chart(
                    backtest_df[["Buy & Hold (Market)", "ML Algorithmic Strategy"]]
                )

                # Display underlying statistical model features for your presentation
                st.write("#### Statistical Feature Importance Breakdown")
                importances = model.feature_importances_
                feat_imp_df = pd.DataFrame(
                    {
                        "Feature Matrix Component": feature_columns,
                        "Importance Weight": [f"{val:.2%}" for val in importances],
                    }
                ).set_index("Feature Matrix Component")
                st.dataframe(feat_imp_df)

            else:
                st.warning(
                    "Insufficient overlapping data metrics available to fit machine learning frames."
                )

    else:
        st.error(
            "No overlapping asset data found for the designated date parameter."
        )
else:
    st.warning(
        "Please specify at least one market asset in the sidebar controller to generate analytical modeling."
    )
