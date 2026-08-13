import streamlit as st
import importlib

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "HOME": "01_home",
    "COMPANY PROFILE": "02_profile",
    "SCREENER": "03_screener",
    "PEER COMPARISON": "04_peers",
    "TREND ANALYSIS": "05_trends",
    "SECTOR ANALYSIS": "06_sectors",
    "CAPITAL ALLOCATION": "07_capital",
    "ANNUAL REPORTS": "08_reports",
}

st.sidebar.title("Navigation")

selection = st.sidebar.radio(
    "Go to",
    list(PAGES.keys())
)

module = importlib.import_module(
    f"src.dashboard.pages.{PAGES[selection]}"
)

module.show()