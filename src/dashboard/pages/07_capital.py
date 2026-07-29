import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_capital_allocation


def show():

    st.title("CAPITAL ALLOCATION")

    data = get_capital_allocation()

    fig = px.treemap(
        data,
        path=["capex_label", "company_name"],
        values="market_cap_crore",
        color="capex_label",
        title="Capital Allocation Patterns",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    pattern = st.selectbox(
        "Capital Allocation Pattern",
        sorted(data["capex_label"].unique())
    )

    st.subheader("Companies")

    st.dataframe(
        data[
            data["capex_label"] == pattern
        ][
            [
                "company_name",
                "market_cap_crore",
            ]
        ],
        use_container_width=True,
    )