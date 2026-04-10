"""
Pytest configuration.
"""

import sys
import os

# Ensure src/ is in the PYTHONPATH so tests can import from green_rock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Ensure the root directory is in the PYTHONPATH so tests can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
