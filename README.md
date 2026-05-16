# JSE-quant-dashboard
Live market comparison and risk analysis dashboard analyzing JSE banking sector capital flows
# JSE Banking Sector Market Analysis Dashboard
### Built by Mr. Ndwandwe

This is an interactive financial dashboard I built using Python and Streamlit to run live time-series tracking and risk analysis on major retail banks listed on the Johannesburg Stock Exchange (JSE).

## 🎯 The Research Question
I put this project together to test a specific market theory about what happens when a banking giant faces massive public backlash. Following the viral media coverage and data breach controversy surrounding Standard Bank, social media was filled with claims of people closing their accounts to shift to other banks. 

As a statistics student, I wanted to move past the rumors and check the actual numbers. I set up this app to investigate:
1. **The Hit:** Did the public backlash actually damage Standard Bank's (`SBK.JO`) equity performance in a measurable way?
2. **The Shift:** Did competitors like Capitec (`CPI.JO`) and FirstRand/FNB (`FSR.JO`) capture that fleeing market value, resulting in a visible upward spike in their stock prices during the scandal?

## 📊 How the Analytics Engine Works
- **Price Normalization (Base 100):** Comparing these stocks on raw share price is impossible—Capitec sits way up over R4,000 while FNB trades below R100. To fix this, the engine forces all selected stocks to start at a baseline of 100 on Day 1 (January 1, 2024). This lets you compare their pure percentage growth side-by-side on an even playing field.
- **Risk-Return Summary:** The app automatically calculates the Expected Mean Daily Return and Daily Volatility (Standard Deviation). This lets any analyst instantly see how much systematic risk shot up during the market panic.
- **Data Export:** To keep things open, I built in a download button that lets anyone pull the exact synchronized dataset they are looking at into a clean CSV file to run their own statistical tests.

## 🛠️ Tech Stack
- **Language:** Python
- **Frontend & Deployment:** Streamlit Community Cloud
- **Data Source:** Yahoo Finance API (`yfinance`)
- **Data Crunching:** Pandas & NumPy
