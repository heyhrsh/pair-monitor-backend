from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import pearsonr

def get_daily_closes(ticker: str, lookback_days: int = 90) -> pd.Series:
    end = datetime.utcnow().date()
    start = end - timedelta(days=lookback_days)
    df = yf.download(ticker, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(), progress=False)
    if 'Close' not in df.columns:
        raise RuntimeError(f"No close data for {ticker}")
    series = df['Close'].dropna()
    series.index = pd.to_datetime(series.index).normalize()
    series.name = ticker
    return series

def align_closes(a: pd.Series, b: pd.Series, min_days: int = 40) -> pd.DataFrame:
    df = pd.concat([a, b], axis=1, join='inner').dropna()
    if df.shape[0] < min_days:
        raise ValueError(f"Insufficient overlapping trading days: {df.shape[0]} (< {min_days})")
    df.columns = ['A', 'B']
    return df

def analyze_pair(ticker_a: str, ticker_b: str, window_days: int = 60, corr_threshold: float = 0.75):
    a = get_daily_closes(ticker_a, lookback_days=window_days + 40)
    b = get_daily_closes(ticker_b, lookback_days=window_days + 40)
    df = align_closes(a, b, min_days=10)
    df = df.sort_index()
    if df.shape[0] < window_days:
        raise ValueError(f"Not enough common trading days: {df.shape[0]} < {window_days}")
    df_window = df.iloc[-window_days:]
    corr, _p = pearsonr(df_window['A'].values, df_window['B'].values)
    if (df_window['B'] == 0).any():
        raise ZeroDivisionError("Share B has zero close value in window.")
    ratios = df_window['A'] / df_window['B']
    mu = ratios.mean()
    sigma = ratios.std(ddof=0)
    latest_ratio = ratios.iloc[-1]
    z = None
    if sigma == 0:
        z = float('nan')
    else:
        z = (latest_ratio - mu) / sigma
    result = {
        'ticker_a': ticker_a,
        'ticker_b': ticker_b,
        'corr': float(corr),
        'corr_pvalue': float(_p),
        'ratio_mean': float(mu),
        'ratio_std': float(sigma),
        'latest_ratio': float(latest_ratio),
        'z_score': float(z) if not np.isnan(z) else None,
        'window_days': window_days,
        'last_date': df_window.index[-1].strftime('%Y-%m-%d'),
    }
    result['corr_pass'] = bool(corr >= corr_threshold)
    result['signal'] = None
    if result['z_score'] is not None:
        if result['z_score'] >= 2.0:
            result['signal'] = 'UPPER'
        elif result['z_score'] <= -2.0:
            result['signal'] = 'LOWER'
    return result
