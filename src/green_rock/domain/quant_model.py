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

def train_and_predict_rf(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str = "baseline_regime",
    test_ratio: float = 0.2,
    random_state: int = 42
) -> tuple[pd.DataFrame, dict[str, float], object]:
    """
    Trains a deterministic RandomForestClassifier utilizing a strict time-based boundary.

    Args:
        df: Pandas DataFrame containing features and target column.
            The index should represent a strictly temporal order.
        feature_cols: List of column names to use as features.
        target_col: Column name containing the target risk regimes.
            Outputs are expected to map to "Low", "Medium", and "High".
        test_ratio: Float representing the proportion of the dataset to include in the test split.
        random_state: Hard-coded random seed to enforce deterministic results.

    Returns:
        A tuple containing:
        - A new DataFrame with predictions appended.
          Columns added:
              - 'is_test': Boolean mask where True indicates test set rows.
              - 'rf_prediction': Model prediction for test rows (NaN or empty for training rows).
        - A dictionary mapping feature names to their relative importance (float).
        - The fitted RandomForestClassifier model.
    """
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np

    if not feature_cols:
        raise ValueError("feature_cols must be a non-empty list of strings.")
        
    if not (0 < test_ratio < 1):
        raise ValueError("test_ratio must be strictly between 0 and 1.")
        
    if target_col in feature_cols:
        raise ValueError(f"Target column '{target_col}' cannot be in feature_cols to prevent data leakage.")
        
    missing_cols = set(feature_cols + [target_col]) - set(df.columns)
    if missing_cols:
        raise KeyError(f"Missing required columns in DataFrame: {missing_cols}")
    
    # Avoid mutating input
    result_df = df.copy()
    if not result_df.index.is_monotonic_increasing:
        result_df = result_df.sort_index()
    result_df["is_test"] = False
    result_df["rf_prediction"] = pd.Series(np.nan, index=result_df.index, dtype="object")
    
    # Calculate cutoff index for time-series split
    dataset_length = len(result_df)
    if dataset_length < 2:
        raise ValueError("DataFrame size too small to perform a train/test split.")
    test_size = int(round(dataset_length * test_ratio))
    split_idx = dataset_length - test_size
    
    if test_size == 0 or split_idx <= 0:
         raise ValueError("DataFrame size too small for test split.")
    
    result_df.iloc[split_idx:, result_df.columns.get_loc("is_test")] = True
    
    # Extract sets
    train_df = result_df.iloc[:split_idx]
    test_df = result_df.iloc[split_idx:]
    
    # Drop NaNs
    train_clean = train_df.dropna(subset=feature_cols + [target_col])
    
    if train_clean.empty:
         raise ValueError("Training set is empty after dropping NaNs.")
    
    X_train = train_clean[feature_cols]
    y_train = train_clean[target_col]
    
    valid_classes = {"Low", "Medium", "High"}
    if not set(y_train.unique()).issubset(valid_classes):
        raise ValueError(f"Target column must only contain {valid_classes}")
    
    # Instantiate deterministic classifier
    clf = RandomForestClassifier(random_state=random_state)
    clf.fit(X_train, y_train)
    
    importances = dict(zip(feature_cols, [float(x) for x in clf.feature_importances_]))
    importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    
    # Predict on test set
    test_clean_mask = test_df[feature_cols].notna().all(axis=1)
    
    if test_clean_mask.any():
         X_test = test_df.loc[test_clean_mask, feature_cols]
         predictions = clf.predict(X_test)
         # Assign back to result_df using iloc to avoid duplicate index issues
         test_clean_ilocs = np.where(test_clean_mask.values)[0] + split_idx
         result_df.iloc[test_clean_ilocs, result_df.columns.get_loc("rf_prediction")] = predictions

    return result_df, importances, clf

