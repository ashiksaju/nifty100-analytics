import pandas as pd
import streamlit as st

from src.dashboard.utils.db import get_screener_data

def show():

    st.title("STOCK SCREENER")

    data = get_screener_data()

    

    st.sidebar.header(" FILTERS")
    

    

    roe_min = st.sidebar.slider(
    "Minimum ROE %",
    0,
    50,
    15,
)

    de_max = st.sidebar.slider(
    "Maximum Debt / Equity",
    0.0,
    5.0,
    1.0,
)

    fcf_min = st.sidebar.slider(
    "Minimum Free Cash Flow",
    0,
    10000,
    0,
)

    revenue_cagr_min = st.sidebar.slider(
    "Minimum Revenue CAGR %",
    0,
    50,
    10,
)

    pat_cagr_min = st.sidebar.slider(
    "Minimum PAT CAGR %",
    0,
    50,
    10,
)

    opm_min = st.sidebar.slider(
    "Minimum Net Profit Margin %",
    0,
    50,
    15,
)

    asset_turnover_min = st.sidebar.slider(
    "Minimum Asset Turnover",
    0.0,
    5.0,
    1.0,
)

    interest_coverage_min = st.sidebar.slider(
    "Minimum Interest Coverage",
    0.0,
    20.0,
    3.0,
)

    quality_score_min = st.sidebar.slider(
      "Minimum Quality Score",
       0.0,
       100.0,
       0.0,
)

    top_n = st.sidebar.slider(
     "Maximum Results",
      5,
      100,
      50,
)

   

    filtered = data.copy()

    filtered["roe_percentage"] = pd.to_numeric(
    filtered["roe_percentage"],
    errors="coerce",
)

    filtered["debt_to_equity"] = pd.to_numeric(
    filtered["debt_to_equity"],
    errors="coerce",
)

    filtered["free_cash_flow_cr"] = pd.to_numeric(
    filtered["free_cash_flow_cr"],
    errors="coerce",
)

    filtered["revenue_cagr_5yr"] = pd.to_numeric(
    filtered["revenue_cagr_5yr"],
    errors="coerce",
)

    filtered["pat_cagr_5yr"] = pd.to_numeric(
    filtered["pat_cagr_5yr"],
    errors="coerce",
)

    filtered["net_profit_margin_pct"] = pd.to_numeric(
    filtered["net_profit_margin_pct"],
    errors="coerce",
)

    filtered["asset_turnover"] = pd.to_numeric(
    filtered["asset_turnover"],
    errors="coerce",
)

    filtered["interest_coverage"] = pd.to_numeric(
    filtered["interest_coverage"],
    errors="coerce",
)

    filtered["composite_quality_score"] = pd.to_numeric(
    filtered["composite_quality_score"],
    errors="coerce",
)
    st.write("Before filtering:", len(filtered))

    st.write("ROE >=", (filtered["roe_percentage"] >= roe_min).sum())
    st.write("Debt <=", (filtered["debt_to_equity"] <= de_max).sum())
    st.write("FCF >=", (filtered["free_cash_flow_cr"] >= fcf_min).sum())
    st.write("Revenue CAGR >=", (filtered["revenue_cagr_5yr"] >= revenue_cagr_min).sum())
    st.write("PAT CAGR >=", (filtered["pat_cagr_5yr"] >= pat_cagr_min).sum())
    st.write("Net Profit Margin >=", (filtered["net_profit_margin_pct"] >= opm_min).sum())
    st.write("Asset Turnover >=", (filtered["asset_turnover"] >= asset_turnover_min).sum())
    st.write("Interest Coverage >=", (filtered["interest_coverage"] >= interest_coverage_min).sum())
    st.write("Quality Score >=", (filtered["composite_quality_score"] >= quality_score_min).sum())
    


    filtered = filtered.head(top_n)

    st.success(
        f"{len(filtered)} companies match your filters."
    )
    
    st.dataframe(
        filtered,
        use_container_width=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
    label=" DOWNLOAD",
    data=csv,
    file_name="screening_results.csv",
    mime="text/csv",
)