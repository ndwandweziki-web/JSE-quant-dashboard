import pandas as pd
import streamlit as st
import yfinance as yf

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
    else:
        st.error(
            "No overlapping asset data found for the designated date parameter."
        )
else:
    st.warning(
        "Please specify at least one market asset in the sidebar controller to generate analytical modeling."
    )
