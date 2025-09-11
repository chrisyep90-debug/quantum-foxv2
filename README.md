
# Quantum Fox — Active Trading Package (Dummy-Proof)

This package is a Streamlit web app that can connect to Alpaca (paper or live) to view charts, generate simple SMA signals, and place market/limit orders with optional take-profit and stop-loss child orders.

## How to launch (no command-line required if deploying to Streamlit Cloud)
1. Create a new GitHub repository named `quantum_fox`.
2. Upload the files from this package (`quantum_fox_app.py`, `requirements.txt`, `README.md`) to the repo (use GitHub web UI: "Add file" → "Upload files").
3. Go to https://streamlit.io/cloud and sign in with GitHub, then create a new app from your `quantum_fox` repo. Streamlit will install dependencies and launch the app.
4. Open the app URL in Safari on your iPhone and use **Share → Add to Home Screen** to create a pseudo-native app.

## How to use (paper trading recommended)
- In the left sidebar, enter your Alpaca **API KEY** and **SECRET**.
- Choose **paper** environment to test without real money.
- Enter a symbol, view the chart, and place market or limit orders.
- Use Take Profit / Stop Loss fields to create simple protective orders (implemented as separate orders).

## Safety and notes
- This app will place real orders when you use LIVE mode and provide live API keys. Only use LIVE mode if you know what you're doing.
- Always test extensively in PAPER mode first.
- Alpaca accounts and API keys are required for trading; get them at https://alpaca.markets/

