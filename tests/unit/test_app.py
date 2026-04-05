def test_import_streamlit_app():
    try:
        from green_rock.entrypoints import streamlit_app
        assert streamlit_app.main is not None
    except ImportError as e:
        raise RuntimeError(f"Importing streamlit_app failed: {e}") from e
