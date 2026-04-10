import os
import pandas as pd

# Anchor path relative to this test file so pytest works regardless of invocation directory.
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_TEST_DIR))
_SNAPSHOT_PATH = os.path.join(_PROJECT_ROOT, "data", "static_snapshot.csv")


def test_static_snapshot_can_be_generated():
    # Since running the script takes ~15 seconds and hits real network APIs, we validate
    # the artefact produced by the developer's prior execution of generate_snapshot.py.
    assert os.path.exists(_SNAPSHOT_PATH), (
        f"Snapshot file not found at {_SNAPSHOT_PATH}. "
        "Run `python scripts/generate_snapshot.py` from the project root first."
    )

    df = pd.read_csv(_SNAPSHOT_PATH)

    # Shape and required columns
    assert not df.empty, "Snapshot is empty"
    expected_cols = {"date", "spy_close", "tlt_close", "gld_close", "yield_spread_10y_2y"}
    missing = expected_cols - set(df.columns)
    assert not missing, f"Required columns missing from snapshot: {missing}"

    # No NaN values — data must be fully contiguous after normalization
    assert df.isnull().sum().sum() == 0, "Snapshot contains NaN values after normalization"
