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

     roe = company["roe_percentage_y"]

    if pd.isna(roe):
        roe = "N/A"
    else:
        roe = round(float(roe), 2)

    st.metric(
        "ROE %",
        roe,
    )


    with kpi2:

     roce = company["roce_percentage_y"]

    if pd.isna(roce):
        roce = "N/A"
    else:
        roce = round(float(roce), 2)

    st.metric(
        "ROCE %",
        roce,
    )


    with kpi3:

     net_profit_margin = company["net_profit_margin_pct"]

    if pd.isna(net_profit_margin):
        net_profit_margin = "N/A"
    else:
        net_profit_margin = round(float(net_profit_margin), 2)

    st.metric(
        "Net Profit Margin %",
        net_profit_margin,
    )


    kpi4, kpi5, kpi6 = st.columns(3)

    with kpi4:

     debt_to_equity = company["debt_to_equity"]

    if pd.isna(debt_to_equity):
        debt_to_equity = "N/A"
    else:
        debt_to_equity = round(float(debt_to_equity), 2)

    st.metric(
        "Debt / Equity",
        debt_to_equity,
    )
    with kpi5:

     revenue_cagr = company["revenue_cagr_5yr"]

    if pd.isna(revenue_cagr):
        revenue_cagr = "N/A"
    else:
        revenue_cagr = round(float(revenue_cagr), 2)

    st.metric(
        "Revenue CAGR (5Y)",
        revenue_cagr,
    )


    with kpi6:

     free_cash_flow = company["free_cash_flow_cr"]

    if pd.isna(free_cash_flow):
        free_cash_flow = "N/A"
    else:
        free_cash_flow = round(float(free_cash_flow), 2)

    st.metric(
        "Free Cash Flow",
        free_cash_flow,
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
    st.write("Company ID:", company["company_id"])
    st.write("Selected Company ID:", company["company_id"])
    pros_cons = get_pros_cons(
    company["company_id"]
)
    if pros_cons.empty:
      st.info("No Pros & Cons available for this company.")
    else:
      st.subheader("PROS & CONS")

    left, right = st.columns(2)

    with left:
        st.markdown("### ✅ Pros")
        for value in pros_cons["pros"].dropna():
            st.success(value)

    with right:
        st.markdown("### ⚠️ Cons")
        for value in pros_cons["cons"].dropna():
            st.error(value)

    st.subheader(" PROS &  CONS")
    st.write(pros_cons)
    st.write(pros_cons["pros"].tolist())

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
    