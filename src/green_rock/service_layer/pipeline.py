import datetime
import pandas as pd
from typing import Tuple, Optional
from green_rock.adapters.data_fetcher import DataFetcher
from green_rock.adapters.file_repository import FileRepository

class DataPipeline:
    """Orchestrates data fetching with fallback mechanism."""
    
    def __init__(
        self,
        data_fetcher: Optional[DataFetcher] = None,
        file_repository: Optional[FileRepository] = None,
    ) -> None:
        self.data_fetcher = data_fetcher or DataFetcher()
        self.file_repository = file_repository or FileRepository()

    def get_data(self, start_date: str = "2010-01-01", end_date: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """
        Attempts to fetch live data. On failure (timeout or network error),
        falls back to reading from the snapshot.
        Returns a tuple: (DataFrame, source_status)
        where source_status is 'LIVE' or 'CACHED'.
        """
        if not end_date:
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        try:
            df = self.data_fetcher.fetch_live_data(start_date, end_date)
            return df, "LIVE"
        except (RuntimeError, OSError, ValueError, TimeoutError) as exc:
            print(f"Live data fetch failed: {exc}. Falling back to cached data.")
            try:
                df = self.file_repository.read_snapshot()
                return df, "CACHED"
            except Exception as inner_exc:
                raise RuntimeError(
                    f"Fatal error: Unable to fetch live data ({exc}) and unable to read snapshot ({inner_exc})."
                ) from inner_exc

    def run_pipeline(
        self,
        start_date: str = "2010-01-01",
        end_date: Optional[str] = None,
        compute_baseline: bool = True,
        compute_rf: bool = False,
        rf_features: Optional[list[str]] = None
    ) -> Tuple[pd.DataFrame, str, Optional[dict[str, float]], Optional[dict]]:
        """
        Orchestrates full fetching and domain modeling flow, including machine learning if requested.
        """
        if compute_rf and not compute_baseline:
            raise ValueError("compute_baseline must be True if compute_rf is True (RF requires baseline_regime target).")
            
        df, status = self.get_data(start_date, end_date)
        
        rf_importances = None
        
        if compute_baseline:
            from green_rock.domain.quant_model import calculate_baseline_regime
            df = calculate_baseline_regime(df)
            
        if compute_rf:
            if not rf_features:
                raise ValueError("rf_features must be a non-empty list of strings if compute_rf is True.")
            from green_rock.domain.quant_model import train_and_predict_rf
            df, rf_importances, clf = train_and_predict_rf(
                df=df,
                feature_cols=rf_features,
                target_col="baseline_regime"
            )
            
        return df, status, rf_importances, None

    def compute_ml_analysis(
        self,
        df: pd.DataFrame,
        rf_features: Optional[list[str]] = None,
        target_col: str = "baseline_regime"
    ) -> Tuple[pd.DataFrame, Optional[dict[str, float]], dict, Optional[dict], pd.DataFrame]:
        """
        Runs ML analysis: trains RF classifier and computes comparative metrics.

        Args:
            df: DataFrame with baseline_regime already computed.
            rf_features: List of feature column names for the RF model.
            target_col: Target column name for the RF model.

        Returns:
            Tuple of (df_with_predictions, feature_importances, comparative_metrics, xai_attribution, strategy_returns).
        """
        if rf_features is None:
            rf_features = ["spy_close", "tlt_close", "gld_close", "yield_spread_10y_2y", "spy_volatility_20d"]
            
        from green_rock.domain.quant_model import train_and_predict_rf, calculate_comparative_metrics, calculate_daily_xai_attribution, calculate_strategy_returns
        df, importances, clf = train_and_predict_rf(
            df=df,
            feature_cols=rf_features,
            target_col=target_col
        )
        comparative_metrics = calculate_comparative_metrics(df)
        
        # Calculate strategy returns / benchmarks
        try:
            raw_sr = calculate_strategy_returns(df)
            
            def safe_pct(val):
                return (val * 100.0) if val is not None else None
                
            strategy_returns = pd.DataFrame({
                "Strategy": ["Baseline MA", "Random Forest", "60/40 Portfolio", "S&P 500"],
                "Cumulative Return": [
                    safe_pct(raw_sr.get('baseline_cumulative')),
                    safe_pct(raw_sr.get('rf_cumulative')),
                    safe_pct(raw_sr.get('benchmark_60_40')),
                    safe_pct(raw_sr.get('benchmark_spy'))
                ],
                "Max Drawdown": [
                    safe_pct(raw_sr.get('baseline_max_drawdown')),
                    safe_pct(raw_sr.get('rf_max_drawdown')),
                    safe_pct(raw_sr.get('benchmark_60_40_max_drawdown')),
                    safe_pct(raw_sr.get('benchmark_spy_max_drawdown'))
                ]
            })
        except KeyError:
            strategy_returns = pd.DataFrame()
        
        xai_attribution = None
        test_df = df[df["is_test"]].dropna(subset=rf_features)
        if not test_df.empty:
            latest_row = test_df.iloc[[-1]]
            xai_attribution = calculate_daily_xai_attribution(clf, latest_row, rf_features)
            
        return df, importances, comparative_metrics, xai_attribution, strategy_returns
