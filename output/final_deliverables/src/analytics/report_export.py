from pathlib import Path
import sqlite3

import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)

from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "peer_tables"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

def load_table():

    conn = sqlite3.connect(
        DATABASE
    )

    table = pd.read_sql(
        "SELECT * FROM comparison_table",
        conn,
    )

    conn.close()

    return table

def top_five(df):

    return (
        df
        .sort_values(
            "composite_quality_score",
            ascending=False,
        )
        .head(5)
    )

def export_html(
    peer_group,
    table,
):

    html = f"""
    <html>

    <head>

    <title>{peer_group}</title>

    <style>

    body{{
        font-family:Arial;
        margin:40px;
    }}

    h1{{
        color:#003366;
    }}

    table{{
        border-collapse:collapse;
        width:100%;
    }}

    th,td{{
        border:1px solid black;
        padding:8px;
        text-align:center;
    }}

    th{{
        background:#003366;
        color:white;
    }}

    tr:nth-child(even){{
        background:#F5F5F5;
    }}

    </style>

    </head>

    <body>

    <h1>{peer_group}</h1>

    <h3>Top 5 Companies</h3>

    {table.to_html(index=False)}

    </body>

    </html>
    """

    with open(
        OUTPUT_DIR / f"{peer_group}.html",
        "w",
        encoding="utf-8",
    ) as file:

        file.write(html)

def export_pdf(
    peer_group,
    table,
):

    pdf = OUTPUT_DIR / f"{peer_group}.pdf"

    document = SimpleDocTemplate(
    str(pdf),
)

    data = [
        table.columns.tolist()
    ]

    data.extend(
        table.values.tolist()
    )

    report_table = Table(
        data,
    )

    report_table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("GRID",(0,0),(-1,-1),1,colors.black),

            ("BACKGROUND",(0,1),(-1,-1),colors.beige),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ])

    )

    document.build(
        [report_table]
    )

def generate_reports(master):

    groups = sorted(

        master[
            "peer_group_name"
        ].dropna().unique()

    )

    for group in groups:

        table = (

            master[
                master["peer_group_name"] == group
            ]

            .sort_values(
                "composite_quality_score",
                ascending=False,
            )

            .head(5)

        )

        report_columns = [
    "company_id",
    "company_name",
    "roe_percentage",
    "roce_percentage",
    "net_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "capex_label",
    "capex_cr",
    "fcf_conversion_rate",
    "composite_quality_score",
]
        available_columns = [
    column
    for column in report_columns
    if column in table.columns
]

    table = table[
    available_columns
]


    table = table.rename(
    columns={
        "company_id": "Company",
        "company_name": "Company Name",
        "roe_percentage": "ROE (%)",
        "roce_percentage": "ROCE (%)",
        "net_profit_margin_pct": "Net Profit Margin (%)",
        "debt_to_equity": "Debt / Equity",
        "interest_coverage": "Interest Coverage",
        "asset_turnover": "Asset Turnover",
        "free_cash_flow_cr": "Free Cash Flow (Cr)",
        "revenue_cagr_5yr": "Revenue CAGR (5Y)",
        "pat_cagr_5yr": "PAT CAGR (5Y)",
        "eps_cagr_5yr": "EPS CAGR (5Y)",
        "capex_label": "Capital Allocation",
        "capex_cr": "CapEx (Cr)",
        "fcf_conversion_rate": "FCF Conversion (%)",
        "composite_quality_score": "Composite Score",
    }
)


    export_html(
            group,
            table,
        )

    export_pdf(
            group,
            table,
        )

    print(
            f"{group} completed."
        )

if __name__ == "__main__":

    table = load_table()

    generate_reports(table)

    print()

    print("Reports generated successfully.")