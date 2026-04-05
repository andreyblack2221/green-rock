import sys
import os

# Ensure src/ is in the PYTHONPATH so Streamlit Cloud can import green_rock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from green_rock.entrypoints import streamlit_app

if __name__ == "__main__":
    streamlit_app.main()
