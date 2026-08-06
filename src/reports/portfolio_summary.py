from pathlib import Path
import sqlite3

import pandas as pd
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "database" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "portfolio"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def load_tables():

    conn = sqlite3.connect(DB_PATH)
    print(DB_PATH)

    comparison = pd.read_sql(
        "SELECT * FROM comparison_table",
        conn,
    )

    profit_loss = pd.read_sql(
        "SELECT * FROM profit_loss",
        conn,
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    conn.close()

    return (
        comparison,
        profit_loss,
        sectors,
    )

def get_trend_arrow(current, previous):

    if pd.isna(current) or pd.isna(previous):
        return "?"

    if previous == 0:
        return "?"

    change = ((current - previous) / abs(previous)) * 100

    if abs(change) <= 2:
        return "→"

    if change > 0:
        return "↑"

    return "↓"


def create_portfolio_summary():

    comparison, profit_loss, sectors = load_tables()

    doc = SimpleDocTemplate(
    str(OUTPUT_DIR / "portfolio_summary.pdf"),
    pagesize=A4,
)

    styles = getSampleStyleSheet()
    styles["Title"].spaceAfter = 6
    styles["Title"].spaceBefore = 0
    styles["Title"].leading = 24

    elements = []

    comparison = comparison.sort_values("company_id")

    for _, company in comparison.iterrows():

        # -----------------------------
        # Company Name
        # -----------------------------
        company_name = company["company_name"]

        if pd.isna(company_name):
            company_name = company["company_id"]

        
        title_style = styles["Title"]
        title_style.alignment = 1   # Center

        elements.append(
            Paragraph(
            str(company_name),
            title_style,
    )
)

        elements.append(
            Paragraph(
                f"<b>Ticker:</b> {company['company_id']}",
                styles["Normal"],
    )
)

        sector = sectors[
            sectors["company_id"] == company["company_id"]
]

        if not sector.empty:
            elements.append(
                Paragraph(
                    f"<b>Sector:</b> {sector.iloc[0]['broad_sector']}",
                    styles["Normal"],
                )
            )
    

        elements.append(Spacer(1, 0.05 * inch))

        # -----------------------------
        # KPI TABLE
        # -----------------------------

        kpi_data = [

            ["Metric", "Value"],

            ["ROE", f"{company['roe_percentage']:.2f}%"],

            ["ROCE", f"{company['roce_percentage']:.2f}%"],

            ["Net Margin", f"{company['net_profit_margin_pct']:.2f}%"],

            ["Debt / Equity", "N/A" if pd.isna(company["debt_to_equity"]) else f"{company['debt_to_equity']:.2f}"],

            ["Asset Turnover", f"{company['asset_turnover']:.2f}"],

            ["CFO Score", f"{company['cfo_quality_score']:.2f}"],

        ]

        table = Table(
        kpi_data,
        colWidths=[2.1 * inch, 0.9 * inch],
        rowHeights=[0.22 * inch] * len(kpi_data),
        
)

        table.setStyle(
            TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.navy),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),

                ("TOPPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ])
        )

    

        elements.append(
            Spacer(1, 0.03 * inch)
        )
        # -----------------------------
        # TRENDS
        # -----------------------------

        history = (
            profit_loss[
                (profit_loss["company_id"] == company["company_id"])
                &
                (~profit_loss["year"].str.contains("TTM", na=False))
            ]
            .sort_values("year")
        )
        
        
        
        

        

        if len(history) >= 2:

            previous = history.iloc[-2]

            latest = history.iloc[-1]

            trends = [

                ("Sales",
                 get_trend_arrow(
                     latest["sales"],
                     previous["sales"],
                 )),

                ("Operating Profit",
                 get_trend_arrow(
                     latest["operating_profit"],
                     previous["operating_profit"],
                 )),

                ("Net Profit",
                 get_trend_arrow(
                     latest["net_profit"],
                     previous["net_profit"],
                 )),

                ("EPS",
                 get_trend_arrow(
                     latest["eps"],
                     previous["eps"],
                 )),

                ("OPM",
                 get_trend_arrow(
                     latest["opm_percentage"],
                     previous["opm_percentage"],
                 )),

                ("Dividend",
                 get_trend_arrow(
                     latest["dividend_payout"],
                     previous["dividend_payout"],
                 )),
            ]

            trend_data = [["Metric", "Trend"]]

            for metric, arrow in trends:
             trend_data.append([metric, arrow])

            trend_table = Table(
            trend_data,
            colWidths=[2.1 * inch, 0.9 * inch],
            rowHeights=[0.22 * inch] * len(trend_data),
            
)
            trend_table.setStyle(
            TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (1,1), (1,-1), "CENTER"),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ])
)

            

        else:

            elements.append(
            Paragraph(
                "Not enough historical data.",
                styles["Normal"],
    )
)
        combined_table = Table(
            [[table, trend_table]],
            colWidths=[3.15 * inch, 3.15 * inch],
)

        combined_table.setStyle(
            TableStyle([
        ("VALIGN", (0, 0), (0, 0), "TOP"),
        ("VALIGN", (1, 0), (1, 0), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ])
)

        elements.append(combined_table)      

        elements.append(PageBreak())

    doc.build(elements)

    print(f"Created: {OUTPUT_DIR / 'portfolio_summary.pdf'}")

    


def main():

    create_portfolio_summary()


if __name__ == "__main__":

    main()