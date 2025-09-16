# Pair Monitor Backend (FastAPI)

Run locally:
1. Create virtualenv: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -r requirements.txt`
3. Run: `uvicorn api:app --reload --host 0.0.0.0 --port 8000`

Notes:
- yfinance is used for convenience in this demo. Replace with a paid provider for production.
- The analyze endpoint expects JSON: {"ticker_a":"AAPL", "ticker_b":"MSFT"}
