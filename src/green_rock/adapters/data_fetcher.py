import yfinance as yf
import pandas_datareader as pdr
import pandas as pd
from datetime import datetime
import concurrent.futures
import time
import warnings

def fetch_yfinance_data(tickers, start_date, end_date):
    """Fetches daily Close prices from yfinance and formats columns into snake_case."""
    dfs = []
    for t in tickers:
        try:
            tkr = yf.Ticker(t)
            df = tkr.history(start=start_date, end=end_date)
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch {t} from yfinance. Original error: {exc}") from exc

        if df.empty:
            warnings.warn(
                f"Ticker '{t}' returned an empty DataFrame — it will be excluded from the merge.",
                RuntimeWarning,
                stacklevel=2,
            )
            continue

        df = df[["Close"]].copy()
        df.columns = [f"{t.lower()}_close"]
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    prices = pd.concat(dfs, axis=1)
    return prices

def fetch_fred_data(series_id, col_name, start_date, end_date):
    """Fetches a FRED series via pandas_datareader."""
    try:
        df = pdr.get_data_fred(series_id, start=start_date, end=end_date)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch FRED series '{series_id}'. Original error: {exc}") from exc
    df.columns = [col_name]
    return df

class DataFetcher:
    """Adapter to fetch live financial data with timeout mechanism."""
    
    def fetch_live_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches prices and yields from Yahoo Finance and FRED, merges them, and calculates
        rolling 20-day annualised volatility for SPY. Enforces a hard 1.9s wall-clock deadline
        shared across both parallel API calls to guarantee the <2s fallback requirement.
        On timeout, raises RuntimeError so the calling service layer triggers the cached-data
        fallback path.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_prices = executor.submit(fetch_yfinance_data, ["SPY", "TLT", "GLD"], start_date, end_date)
            future_yield = executor.submit(fetch_fred_data, "T10Y2Y", "yield_spread_10y_2y", start_date, end_date)
            
            try:
                # Use a shared wall-clock deadline so both futures share the 1.9s budget,
                # not each getting 1.9s independently (which could sum to 3.8s).
                _deadline = time.monotonic() + 1.9
                prices_df = future_prices.result(timeout=max(0.0, _deadline - time.monotonic()))
                yield_df = future_yield.result(timeout=max(0.0, _deadline - time.monotonic()))
            except concurrent.futures.TimeoutError as exc:
                raise RuntimeError("Data fetch timed out (> 1.9s wall-clock).") from exc
            except Exception as exc:
                raise RuntimeError(f"Data fetch failed: {exc}") from exc
                
        if prices_df.empty:
            raise RuntimeError("No price data fetched.")
            
        if prices_df.index.tz is not None:
            prices_df.index = prices_df.index.tz_convert(None)
            
        if yield_df.index.tz is not None:
            yield_df.index = yield_df.index.tz_convert(None)
            
        merged = pd.merge(prices_df, yield_df, left_index=True, right_index=True, how="outer")
        
        merged.index = pd.to_datetime(merged.index).normalize()
        merged.index.name = "date"
        
        merged = merged.dropna(how="all").ffill(limit=5).dropna()
        
        # Calculate rolling volatility
        if "spy_close" in merged.columns and len(merged) >= 20:
            merged["spy_volatility_20d"] = merged["spy_close"].pct_change().rolling(20).std() * (252 ** 0.5)
        else:
            merged["spy_volatility_20d"] = 0.0
            
        return merged
