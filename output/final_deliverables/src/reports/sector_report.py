from pathlib import Path

import sqlite3
import pandas as pd

from pathlib import Path

import sqlite3
import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from reportlab.lib import colors
from reportlab.lib.units import inch

ROOT = Path(__file__).resolve().parents[2]

DATABASE = (
    ROOT
    / "data"
    / "database"
    / "nifty100.db"
)

OUTPUT = (
    ROOT
    / "reports"
    / "sector"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True,
)

def load_data():

    conn = sqlite3.connect(DATABASE)

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    comparison = pd.read_sql(
        "SELECT * FROM comparison_table",
        conn,
    )
    financial = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
)
    
    conn.close()

    return sectors, comparison , financial
    

def create_sector_report(
    sector_name,
    sector_df,
    comparison,
    financial,
):

    styles = getSampleStyleSheet()

    pdf = OUTPUT / f"{sector_name}_report.pdf"

    doc = SimpleDocTemplate(str(pdf))

    elements = []

    elements.append(
        Paragraph(
            f"<b>{sector_name}</b>",
            styles["Title"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.3 * inch,
        )
    )

    merged = (
    sector_df
    .merge(
        comparison,
        on="company_id",
        how="left",
    )
    .merge(
        financial,
        on="company_id",
        how="left",
    )
)


    elements.append(
        Paragraph(
            f"Companies : {len(merged)}",
            styles["Heading2"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.2 * inch,
        )
    )

    median_table = Table([
    ["Metric", "Median"],
    [
        "ROE",
        f"{merged["return_on_equity_pct_y"].median():.2f}",
    ],
    [
        "ROCE",
        f"{merged["return_on_capital_employed_pct_y"].median():.2f}",
    ],
    [
        "Net Margin",
        f"{merged["net_profit_margin_pct_y"].median():.2f}",
    ],
    [
        "Debt/Equity",
        f"{merged["debt_to_equity_y"].median():.2f}",
    ],
])

    median_table.setStyle(
    TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.navy),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),
    ])
)

    elements.append(median_table)
    elements.append(Spacer(1,0.30*inch))
    elements.append(PageBreak())
    table_data = [
    [
        "Company",
        "ROE",
        "ROCE",
        "Net Margin",
        "Debt/Equity",
        "Asset Turnover",
        "CFO Score",
        "Quality Rank",
    ]
]
    for _, row in merged.iterrows():

        table_data.append(
        [
            row["company_name_y"],

            f"{row['return_on_equity_pct_y']:.2f}"
            if pd.notna(row["return_on_equity_pct_y"])
            else "-",

            f"{row['return_on_capital_employed_pct_y']:.2f}"
            if pd.notna(row["return_on_capital_employed_pct_y"])
            else "-",

            f"{row['net_profit_margin_pct_y']:.2f}"
            if pd.notna(row["net_profit_margin_pct_y"])
            else "-",

            f"{row['debt_to_equity_y']:.2f}"
            if pd.notna(row["debt_to_equity_y"])
            else "-",

            f"{row['asset_turnover_y']:.2f}"
            if pd.notna(row["asset_turnover_y"])
            else "-",

            f"{row['cfo_quality_score_y']:.2f}"
            if pd.notna(row["cfo_quality_score_y"])
            else "-",

            row["quality_rank"],
        ]
    )
        company_table = Table(
        table_data,
        repeatRows=1,
)

        company_table.setStyle(
        TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ]
    )
)

        elements.append(company_table)

        doc.build(elements)

        print(pdf.name)
        

def main():

    (
    sectors,
    comparison,
    financial,
) = load_data()

    for sector in sorted(
        sectors["broad_sector"].unique()
    ):

        sector_df = sectors[
            sectors["broad_sector"] == sector
        ]

        create_sector_report(
            sector,
            sector_df,
            comparison,
            financial,
)

    print("\nSector reports complete.")

if __name__ == "__main__":
 main()

