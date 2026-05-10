import pandas as pd
from streamlit.testing.v1 import AppTest
from pathlib import Path
from unittest.mock import patch

def test_streamlit_app_boot_and_layout():
    """Verify application launches and uses layout='wide' AC 1, 3."""
    root = Path(__file__).parent.parent.parent
    app_path = root / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"
    
    with patch("green_rock.entrypoints.streamlit_app.DataPipeline") as MockPipeline, \
         patch("green_rock.domain.quant_model.train_and_predict_rf") as MockTrain:
        
        mock_dates = pd.date_range("2023-01-01", periods=100)
        
        mock_instance = MockPipeline.return_value
        mock_instance.run_pipeline.return_value = (
            pd.DataFrame({"spy_close": range(100)}, index=mock_dates), 
            "LIVE", 
            None,
            None
        )
        
        MockTrain.return_value = (
            pd.DataFrame({"spy_close": range(100), "baseline_regime": ["Low"]*100}, index=mock_dates), 
            None,
            None
        )

        at = AppTest.from_file(str(app_path))
        at.run(timeout=10)
        
        assert not at.exception, f"Streamlit app raised an exception on boot: {at.exception}"
        
        content = app_path.read_text()
        assert "layout=\"wide\"" in content or "layout='wide'" in content, "layout='wide' not found in entrypoint source"
