import sqlite3
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from reportlab.graphics.shapes import Drawing
ROOT = Path(__file__).resolve().parents[2]

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = (
    BASE_DIR
    / "data"
    / "database"
    / "nifty100.db"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
    / "tearsheets"
)

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

    balance_sheet = pd.read_sql(
        "SELECT * FROM balance_sheet",
        conn,
    )

    cash_flow = pd.read_sql(
        "SELECT * FROM cash_flow",
        conn,
    )

    pros_cons = pd.read_csv(
    BASE_DIR
    / "output"
    / "pros_cons_generated.csv"
)

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )
    cashflow_intelligence = pd.read_excel(
    BASE_DIR / "output" / "cashflow_intelligence.xlsx"
)
    

    conn.close()

    return(
    comparison,
    profit_loss,
    balance_sheet,
    cash_flow,
    pros_cons,
    sectors,

    ) 
def draw_header(canvas, doc):

    page_width = doc.pagesize[0]
    page_height = doc.pagesize[1]

    canvas.saveState()

    canvas.setFillColor(HexColor("#0B1F3A"))

    canvas.rect(
        0,
        page_height - 70,
        page_width,
        70,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(white)

    canvas.setFont(
        "Helvetica-Bold",
        20,
    )

    canvas.drawCentredString(
    page_width / 2,
    page_height - 45,
    doc.company_title,
)

    canvas.restoreState()

def create_financial_charts(
    company_id,
    profit_loss,
):

    data = (
        profit_loss[
            profit_loss["company_id"] == company_id
        ]
        .copy()
    )

    data = (
        data[
            ~data["year"].str.contains(
                "TTM",
                na=False,
            )
        ]
    )

    data["year_num"] = (
        data["year"]
        .str.extract(r"(\d{4})")
        .astype(int)
    )

    data = (
        data
        .sort_values("year_num")
        .tail(10)
    )

    revenue_chart = (
        OUTPUT_DIR
        / f"{company_id}_revenue.png"
    )

    profit_chart = (
        OUTPUT_DIR
        / f"{company_id}_profit.png"
    )

    plt.figure(figsize=(4,3))

    plt.bar(
        data["year_num"].astype(str),
        data["sales"],
    )

    plt.title("Revenue")

    plt.tight_layout()

    plt.savefig(
        revenue_chart,
        dpi=200,
    )

    plt.close()

    plt.figure(figsize=(4,3))

    plt.bar(
        data["year_num"].astype(str),
        data["net_profit"],
    )

    plt.title("Net Profit")

    plt.tight_layout()

    plt.savefig(
        profit_chart,
        dpi=200,
    )

    plt.close()

    return (
        revenue_chart,
        profit_chart,
    )

def create_roe_roce_chart(
    company_id,
    profit_loss,
    comparison,
):

    company = comparison[
        comparison["company_id"] == company_id
    ]

    years = (
        profit_loss[
            profit_loss["company_id"] == company_id
        ]
        .copy()
    )

    years = years[
        ~years["year"].str.contains(
            "TTM",
            na=False,
        )
    ]

    years["year_num"] = (
        years["year"]
        .str.extract(r"(\d{4})")
        .astype(int)
    )

    years = (
        years
        .sort_values("year_num")
        .tail(10)
    )

    roe = company["roe_percentage"].iloc[0]
    roce = company["roce_percentage"].iloc[0]

    fig, ax1 = plt.subplots(figsize=(6,3))

    ax1.plot(
        years["year_num"],
        [roe] * len(years),
        linewidth=2,
        label="ROE",
    )

    ax2 = ax1.twinx()

    ax2.plot(
        years["year_num"],
        [roce] * len(years),
        linewidth=2,
        label="ROCE",
    )

    ax1.set_title("ROE vs ROCE")

    chart = (
        OUTPUT_DIR
        / f"{company_id}_roe_roce.png"
    )

    plt.tight_layout()

    plt.savefig(
        chart,
        dpi=200,
    )

    plt.close()

    return chart

def create_balance_sheet_chart(
    company_id,
    balance_sheet,
):

    data = (
        balance_sheet[
            balance_sheet["company_id"] == company_id
        ]
        .copy()
    )

    data = (
        data[
            ~data["year"].str.contains(
                "TTM",
                na=False,
            )
        ]
    )

    data["year_num"] = (
        data["year"]
        .str.extract(r"(\d{4})")
        .astype(int)
    )

    data = (
        data
        .sort_values("year_num")
        .tail(10)
    )

    chart = (
        OUTPUT_DIR
        / f"{company_id}_balance.png"
    )

    plt.figure(figsize=(6,3))

    plt.bar(
        data["year_num"].astype(str),
        data["equity_capital"] + data["reserves"],
        label="Equity",
    )

    plt.bar(
        data["year_num"].astype(str),
        data["borrowings"],
        bottom=data["equity_capital"] + data["reserves"],
        label="Borrowings",
    )

    plt.bar(
        data["year_num"].astype(str),
        data["other_liabilities"],
        bottom=(
            data["equity_capital"]
            + data["reserves"]
            + data["borrowings"]
        ),
        label="Other Liabilities",
    )

    plt.legend()

    plt.title("Balance Sheet Composition")

    plt.tight_layout()

    plt.savefig(
        chart,
        dpi=200,
    )

    plt.close()

    return chart

def create_cashflow_chart(
    company_id,
    cash_flow,
):

    data = (
        cash_flow[
            cash_flow["company_id"] == company_id
        ]
        .copy()
    )

    data = (
        data[
            ~data["year"].str.contains(
                "TTM",
                na=False,
            )
        ]
        .sort_values("year")
    )

    latest = data.iloc[-1]

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net",
    ]

    values = [
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        latest["net_cash_flow"],
    ]

    chart = (
        OUTPUT_DIR
        / f"{company_id}_cashflow.png"
    )

    plt.figure(figsize=(6,3))

    plt.bar(
        labels,
        values,
    )

    plt.title("Latest Cash Flow")

    plt.tight_layout()

    plt.savefig(
        chart,
        dpi=200,
    )

    plt.close()

    return chart