def calculate_daily_xai_attribution(clf, X_row: pd.DataFrame, feature_cols: list[str]) -> dict:
    """
    Calculates the XAI risk attribution waterfall components for the given prediction row.
    
    Contributions are always computed relative to the "High" risk class so that
    positive values mean risk-increasing and negative values mean risk-reducing,
    ensuring consistent color semantics in the Waterfall chart.
    
    Args:
        clf: Fitted RandomForestClassifier.
        X_row: A single-row DataFrame containing the features for the day.
        feature_cols: The list of feature column names.
        
    Returns:
        A dictionary containing:
            - 'base_value': The mean base probability of "High" risk across all trees.
            - '{feature_name}': The contribution of each feature to the "High" risk probability.
            - 'predicted_class': The predicted regime class.
    """
    import numpy as np
    if len(X_row) != 1:
        raise ValueError("X_row must be a single-row DataFrame")
    X_array = X_row[feature_cols].values
    predicted_class = clf.predict(X_array)[0]
    
    # Always compute contributions relative to "High" risk class
    # so positive = risk-increasing, negative = risk-reducing
    if "High" in clf.classes_:
        target_class_idx = np.where(clf.classes_ == "High")[0][0]
    else:
        target_class_idx = np.where(clf.classes_ == predicted_class)[0][0]
    
    n_features = len(feature_cols)
    contributions = np.zeros(n_features)
    base_value = 0.0
    
    for tree in clf.estimators_:
        path = tree.decision_path(X_array).indices
        
        root_node = path[0]
        root_value = tree.tree_.value[root_node][0]
        root_prob = root_value[target_class_idx] / np.sum(root_value)
        base_value += root_prob
        
        previous_prob = root_prob
        for node in path[1:]:
            current_value = tree.tree_.value[node][0]
            current_prob = current_value[target_class_idx] / np.sum(current_value)
            
            parent_node = path[np.where(path == node)[0][0] - 1]
            split_feature = tree.tree_.feature[parent_node]
            
            contributions[split_feature] += (current_prob - previous_prob)
            previous_prob = current_prob
            
    base_value /= clf.n_estimators
    contributions /= clf.n_estimators
    
    result = {
        "base_value": float(base_value),
        "predicted_class": predicted_class
    }
    
    for i, col in enumerate(feature_cols):
        result[col] = float(contributions[i])
        
    return result

def calculate_comparative_metrics(df: pd.DataFrame) -> dict:
    """
    Computes agreement/divergence between baseline and RF models over the test period.
    Returns:
        dict containing:
            - 'baseline_latest': str
            - 'rf_latest': str
            - 'agreement_rate': float (percentage of matching regimes in test set)
            - 'divergence_count': int (number of divergent predictions in test set)
            - 'total_test_days': int
    """
    required_cols = {"is_test", "rf_prediction", "baseline_regime"}
    if not required_cols.issubset(df.columns):
        return {}

    test_df = df[df["is_test"]].dropna(subset=["baseline_regime", "rf_prediction"])
    
    if test_df.empty:
        return {}
    
    baseline_latest = test_df["baseline_regime"].iloc[-1]
    rf_latest = test_df["rf_prediction"].iloc[-1]
    
    matches = (test_df["baseline_regime"] == test_df["rf_prediction"]).sum()
    total = len(test_df)
    
    agreement_rate = (matches / total) * 100 if total > 0 else 0.0
    divergence_count = total - matches
    
    return {
        "baseline_latest": baseline_latest,
        "rf_latest": rf_latest,
        "agreement_rate": float(agreement_rate),
        "divergence_count": int(divergence_count),
        "total_test_days": int(total)
    }

