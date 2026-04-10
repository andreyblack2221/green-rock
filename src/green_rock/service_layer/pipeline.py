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
