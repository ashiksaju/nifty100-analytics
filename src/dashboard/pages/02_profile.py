import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_financial_history,
    get_pros_cons,
)


def show():

    st.title(" COMPANY PROFILE")

    companies = get_companies()

    options = sorted(
        companies["company_name"].tolist()
    )

    selected_company = st.selectbox(
        "Search Company",
        options,
    )

    company = companies[
        companies["company_name"] == selected_company
    ].iloc[0]

    

    st.success(
        f"Selected Company: {selected_company}"
    )

    st.subheader(company["company_name"])

    st.write("**Company ID:**", company["company_id"])

    st.write("**Peer Group:**", company["peer_group_name"])

    st.write("**Website:**", company["website"])

    st.write("**About Company:**")

    st.write(company["about_company"])

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
     st.metric(
        "ROE %",
        round(company["roe_percentage_y"], 2),
    )

    with kpi2:
     st.metric(
        "ROCE %",
        round(company["roce_percentage_y"], 2),
    )

    with kpi3:
     st.metric(
        "Net Profit Margin %",
        round(float(company["net_profit_margin_pct"]), 2),
    )

    kpi4, kpi5, kpi6 = st.columns(3)

    with kpi4:
     st.metric(
        "Debt / Equity",
        round(float(company["debt_to_equity"]), 2),
    )

    with kpi5:
     st.metric(
        "Revenue CAGR (5Y)",
        round(float(company["revenue_cagr_5yr"]), 2),
    )

    with kpi6:
     st.metric(
        "Free Cash Flow",
        round(float(company["free_cash_flow_cr"]), 2),
    )

    history = get_pl(
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

    chart_data = history.melt(
    id_vars="year",
    value_vars=[
        "sales",
        "net_profit",
    ],
    var_name="Metric",
    value_name="Value",
)

    fig = px.bar(
    chart_data,
    x="year",
    y="Value",
    color="Metric",
    barmode="group",
    title="Revenue vs Net Profit",
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)
    pros_cons = get_pros_cons(
    company["company_id"]
)

    st.subheader(" PROS &  CONS")

    left, right = st.columns(2)

    with left:
     st.markdown("### ✅ Pros")

    for value in pros_cons["pros"].dropna():

        st.success(value)

    with right:
     st.markdown("### ⚠️ Cons")

    for value in pros_cons["cons"].dropna():

        st.error(value)
    history = get_financial_history(
    company["company_id"]
)
    history["roe_percentage"] = pd.to_numeric(
    history["roe_percentage"],
    errors="coerce",
)

    history["roce_percentage"] = pd.to_numeric(
    history["roce_percentage"],
    errors="coerce",
)

    line_data = history.melt(
    id_vars="year",
    value_vars=[
        "roe_percentage",
        "roce_percentage",
    ],
    var_name="Metric",
    value_name="Value",
)

    fig2 = px.line(
    line_data,
    x="year",
    y="Value",
    color="Metric",
    markers=True,
    title="ROE vs ROCE (10 Year Trend)",
)

    st.plotly_chart(
    fig2,
    use_container_width=True,
)