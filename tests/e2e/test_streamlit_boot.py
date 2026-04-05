from streamlit.testing.v1 import AppTest
from pathlib import Path

def test_streamlit_app_boot_and_layout():
    """Verify application launches and uses layout='wide' AC 1, 3."""
    root = Path(__file__).parent.parent.parent
    app_path = root / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"
    
    at = AppTest.from_file(str(app_path))
    at.run()
    
    assert not at.exception, "Streamlit app raised an exception on boot"
    
    content = app_path.read_text()
    assert "layout=\"wide\"" in content or "layout='wide'" in content, "layout='wide' not found in entrypoint source"
