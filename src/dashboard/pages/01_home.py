import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_ratios
import plotly.express as px


from src.dashboard.utils.db import (
    get_ratios,
    get_sectors,
)

def show():

    st.title("HOME")

    st.markdown("---")

    
    ratios = get_ratios()
    sectors = get_sectors()

    
    selected_year = st.sidebar.selectbox(
        "Select Year",
        sorted(
            ratios["year"].dropna().unique(),
            reverse=True,
        ),
    )

    
    numeric_columns = [
        "roe_percentage",
        "roce_percentage",
        "debt_to_equity",
        "revenue_cagr_5yr",
    ]

    for column in numeric_columns:
        ratios[column] = pd.to_numeric(
            ratios[column],
            errors="coerce",
        )

    
    filtered_ratios = ratios[
        ratios["year"] == selected_year
    ].copy()

    
    top5 = (
        filtered_ratios
        .sort_values(
            "composite_quality_score",
            ascending=False,
        )
        .drop_duplicates("company_id")
        .head(5)[
            [
                "company_id",
                "company_name",
                "composite_quality_score",
                "quality_rank",
            ]
        ]
    )

    
    average_roe = filtered_ratios["roe_percentage"].mean()

    median_roce = filtered_ratios["roce_percentage"].median()

    median_de = filtered_ratios["debt_to_equity"].median()

    total_companies = filtered_ratios["company_id"].nunique()

    median_revenue_cagr = filtered_ratios[
    "revenue_cagr_5yr"
    ].median()

    debt_free = (
    filtered_ratios[
    filtered_ratios["debt_to_equity"] == 0
    ]["company_id"]
    .nunique()
    )


    kpi1, kpi2, kpi3 = st.columns(3)

    filtered_ratios = ratios[
        ratios["year"] == selected_year
        ].copy()

    st.write("Selected Year:", selected_year)
    st.write("Rows:", len(filtered_ratios))
    st.write(filtered_ratios[["company_id", "year"]].head())

    average_roe = filtered_ratios["roe_percentage"].mean()
    median_roce = filtered_ratios["roce_percentage"].median()

    median_de = filtered_ratios["debt_to_equity"].median()

    total_companies = filtered_ratios["company_id"].nunique()
    

    median_revenue_cagr = (
    pd.to_numeric(
        ratios["revenue_cagr_5yr"],
        errors="coerce",
    )
    .median()
)

    debt_free = (
    ratios[ratios["debt_to_equity"] == 0]
    ["company_id"]
    .nunique()
)

    with kpi1:
     st.metric(
        "Average ROE",
        f"{average_roe:.2f}%"
    )

    with kpi2:
     st.metric(
        "Median ROCE",
        f"{median_roce:.2f}%"
    )

    with kpi3:
     st.metric(
        "Median D/E",
        f"{median_de:.2f}"
    )

    kpi4, kpi5, kpi6 = st.columns(3)

    with kpi4:
     st.metric(
        "Total Companies",
        total_companies
    )

    with kpi5:
     st.metric(
        "Median Revenue CAGR",
        f"{median_revenue_cagr:.2f}%"
    )

    with kpi6:
     st.metric(
        "Debt-Free Companies",
        debt_free
    )

    st.markdown("---")

    st.subheader("Sector Breakdown")

    sector_counts = (
    sectors
    .groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
)

    fig = px.pie(
    sector_counts,
    names="broad_sector",
    values="Companies",
    hole=0.5,
    title="Companies by Broad Sector",
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)

    st.markdown("---")

    st.subheader("Top 5 Companies by Quality Score")

    st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True,
)