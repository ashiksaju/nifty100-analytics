import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import (
    get_sector_data,
)


def show():

    st.title("SECTOR ANALYSIS")

    data = get_sector_data()
    

    sector = st.selectbox(
    "Select Sector",
    sorted(data["broad_sector"].unique())
)

    filtered = data[
    data["broad_sector"] == sector
]
    filtered["sales"] = filtered["sales"].astype(float)

    filtered["roe_percentage"] = filtered["roe_percentage"].astype(float)

    filtered["market_cap_crore"] = filtered["market_cap_crore"].astype(float)

    fig = px.scatter(
    filtered,
    x="sales",
    y="roe_percentage",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    title="Sector Bubble Chart",
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)
    median_df = filtered[
    [
        "sales",
        "roe_percentage",
        "market_cap_crore",
    ]
    ].median()

    median_df = median_df.reset_index()

    median_df.columns = [
    "KPI",
    "Median",
]

    fig = px.bar(
    median_df,
    x="KPI",
    y="Median",
    title="Sector Median KPIs",
    text_auto=".2f",
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)