import pytest
import pandas as pd
import numpy as np
from green_rock.domain.quant_model import train_and_predict_rf

def test_train_and_predict_rf_importances_format():
    """
    [P0] Verify that train_and_predict_rf returns a dictionary of importances 
    mapping feature names to floats.
    """
    # GIVEN a dataframe with features and target
    df = pd.DataFrame({
        "feature1": range(10),
        "feature2": range(10, 20),
        "baseline_regime": ["Low"] * 5 + ["High"] * 5
    })
    
    # WHEN training and predicting
    _, importances, _ = train_and_predict_rf(df, feature_cols=["feature1", "feature2"], test_ratio=0.5)
    
    # THEN importances should be a dict with correct keys
    assert isinstance(importances, dict)
    assert set(importances.keys()) == {"feature1", "feature2"}
    assert all(isinstance(v, float) for v in importances.values())

def test_train_and_predict_rf_empty_features():
    """
    [P1] Verify that train_and_predict_rf raises ValueError for empty feature list.
    """
    df = pd.DataFrame({"baseline_regime": ["Low"] * 10})
    
    with pytest.raises(ValueError, match="feature_cols must be a non-empty list"):
        train_and_predict_rf(df, feature_cols=[], test_ratio=0.5)
