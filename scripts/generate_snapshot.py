import os
import yfinance as yf
import pandas_datareader as pdr
import pandas as pd
from datetime import datetime

# Anchor all paths relative to this script file so the script works
# regardless of which directory it is invoked from.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)


def fetch_yfinance_data(tickers, start_date, end_date):
    """Fetches daily Close prices from yfinance and formats columns into snake_case.

    Returns an empty DataFrame and prints a warning if all tickers fail.
    Raises RuntimeError with a clear message on unexpected network errors.
    """
    dfs = []
    for t in tickers:
        print(f"Fetching {t} from yfinance...")
        try:
            tkr = yf.Ticker(t)
            df = tkr.history(start=start_date, end=end_date)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch {t} from yfinance. "
                f"Check your network connection and try again. Original error: {exc}"
            ) from exc

        if df.empty:
            print(f"Warning: No data returned for {t} — ticker may be invalid or delisted.")
            continue

        # Keep only the Close price and rename to snake_case
        df = df[["Close"]].copy()
        df.columns = [f"{t.lower()}_close"]
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    prices = pd.concat(dfs, axis=1)
    return prices


def fetch_fred_data(series_id, col_name, start_date, end_date):
    """Fetches a FRED series via pandas_datareader.

    Raises RuntimeError with a clear message on network or series errors.
    """
    print(f"Fetching {series_id} from FRED...")
    try:
        df = pdr.get_data_fred(series_id, start=start_date, end=end_date)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch FRED series '{series_id}'. "
            f"Check your network connection and that the series ID is valid. Original error: {exc}"
        ) from exc

    df.columns = [col_name]
    return df


def generate_snapshot():
    # Define time horizon
    start_date = "2010-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    # 1. Fetch yfinance prices
    prices_df = fetch_yfinance_data(["SPY", "TLT", "GLD"], start_date, end_date)

    # Guard: abort early with a clear error if all price tickers failed
    if prices_df.empty:
        raise RuntimeError(
            "No price data was fetched for any ticker (SPY, TLT, GLD). "
            "The snapshot cannot be generated. Check the warnings above."
        )

    if prices_df.index.tz is not None:
        prices_df.index = prices_df.index.tz_convert(None)

    # 2. Fetch FRED yield curve data
    yield_df = fetch_fred_data("T10Y2Y", "yield_spread_10y_2y", start_date, end_date)
    if yield_df.index.tz is not None:
        yield_df.index = yield_df.index.tz_convert(None)

    # 3. Merge data (outer join to retain all dates from both sources)
    print("Merging data...")
    merged = pd.merge(prices_df, yield_df, left_index=True, right_index=True, how="outer")

    # 4. Standardize index to YYYY-MM-DD naive dates
    merged.index = pd.to_datetime(merged.index).normalize()
    merged.index.name = "date"

    # 5. Clean missing data
    # Order matters: first drop rows where ALL columns are NaN (genuine empty rows),
    # then forward-fill remaining partial gaps (weekends, holidays).
    # limit=5 caps filling at 5 calendar days — enough to cover any normal weekend/holiday
    # stretch. Gaps longer than 5 days indicate an upstream data outage and will surface
    # as NaN rows (caught by the validation step below).
    merged = merged.dropna(how="all").ffill(limit=5).dropna()

    # 6. Save to anchored output path
    output_dir = os.path.join(_PROJECT_ROOT, "data")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "static_snapshot.csv")

    merged.to_csv(out_file, encoding="utf-8")
    print(
        f"Snapshot successfully saved to {out_file} "
        f"with {len(merged)} rows and {len(merged.columns)} columns."
    )


if __name__ == "__main__":
    generate_snapshot()
