import os
from typing import Optional
import pandas as pd

class FileRepository:
    """Adapter to read offline static snapshot data."""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = data_dir
        else:
            # Default points to project root data directory
            _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPT_DIR)))
            self.data_dir = os.path.join(_PROJECT_ROOT, "data")

    def read_snapshot(self, filename: str = "static_snapshot.csv") -> pd.DataFrame:
        """Reads a CSV snapshot into a Pandas DataFrame."""
        file_path = os.path.join(self.data_dir, filename)
        
        df = pd.read_csv(file_path, index_col="date", parse_dates=True)
        # Calculate trailing volatility locally as in data_fetcher
        if "spy_close" in df.columns and len(df) >= 20:
            df["spy_volatility_20d"] = df["spy_close"].pct_change().rolling(20).std() * (252 ** 0.5)
        else:
            df["spy_volatility_20d"] = 0.0
            
        return df
