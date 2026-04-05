import os
from pathlib import Path
import re

def test_theme_configuration():
    """Verify Streamlit theme configuration according to AC 4."""
    root = Path(__file__).parent.parent.parent
    config_path = root / ".streamlit" / "config.toml"
    assert config_path.is_file(), "config.toml missing"
    
    content = config_path.read_text()
    
    # AC 4 criteria
    # White background, Slate Blue primary color, Charcoal text, Institutional Grey secondary backgrounds
    assert re.search(r'primaryColor\s*=\s*["\']\#1F3A5F["\']', content, re.IGNORECASE), "Deep Slate Blue primary color missing"
    assert re.search(r'backgroundColor\s*=\s*["\']\#FFFFFF["\']', content, re.IGNORECASE), "Pure White background missing"
    assert re.search(r'secondaryBackgroundColor\s*=\s*["\']\#F0F2F6["\']', content, re.IGNORECASE), "Light Institutional Grey secondary missing"
    assert re.search(r'textColor\s*=\s*["\']\#262730["\']', content, re.IGNORECASE), "High-Contrast Charcoal text missing"
    assert re.search(r'font\s*=\s*["\']sans serif["\']', content, re.IGNORECASE), "Sans serif font missing"