def build_pros_cons(company_id, pros_cons, styles):

    pros = pros_cons[
        (pros_cons["company_id"] == company_id)
        & (pros_cons["type"] == "pro")
    ]

    cons = pros_cons[
        (pros_cons["company_id"] == company_id)
        & (pros_cons["type"] == "con")
    ]

    items = []

    title = styles["Heading2"]

    items.append(Paragraph("Pros", title))

    for _, row in pros.iterrows():

        items.append(
            Paragraph(
                f"<font color='green'>• {row['text']}</font>",
                styles["BodyText"],
            )
        )

    items.append(Spacer(1, 0.15 * inch))

    items.append(Paragraph("Cons", title))

    for _, row in cons.iterrows():

        items.append(
            Paragraph(
                f"<font color='red'>• {row['text']}</font>",
                styles["BodyText"],
            )
        )

    return items

def capital_badge(company):

    style = getSampleStyleSheet()["Heading2"]

    return Table(
        [[
            Paragraph(
                f"<b>Capital Allocation</b><br/>{company['capital_allocation_label']}",
                style,
            )
        ]],
        colWidths=[3.0 * inch],
    )

    


def create_tearsheet(company_id):
    (
    comparison,
    profit_loss,
    balance_sheet,
    cash_flow,
    pros_cons,
    sectors,
) = load_tables()

    cashflow_intelligence = pd.read_excel(
    BASE_DIR / "output" / "cashflow_intelligence.xlsx"
)
     
    

    company = comparison[
    comparison["company_id"].astype(str).str.upper()
    == company_id.upper()
]
    

    if company.empty:
        raise ValueError(
        f"{company_id} not found in comparison_table"
    )

    company = company.iloc[0]

    
    pdf_path = (
        OUTPUT_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=(8.27 * inch, 11.69 * inch),
    topMargin=1.25 * inch,
    bottomMargin=0.5 * inch,
    leftMargin=0.5 * inch,
    rightMargin=0.5 * inch,
)

    styles = getSampleStyleSheet()

    elements = []
    elements.append(
    Spacer(
        1,
        0.25 * inch,
    )
)
    kpi_data = [

    [
        f"ROE\n{company['roe_percentage']:.2f}%",
        f"ROCE\n{company['roce_percentage']:.2f}%",
        f"NPM\n{company['net_profit_margin_pct']:.2f}%"
    ],

    [
        f"OPM\n{company['operating_profit_margin_pct']:.2f}%",
        f"CFO Score\n{company['cfo_quality_score']:.2f}",
        f"Revenue CAGR\n{pd.to_numeric(company['revenue_cagr_5yr'], errors='coerce'):.2f}%"
    ],

]
    kpi_table = Table(
    kpi_data,
    colWidths=[2.2*inch]*3,
    rowHeights=[0.9*inch]*2,
)

    kpi_table.setStyle(

    TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),colors.whitesmoke),

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BOX",(0,0),(-1,-1),1.5,colors.black),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

        ("FONTSIZE",(0,0),(-1,-1),11),

        ("BOTTOMPADDING",(0,0),(-1,-1),8),

    ])

)

    elements.append(kpi_table)

    elements.append(
    Spacer(
        1,
        0.3*inch,
    )
)

    elements.append(
    Spacer(
        1,
        0.25 * inch,
    )
)

    cashflow_chart = create_cashflow_chart(
    company_id,
    cash_flow,
)

    elements.append(
    Image(
        str(cashflow_chart),
        width=6.4 * inch,
        height=2.8 * inch,
    )
)
    revenue_chart, profit_chart = create_financial_charts(
    company_id,
    profit_loss,
)

    chart_table = Table(
    [[
        Image(
            str(revenue_chart),
            width=3.1*inch,
            height=2.3*inch,
        ),
        Image(
            str(profit_chart),
            width=3.1*inch,
            height=2.3*inch,
        )
    ]]
)

    elements.append(chart_table)

    elements.append(
    Spacer(
        1,
        0.2 * inch,
    )
)
    elements.append(
    Spacer(
        1,
        0.4 * inch,
    )
)

    balance_chart = create_balance_sheet_chart(
    company_id,
    balance_sheet,
)

    elements.append(
    Image(
        str(balance_chart),
        width=6.4 * inch,
        height=3.0 * inch,
    )
)

    roe_chart = create_roe_roce_chart(
    company_id,
    profit_loss,
    comparison,
)

    elements.append(
    Image(
        str(roe_chart),
        width=6.4 * inch,
        height=2.5 * inch,
    )
)
    elements.append(
    Spacer(
        1,
        0.3 * inch,
    )
)

    elements.extend(
    build_pros_cons(
        company_id,
        pros_cons,
        styles,
    )
)
    elements.append(
    Spacer(
        1,
        0.25 * inch,
    )
)
    allocation = cashflow_intelligence[
    cashflow_intelligence["company_id"] == company_id
]

    if allocation.empty:
        allocation = {
        "capital_allocation_label": "Not Available"
    }
    else:
        allocation = allocation.iloc[0]
    print("\nAllocation being passed to badge:")
    
    badge = capital_badge(allocation)


    badge.setStyle(
    TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.lightgrey),
        ("BOX", (0,0), (-1,-1), 1.5, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ])
)

    elements.append(badge)

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    

    canvas_title = (
    f"{company['company_name']} ({company_id})"
)

    doc.company_title = canvas_title
    print("Building PDF...")
    
    doc.build(
    elements,
    onFirstPage=draw_header,
    onLaterPages=draw_header,
)
    

    print(f"Created: {pdf_path}")
    

