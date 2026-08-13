import streamlit as st
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_peer_groups,
    get_peer_data,
)


def show():

    st.title("PEER COMPARISON")

    groups = get_peer_groups()

    selected_group = st.selectbox(
        "Peer Group",
        groups["peer_group_name"],
    )

    peers = get_peer_data(
        selected_group
    )
    company = st.selectbox(
    "Select Company",
    peers["company_id"],
)
    selected = peers[
    peers["company_id"] == company
    ].iloc[0]

    

    metrics = [
    "roe_percentage",
    "roce_percentage",
    "net_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
]

    for metric in metrics:
     peers[metric] = peers[metric].astype(float)

    peer_average = peers[metrics].mean()

    fig = go.Figure()

    fig.add_trace(
    go.Scatterpolar(
        r=[selected[m] for m in metrics],
        theta=metrics,
        fill="toself",
        name=company,
    )
)

    fig.add_trace(
    go.Scatterpolar(
        r=[peer_average[m] for m in metrics],
        theta=metrics,
        fill="toself",
        name="Peer Average",
    )
)

    fig.update_layout(
    polar=dict(
    radialaxis=dict(
        visible=True,
        )
    ),
    showlegend=True,
)

    st.plotly_chart(
    fig,
    use_container_width=True,
)
    st.success(
            f"{len(peers)} companies found."
        )
    
    display_df = peers.copy()

    display_df.insert(
    0,
    "Selected",
    display_df["company_id"].apply(
        lambda x: "✅" if x == company else ""
    ),
)

    st.dataframe(
    display_df,
    use_container_width=True,
)
