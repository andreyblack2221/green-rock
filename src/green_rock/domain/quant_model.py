"""
Quantitative Domain Models for Green-Rock
"""

import numpy as np
import pandas as pd


def calculate_baseline_regime(df: pd.DataFrame, short_window: int = 50, long_window: int = 200) -> pd.DataFrame:
    """
    Calculates a simple Moving-Average crossover to establish a baseline market risk regime.

    Mathematical Rules:
    1. Short MA = df['spy_close'].rolling(window=short_window).mean()
    2. Long MA  = df['spy_close'].rolling(window=long_window).mean()
    3. Ratio bounds: 1.01 (bullish threshold) and 0.99 (bearish threshold)
    4. Regime Mapping:
       - Short MA > Long MA * 1.01  →  "Low"    Risk  (bullish)
       - Short MA < Long MA * 0.99  →  "High"   Risk  (bearish)
       - Otherwise                  →  "Medium" Risk  (neutral / transitional)
    5. Warm-up: rows where either MA cannot yet be calculated receive np.nan.

    Args:
        df: Pandas DataFrame containing a 'spy_close' column with a monotonically
            increasing, non-duplicate index (typically a timezone-normalised DatetimeIndex).
        short_window: Positive integer window size for the short moving average.
            Must be strictly less than long_window.
        long_window: Positive integer window size for the long moving average.
            Must be strictly greater than short_window.

    Returns:
        A new DataFrame (copy of input) with three additional columns:
        - 'short_ma'        — trailing short-window moving average of spy_close
        - 'long_ma'         — trailing long-window moving average of spy_close
        - 'baseline_regime' — "Low", "Medium", or "High" for fully warmed-up rows;
          np.nan for the first (long_window - 1) warm-up rows.

    Raises:
        ValueError: If short_window or long_window are not positive integers.
        ValueError: If short_window >= long_window.
        ValueError: If len(df) < long_window (no row would ever receive a classification).
        KeyError:   If 'spy_close' is not found in the input DataFrame.
    """
    if not isinstance(short_window, int) or not isinstance(long_window, int):
        raise ValueError("short_window and long_window must be integers.")
    if short_window <= 0 or long_window <= 0:
        raise ValueError("short_window and long_window must be positive integers.")
    if short_window >= long_window:
        raise ValueError(
            f"short_window ({short_window}) must be strictly less than long_window ({long_window})."
        )
    if len(df) < long_window:
        raise ValueError(
            f"DataFrame has {len(df)} rows, which is fewer than long_window ({long_window}). "
            "Provide at least long_window rows to produce any valid classifications."
        )
    if "spy_close" not in df.columns:
        raise KeyError("'spy_close' column is missing from the input DataFrame.")

    result_df = df.copy()

    result_df["short_ma"] = result_df["spy_close"].rolling(window=short_window).mean()
    result_df["long_ma"] = result_df["spy_close"].rolling(window=long_window).mean()

    # Assign regime based on ratio thresholds
    result_df["baseline_regime"] = "Medium"
    result_df.loc[result_df["short_ma"] > result_df["long_ma"] * 1.01, "baseline_regime"] = "Low"
    result_df.loc[result_df["short_ma"] < result_df["long_ma"] * 0.99, "baseline_regime"] = "High"

    # Nullify warm-up rows where either MA is not yet calculable
    warm_up_mask = result_df["short_ma"].isna() | result_df["long_ma"].isna()
    result_df.loc[warm_up_mask, "baseline_regime"] = np.nan

    return result_df
