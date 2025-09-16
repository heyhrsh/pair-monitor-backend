from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core import analyze_pair

app = FastAPI(title="Pair Monitor Backend")

class PairRequest(BaseModel):
    ticker_a: str
    ticker_b: str
    window_days: int = 60
    corr_threshold: float = 0.75

@app.post("/analyze")
def analyze(req: PairRequest):
    # Simple retry logic for yfinance on cold starts
    for attempt in range(2):
        try:
            r = analyze_pair(req.ticker_a.upper(), req.ticker_b.upper(), window_days=req.window_days, corr_threshold=req.corr_threshold)
            return r
        except Exception as e:
            if attempt == 0: # If it's the first attempt, wait a bit and retry
                import time
                time.sleep(2)
                continue
            else: # If it fails on the second attempt, raise the error
                raise HTTPException(status_code=400, detail=str(e))