def calculate_strategy_returns(df: pd.DataFrame) -> dict:
    """
    Calculates portfolio returns based on dynamic risk regimes for both Baseline MA
    and Random Forest models, and compares them against static benchmarks.
    
    Weights mapping:
      - "Low" Risk (Equities-heavy): 70% SPY, 20% TLT, 10% GLD
      - "Medium" Risk (Balanced): 40% SPY, 40% TLT, 20% GLD
      - "High" Risk (Defensive): 20% SPY, 50% TLT, 30% GLD
      
    Args:
        df: DataFrame containing at least 'spy_close', 'tlt_close', 'gld_close',
            'baseline_regime', 'rf_prediction', and 'is_test'.
            
    Returns:
        A dictionary containing the cumulative returns for the four strategies:
        - 'baseline_cumulative': float
        - 'rf_cumulative': float
        - 'benchmark_60_40': float
        - 'benchmark_spy': float
    """
    required_cols = {"spy_close", "tlt_close", "gld_close", "baseline_regime", "rf_prediction", "is_test"}
    if not required_cols.issubset(df.columns):
        raise KeyError(f"Missing required columns. Expected: {required_cols}")
        
    # Weights for [SPY, TLT, GLD]
    weights_map = {
        "Low": np.array([0.70, 0.20, 0.10]),
        "Medium": np.array([0.40, 0.40, 0.20]),
        "High": np.array([0.20, 0.50, 0.30])
    }
    
    # Calculate daily simple returns (shift is handled by pct_change)
    returns_df = pd.DataFrame()
    returns_df["spy_ret"] = df["spy_close"].pct_change()
    returns_df["tlt_ret"] = df["tlt_close"].pct_change()
    returns_df["gld_ret"] = df["gld_close"].pct_change()
    returns_df["is_test"] = df["is_test"]
    returns_df["baseline_regime"] = df["baseline_regime"]
    returns_df["rf_prediction"] = df["rf_prediction"]
    
    # Filter to only test period. 
    # NOTE: The first day of the test period will have a return based on the last day of the train period.
    test_returns = returns_df[returns_df["is_test"]].copy()
    
    # For rows where regimes are NaN (if any), use Medium as a safe default, or handle gracefully.
    test_returns["baseline_regime"] = test_returns["baseline_regime"].fillna("Medium")
    test_returns["rf_prediction"] = test_returns["rf_prediction"].fillna("Medium")
    
    # Precompute weight arrays for vectorized operations
    # Shape: (N, 3)
    baseline_weights = np.array([weights_map[reg] for reg in test_returns["baseline_regime"]])
    rf_weights = np.array([weights_map[reg] for reg in test_returns["rf_prediction"]])
    
    # Daily returns array: shape (N, 3)
    asset_returns = test_returns[["spy_ret", "tlt_ret", "gld_ret"]].values
    
    # Replace NaNs in returns with 0 (e.g. if the very first row is NaN due to pct_change)
    asset_returns = np.nan_to_num(asset_returns)
    
    # Calculate daily portfolio returns
    test_returns["baseline_port_ret"] = np.sum(baseline_weights * asset_returns, axis=1)
    test_returns["rf_port_ret"] = np.sum(rf_weights * asset_returns, axis=1)
    
    # Benchmarks
    test_returns["bench_60_40_ret"] = np.sum(np.array([0.60, 0.40, 0.0]) * asset_returns, axis=1)
    test_returns["bench_spy_ret"] = asset_returns[:, 0] # 100% SPY
    
    # Cumulative Returns = product of (1 + daily_return) - 1
    baseline_cumulative = np.prod(1 + test_returns["baseline_port_ret"]) - 1
    rf_cumulative = np.prod(1 + test_returns["rf_port_ret"]) - 1
    benchmark_60_40 = np.prod(1 + test_returns["bench_60_40_ret"]) - 1
    benchmark_spy = np.prod(1 + test_returns["bench_spy_ret"]) - 1
    
    def get_max_drawdown(ret_series):
        cum_ret = (1 + ret_series).cumprod()
        running_max = cum_ret.cummax()
        drawdown = (running_max - cum_ret) / running_max
        return float(drawdown.max()) if not drawdown.empty else 0.0

    return {
        "baseline_cumulative": float(baseline_cumulative),
        "rf_cumulative": float(rf_cumulative),
        "benchmark_60_40": float(benchmark_60_40),
        "benchmark_spy": float(benchmark_spy),
        "baseline_max_drawdown": get_max_drawdown(test_returns["baseline_port_ret"]),
        "rf_max_drawdown": get_max_drawdown(test_returns["rf_port_ret"]),
        "benchmark_60_40_max_drawdown": get_max_drawdown(test_returns["bench_60_40_ret"]),
        "benchmark_spy_max_drawdown": get_max_drawdown(test_returns["bench_spy_ret"])
    }

