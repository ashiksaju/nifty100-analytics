import streamlit as st

from src.dashboard.utils.db import get_annual_reports


def show():

    st.title("ANNUAL REPORTS")

    reports = get_annual_reports()

    company = st.selectbox(
        "Select Company",
        sorted(reports["company_id"].unique())
    )

    filtered = reports[
        reports["company_id"] == company
    ]

    st.subheader(f"{company} Annual Reports")

    for _, row in filtered.iterrows():

        st.markdown(
    f"**{row['Year']}** — [📄 Open Annual Report]({row['Annual_Report']})"
)