def main():

    (
    comparison,
    profit_loss,
    balance_sheet,
    cash_flow,
    pros_cons,
    sectors,
) = load_tables()

    



    companies = (

        comparison["company_id"]

        .dropna()

        .unique()

    )



    skipped = []
    generated = 0



    for company in companies:



        years = (

            profit_loss[

                (profit_loss["company_id"] == company)

                &

                (

                    ~profit_loss["year"].str.contains(

                        "TTM",

                        na=False,

                    )

                )

            ]

        )



        if len(years) < 3:



            skipped.append(

                {

                    "company_id": company,

                    "reason": "Less than 3 years data",

                }

            )



            continue



        try:



            create_tearsheet(company)
            generated += 1
           



        except Exception as e:



            skipped.append(

                {

                    "company_id": company,

                    "reason": str(e),

                }

            )



    pd.DataFrame(skipped).to_csv(



        OUTPUT_DIR /

        "skipped_tearsheets.csv",



        index=False,



    )

    



    print("MAIN STARTED")



    



    print("TABLES LOADED")



    companies = comparison["company_id"].unique()



    print(f"Companies: {len(companies)}")



    create_tearsheet(company)
    




    print()



    print("Batch Generation Complete")



    print("Generated :", generated)


    print(

        "Skipped :",

        len(skipped),

    )

if __name__ == "__main__":

    main()