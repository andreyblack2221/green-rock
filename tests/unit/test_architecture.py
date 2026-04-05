import os
from pathlib import Path

def test_project_structure():
    """Verify strictly required folders exist according to AC 2."""
    root = Path(__file__).parent.parent.parent
    src_dir = root / "src" / "green_rock"
    
    assert (src_dir / "adapters").is_dir(), "adapters directory missing"
    assert (src_dir / "domain").is_dir(), "domain directory missing"
    assert (src_dir / "service_layer").is_dir(), "service_layer directory missing"
    assert (src_dir / "entrypoints").is_dir(), "entrypoints directory missing"

    assert (root / ".streamlit").is_dir(), ".streamlit directory missing"
    assert (root / "data").is_dir(), "data directory missing"
    assert (root / "configs").is_dir(), "configs directory missing"
