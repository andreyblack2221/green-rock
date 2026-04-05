import streamlit as st

def main():
    st.set_page_config(
        page_title="Green-Rock Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Green-Rock Adaptive ETF Portfolio")
    st.write("Welcome to the institutional baseline dashboard. Institutional Light Classic applied.")

if __name__ == "__main__":
    main()
