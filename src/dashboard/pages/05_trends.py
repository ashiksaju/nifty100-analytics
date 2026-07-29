import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_profit_loss,
)


def show():

    st.title("TREND ANALYSIS")

    companies = get_companies()

    selected_company = st.selectbox(
        "Select Company",
        sorted(companies["company_name"])
    )

    company = companies[
        companies["company_name"] == selected_company
    ].iloc[0]

    history = get_profit_loss(
    company["company_id"]
)

    history["sales"] = pd.to_numeric(
    history["sales"],
    errors="coerce",
)

    history["net_profit"] = pd.to_numeric(
    history["net_profit"],
    errors="coerce",
)

    history["eps"] = pd.to_numeric(
    history["eps"],
    errors="coerce",
)
    metrics = st.multiselect(
    "Select up to 3 metrics",
    [
        "sales",
        "net_profit",
        "eps",
    ],
    default=["sales"],
    max_selections=3,
)

    fig = px.line()

    for metric in metrics:

     fig.add_scatter(
        x=history["year"],
        y=history[metric],
        mode="lines+markers",
        name=metric.replace("_", " ").title(),
    )

    if len(metrics) > 0:

     metric = metrics[0]

    history["YoY"] = (
        history[metric]
        .pct_change()
        .mul(100)
        .round(2)
    )

    for i in range(1, len(history)):

        fig.add_annotation(
            x=history.iloc[i]["year"],
            y=history.iloc[i][metric],
            text=f'{history.iloc[i]["YoY"]:.2f}%',
            showarrow=True,
            arrowhead=1,
            yshift=15,
        )

    fig.update_layout(
    title="10-Year Trend Analysis",
    xaxis_title="Year",
    yaxis_title="Value",
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)

    

   