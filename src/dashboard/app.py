import streamlit as st
import importlib

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "🏠 Home": "01_home",
    "🏢 Company Profile": "02_profile",
    "🔍 Screener": "03_screener",
    "👥 Peer Comparison": "04_peers",
    "📈 Trend Analysis": "05_trends",
    "🏭 Sector Analysis": "06_sectors",
    "💰 Capital Allocation": "07_capital",
    "📄 Annual Reports": "08_reports",
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