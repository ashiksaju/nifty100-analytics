from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)


OUTPUT = "docs/analyst_guide.pdf"


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "GuideTitle",
    parent=styles["Title"],
    fontSize=24,
    leading=30,
    alignment=TA_CENTER,
    spaceAfter=20,
)

subtitle_style = ParagraphStyle(
    "GuideSubtitle",
    parent=styles["Normal"],
    fontSize=12,
    leading=18,
    alignment=TA_CENTER,
    spaceAfter=30,
)

heading_style = ParagraphStyle(
    "GuideHeading",
    parent=styles["Heading1"],
    fontSize=17,
    leading=22,
    spaceBefore=10,
    spaceAfter=12,
)

subheading_style = ParagraphStyle(
    "GuideSubHeading",
    parent=styles["Heading2"],
    fontSize=13,
    leading=18,
    spaceBefore=8,
    spaceAfter=8,
)

body_style = ParagraphStyle(
    "GuideBody",
    parent=styles["BodyText"],
    fontSize=10.5,
    leading=16,
    spaceAfter=8,
)

code_style = ParagraphStyle(
    "GuideCode",
    parent=styles["Code"],
    fontSize=8.5,
    leading=12,
    leftIndent=10,
    rightIndent=10,
    spaceBefore=5,
    spaceAfter=10,
)

small_style = ParagraphStyle(
    "GuideSmall",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
)


def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(item, body_style)) for item in items],
        bulletType="bullet",
        leftIndent=20,
    )


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(
        A4[0] / 2,
        0.45 * inch,
        f"NIFTY100 Analytics — Analyst Guide — Page {doc.page}",
    )
    canvas.restoreState()


doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=0.65 * inch,
    leftMargin=0.65 * inch,
    topMargin=0.65 * inch,
    bottomMargin=0.7 * inch,
)

story = []


# ------------------------------------------------------------------
# COVER
# ------------------------------------------------------------------

story.append(Spacer(1, 1.4 * inch))
story.append(Paragraph("NIFTY100 Analytics", title_style))
story.append(Paragraph("Analyst Guide", title_style))
story.append(
    Paragraph(
        "User manual for the Streamlit dashboard, FastAPI backend, "
        "financial analytics, reporting and testing workflow.",
        subtitle_style,
    )
)
story.append(Spacer(1, 0.5 * inch))
story.append(
    Paragraph(
        "<b>Project Version:</b> 1.0.0<br/>"
        "<b>Technology:</b> Python, SQLite, FastAPI, Streamlit, Plotly<br/>"
        "<b>Coverage:</b> NIFTY100 financial and analytical data",
        subtitle_style,
    )
)
story.append(PageBreak())


# ------------------------------------------------------------------
# 1. PROJECT OVERVIEW
# ------------------------------------------------------------------

story.append(Paragraph("1. Project Overview", heading_style))

story.append(
    Paragraph(
        "NIFTY100 Analytics is an analytics platform designed to provide "
        "structured financial analysis of companies in the NIFTY100 universe. "
        "The application combines an SQLite database, Python analytics modules, "
        "a FastAPI backend and a Streamlit dashboard.",
        body_style,
    )
)

story.append(
    Paragraph(
        "The system provides company-level analysis, stock screening, peer "
        "comparison, trend analysis, sector analysis, capital allocation "
        "visualisation and annual-report access.",
        body_style,
    )
)

story.append(Paragraph("Primary components", subheading_style))

story.append(
    bullet_list(
        [
            "ETL pipeline for loading and validating source data.",
            "SQLite database containing the processed financial datasets.",
            "Analytics modules for ratios, CAGR, peer analysis, clustering and valuation.",
            "FastAPI REST API exposing analytical functionality.",
            "Streamlit dashboard providing the analyst-facing interface.",
            "PDF tearsheet and reporting functionality.",
            "Automated API and project tests.",
        ]
    )
)

story.append(Paragraph("Technology stack", subheading_style))

data = [
    ["Component", "Technology"],
    ["Programming language", "Python"],
    ["Database", "SQLite"],
    ["API", "FastAPI"],
    ["Dashboard", "Streamlit"],
    ["Charts", "Plotly"],
    ["Testing", "pytest"],
    ["Formatting", "Black"],
    ["Linting", "Ruff"],
]

table = Table(data, colWidths=[2.3 * inch, 3.8 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.append(table)
story.append(PageBreak())


# ------------------------------------------------------------------
# 2. SYSTEM ARCHITECTURE
# ------------------------------------------------------------------

story.append(Paragraph("2. System Architecture", heading_style))

story.append(
    Paragraph(
        "The application follows a layered architecture. Source data is "
        "processed by the ETL layer and stored in SQLite. Analytics modules "
        "operate on the database data. FastAPI exposes backend functionality, "
        "while Streamlit consumes the analytical functionality through the "
        "dashboard interface.",
        body_style,
    )
)

story.append(Paragraph("Major layers", subheading_style))

story.append(
    bullet_list(
        [
            "ETL layer — data loading, normalisation, validation and database loading.",
            "Analytics layer — financial ratios, CAGR, peer analysis, clustering, radar analysis and valuation.",
            "API layer — FastAPI routers for companies, screener, sectors, peers, valuation, portfolio, documents and health.",
            "Dashboard layer — Streamlit pages for analyst interaction.",
            "Reporting layer — portfolio summaries, sector reports and company tearsheets.",
        ]
    )
)

story.append(Paragraph("Database", subheading_style))

story.append(
    Paragraph(
        "The main SQLite database is located at:",
        body_style,
    )
)

story.append(
    Paragraph(
        "data/database/nifty100.db",
        code_style,
    )
)

story.append(
    Paragraph(
        "During Day 43 performance optimisation, indexes were added to "
        "company_id and year columns in the major financial tables. The final "
        "test suite completed with 139 passing tests.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 3. SETUP
# ------------------------------------------------------------------

story.append(Paragraph("3. Setup and Application Startup", heading_style))

story.append(Paragraph("Install project dependencies", subheading_style))

story.append(
    Paragraph(
        "Create or activate the project virtual environment and install the "
        "required Python dependencies.",
        body_style,
    )
)

story.append(
    Paragraph(
        "The project uses pytest configuration from pyproject.toml. The "
        "repository root is included in the Python path, allowing imports "
        "such as src.api.main.",
        body_style,
    )
)

story.append(Paragraph("Start the Streamlit dashboard", subheading_style))

story.append(
    Paragraph(
        "Run the following command from the project root:",
        body_style,
    )
)

story.append(
    Paragraph(
        "streamlit run src/dashboard/app.py",
        code_style,
    )
)

story.append(Paragraph("Start FastAPI", subheading_style))

story.append(
    Paragraph(
        "Run the API using:",
        body_style,
    )
)

story.append(
    Paragraph(
        "uvicorn src.api.main:app --reload --port 8000",
        code_style,
    )
)

story.append(
    Paragraph(
        "The API application object is defined as src.api.main:app.",
        body_style,
    )
)

story.append(Paragraph("Running both applications", subheading_style))

story.append(
    Paragraph(
        "FastAPI and Streamlit use different ports, allowing both applications "
        "to run simultaneously. FastAPI uses port 8000 while Streamlit uses "
        "port 8501 by default.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 4. DASHBOARD NAVIGATION
# ------------------------------------------------------------------

story.append(Paragraph("4. Dashboard Navigation", heading_style))

story.append(
    Paragraph(
        "The Streamlit application provides a sidebar navigation menu. "
        "The current dashboard implementation exposes the following screens:",
        body_style,
    )
)

pages = [
    ("HOME", "01_home", "Application overview and quick navigation."),
    ("COMPANY PROFILE", "02_profile", "Company-level financial information and charts."),
    ("SCREENER", "03_screener", "Filter companies using financial metrics."),
    ("PEER COMPARISON", "04_peers", "Compare companies against peers."),
    ("TREND ANALYSIS", "05_trends", "Analyse historical financial trends."),
    ("SECTOR ANALYSIS", "06_sectors", "Analyse sector-level financial characteristics."),
    ("CAPITAL ALLOCATION", "07_capital", "Visualise company capital allocation patterns."),
    ("ANNUAL REPORTS", "08_reports", "Access available annual reports."),
]

page_data = [["Navigation", "Module", "Purpose"]]
page_data.extend([[p[0], p[1], p[2]] for p in pages])

table = Table(page_data, colWidths=[1.55 * inch, 1.45 * inch, 3.2 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]
    )
)
story.append(table)
story.append(Spacer(1, 12))

story.append(
    Paragraph(
        "The dashboard application uses a page mapping in "
        "src/dashboard/app.py and dynamically imports the selected page.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 5. COMPANY PROFILE
# ------------------------------------------------------------------

story.append(Paragraph("5. Company Profile", heading_style))

story.append(
    Paragraph(
        "The Company Profile screen is intended for detailed analysis of "
        "an individual company. It provides company information, key financial "
        "metrics, historical performance and interactive charts.",
        body_style,
    )
)

story.append(Paragraph("Recommended workflow", subheading_style))

story.append(
    bullet_list(
        [
            "Open COMPANY PROFILE from the sidebar.",
            "Select the company that you want to analyse.",
            "Review the headline financial metrics.",
            "Review historical financial performance.",
            "Use the interactive charts to identify trends.",
            "Use the information together with peer and sector analysis for context.",
        ]
    )
)

story.append(Paragraph("Analyst considerations", subheading_style))

story.append(
    Paragraph(
        "Financial values may be unavailable for some companies or periods. "
        "The dashboard handles missing values by displaying N/A rather than "
        "allowing missing values to crash the application.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Companies with shorter financial histories should not automatically "
        "be treated as having poor performance. The available historical "
        "period should be considered when interpreting trends and CAGR values.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 6. SCREENER
# ------------------------------------------------------------------

story.append(Paragraph("6. Stock Screener", heading_style))

story.append(
    Paragraph(
        "The Stock Screener is designed to narrow the NIFTY100 universe using "
        "financial criteria. Filters can be combined to create a focused "
        "candidate set.",
        body_style,
    )
)

story.append(Paragraph("Available analytical filters", subheading_style))

story.append(
    bullet_list(
        [
            "Minimum ROE — selects companies with return on equity above the selected threshold.",
            "Maximum Debt-to-Equity — limits financial leverage.",
            "Minimum Free Cash Flow — identifies companies above a specified FCF threshold.",
            "Sector — restricts results to a selected sector.",
            "Minimum 5-year Revenue CAGR — filters based on historical revenue growth.",
            "Minimum 5-year PAT CAGR — filters based on historical profit growth.",
            "Maximum P/E — valuation filtering is subject to the availability of P/E data in the backend.",
        ]
    )
)

story.append(Paragraph("Example API screener call", subheading_style))

story.append(
    Paragraph(
        'curl "http://127.0.0.1:8000/api/v1/screener?min_roe=15"',
        code_style,
    )
)

story.append(
    Paragraph(
        "The API returns a result set containing the companies that satisfy "
        "the selected criteria.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 7. PEERS, TRENDS AND SECTORS
# ------------------------------------------------------------------

story.append(Paragraph("7. Peer, Trend and Sector Analysis", heading_style))

story.append(Paragraph("Peer Comparison", subheading_style))

story.append(
    Paragraph(
        "Peer Comparison allows an analyst to evaluate a company against "
        "comparable companies. This is useful for identifying relative "
        "strengths and weaknesses in profitability, leverage and other "
        "financial characteristics.",
        body_style,
    )
)

story.append(Paragraph("Trend Analysis", subheading_style))

story.append(
    Paragraph(
        "Trend Analysis displays historical financial trends using interactive "
        "line charts. Multiple metrics can be compared to understand whether "
        "financial performance is improving, deteriorating or remaining stable.",
        body_style,
    )
)

story.append(Paragraph("Sector Analysis", subheading_style))

story.append(
    Paragraph(
        "Sector Analysis provides sector-level comparisons. The dashboard "
        "uses interactive visualisations and sector median KPI comparisons "
        "to show differences between sectors.",
        body_style,
    )
)

story.append(
    Paragraph(
        "The current database contains 10 populated broad-sector categories. "
        "The API therefore returns 10 sector records. Analysts should treat "
        "the database contents as the source of truth rather than assuming "
        "a fixed number of sectors.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 8. CAPITAL ALLOCATION AND REPORTS
# ------------------------------------------------------------------

story.append(Paragraph("8. Capital Allocation and Annual Reports", heading_style))

story.append(Paragraph("Capital Allocation", subheading_style))

story.append(
    Paragraph(
        "The Capital Allocation screen visualises companies according to "
        "capital allocation patterns. The project documentation describes "
        "an interactive treemap as the primary visualisation.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Use the screen to identify groups of companies with similar capital "
        "allocation characteristics and then investigate individual companies "
        "using the Company Profile screen.",
        body_style,
    )
)

story.append(Paragraph("Annual Reports", subheading_style))

story.append(
    Paragraph(
        "The Annual Reports screen provides access to available annual-report "
        "links. Report availability can vary by company and reporting period.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Unavailable report links are handled gracefully by the dashboard. "
        "If a report is unavailable, use the available company information "
        "and other analytical screens instead.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 9. PDF TEARSHEETS
# ------------------------------------------------------------------

story.append(Paragraph("9. Generating PDF Tearsheets", heading_style))

story.append(
    Paragraph(
        "Company tearsheets provide a compact report for an individual company. "
        "The API exposes a tearsheet endpoint under the company resource.",
        body_style,
    )
)

story.append(Paragraph("API endpoint", subheading_style))

story.append(
    Paragraph(
        "GET /api/v1/companies/{ticker}/tearsheet",
        code_style,
    )
)

story.append(Paragraph("Example using curl", subheading_style))

story.append(
    Paragraph(
        'curl -o TCS_tearsheet.pdf '
        '"http://127.0.0.1:8000/api/v1/companies/TCS/tearsheet"',
        code_style,
    )
)

story.append(
    Paragraph(
        "The endpoint returns the PDF file when the tearsheet exists. If the "
        "company exists but the tearsheet file is not available, the API "
        "returns a 404 response.",
        body_style,
    )
)

story.append(Paragraph("Recommended analyst workflow", subheading_style))

story.append(
    bullet_list(
        [
            "Confirm that FastAPI is running.",
            "Identify the company ticker.",
            "Request the tearsheet endpoint.",
            "Save the returned PDF.",
            "Review the tearsheet alongside the dashboard analysis.",
        ]
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 10. API
# ------------------------------------------------------------------

story.append(Paragraph("10. FastAPI Usage", heading_style))

story.append(
    Paragraph(
        "The backend exposes REST endpoints under /api/v1. FastAPI's "
        "interactive documentation can be opened at /docs while the server "
        "is running.",
        body_style,
    )
)

api_data = [
    ["Endpoint", "Purpose"],
    ["/api/v1/health", "Health and database status."],
    ["/api/v1/companies", "Company listing and company analysis."],
    ["/api/v1/screener", "Financial screening."],
    ["/api/v1/sectors", "Sector analysis."],
    ["/api/v1/peers", "Peer comparison."],
    ["/api/v1/valuation", "Valuation analysis."],
    ["/api/v1/portfolio", "Portfolio analysis."],
    ["/api/v1/documents", "Document-related functionality."],
]

table = Table(api_data, colWidths=[2.5 * inch, 3.7 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]
    )
)
story.append(table)

story.append(PageBreak())


# ------------------------------------------------------------------
# 11. API CURL EXAMPLES
# ------------------------------------------------------------------

story.append(Paragraph("11. API curl Examples", heading_style))

examples = [
    (
        "Health check",
        'curl "http://127.0.0.1:8000/api/v1/health"',
    ),
    (
        "Get companies",
        'curl "http://127.0.0.1:8000/api/v1/companies"',
    ),
    (
        "Get TCS",
        'curl "http://127.0.0.1:8000/api/v1/companies/TCS"',
    ),
    (
        "Get sectors",
        'curl "http://127.0.0.1:8000/api/v1/sectors"',
    ),
    (
        "Get screener results",
        'curl "http://127.0.0.1:8000/api/v1/screener?min_roe=15"',
    ),
    (
        "Get TCS profit and loss",
        'curl "http://127.0.0.1:8000/api/v1/companies/TCS/pl"',
    ),
    (
        "Get TCS balance sheet",
        'curl "http://127.0.0.1:8000/api/v1/companies/TCS/bs"',
    ),
    (
        "Get TCS cash flow",
        'curl "http://127.0.0.1:8000/api/v1/companies/TCS/cashflow"',
    ),
    (
        "Get TCS ratios",
        'curl "http://127.0.0.1:8000/api/v1/companies/TCS/ratios"',
    ),
]

for title, command in examples:
    story.append(Paragraph(title, subheading_style))
    story.append(Paragraph(command, code_style))

story.append(PageBreak())


# ------------------------------------------------------------------
# 12. ETL
# ------------------------------------------------------------------

story.append(Paragraph("12. ETL and Data Workflow", heading_style))

story.append(
    Paragraph(
        "The ETL portion of the project is responsible for preparing source "
        "data for analysis. The src/etl package contains the loader, normaliser, "
        "validator, SQLite loader and database verification components.",
        body_style,
    )
)

story.append(Paragraph("Important ETL modules", subheading_style))

story.append(
    bullet_list(
        [
            "src/etl/loader.py — primary loading workflow.",
            "src/etl/normaliser.py — normalisation utilities.",
            "src/etl/validator.py — data-quality validation.",
            "src/etl/sqlite_loader.py — SQLite loading functionality.",
            "src/etl/db_verify.py — database verification.",
            "src/etl/load_audit.py — loading/audit support.",
            "src/etl/manual_review.py — manual review workflow.",
        ]
    )
)

story.append(
    Paragraph(
        "Run ETL commands according to the project's existing scripts and "
        "configuration. Always verify the SQLite database after loading and "
        "before running analytical or dashboard components.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 13. TESTING
# ------------------------------------------------------------------

story.append(Paragraph("13. Testing", heading_style))

story.append(
    Paragraph(
        "The project uses pytest. The pytest configuration is stored in "
        "pyproject.toml and specifies the repository root as the Python path "
        "and tests/ as the test directory.",
        body_style,
    )
)

story.append(Paragraph("Run the complete test suite", subheading_style))

story.append(
    Paragraph(
        "python -m pytest tests/",
        code_style,
    )
)

story.append(
    Paragraph(
        "The Day 43 final verification produced 139 passing tests with no "
        "reported failures.",
        body_style,
    )
)

story.append(Paragraph("Performance testing", subheading_style))

story.append(
    Paragraph(
        "The performance test sent 10 concurrent screener requests using "
        "Python threading. All 10 requests completed in approximately "
        "0.234 seconds, which is comfortably below the 10-second target.",
        body_style,
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 14. TROUBLESHOOTING
# ------------------------------------------------------------------

story.append(Paragraph("14. Troubleshooting", heading_style))

troubleshooting = [
    (
        "ModuleNotFoundError: No module named 'src'",
        "Run commands from the project root and use the configured pytest "
        "Python path. Avoid launching test files directly with python when "
        "the project expects package imports.",
    ),
    (
        "API returns 404",
        "Confirm FastAPI is running and verify that the requested router is "
        "included in src/api/main.py. Check /docs to see the registered routes.",
    ),
    (
        "Streamlit page does not load",
        "Confirm Streamlit was started using streamlit run "
        "src/dashboard/app.py and check the terminal for import or runtime errors.",
    ),
    (
        "Database error",
        "Verify that data/database/nifty100.db exists and that the application "
        "is using the expected database path.",
    ),
    (
        "Missing financial value",
        "The dashboard may display N/A when a financial field is unavailable. "
        "This is expected behavior for missing data.",
    ),
    (
        "Annual report unavailable",
        "Report availability depends on the source data and available links. "
        "Use the dashboard's available links or another company analysis screen.",
    ),
    (
        "Tearsheet returns 404",
        "Confirm the ticker exists and that the corresponding PDF exists in "
        "the reports/tearsheets directory.",
    ),
]

for problem, solution in troubleshooting:
    story.append(Paragraph(problem, subheading_style))
    story.append(Paragraph(solution, body_style))

story.append(PageBreak())


# ------------------------------------------------------------------
# 15. PERFORMANCE
# ------------------------------------------------------------------

story.append(Paragraph("15. Performance and Optimisation", heading_style))

story.append(
    Paragraph(
        "Performance testing was completed as part of Day 43. The API "
        "successfully handled the required concurrent screener workload.",
        body_style,
    )
)

story.append(Paragraph("Observed result", subheading_style))

story.append(
    bullet_list(
        [
            "10 concurrent screener requests completed in approximately 0.234 seconds.",
            "Target: all 10 requests within 10 seconds.",
            "Result: PASS.",
            "Company Profile performance was tested against the required sub-3-second target.",
            "SQLite indexes were added to company_id and year columns in large financial tables.",
            "Final test suite result: 139 passed.",
        ]
    )
)

story.append(Paragraph("Indexes added", subheading_style))

story.append(
    bullet_list(
        [
            "profit_loss.company_id",
            "profit_loss.year",
            "balance_sheet.company_id",
            "balance_sheet.year",
            "cash_flow.company_id",
            "cash_flow.year",
            "financial_ratios.company_id",
            "financial_ratios.year",
            "documents.company_id",
            "documents.year",
        ]
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 16. PROJECT STRUCTURE
# ------------------------------------------------------------------

story.append(Paragraph("16. Project Directory Reference", heading_style))

structure = """
nifty100-analytics/
├── src/
│   ├── analytics/
│   ├── api/
│   │   ├── main.py
│   │   └── routers/
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   └── utils/
│   ├── etl/
│   ├── nlp/
│   ├── reports/
│   └── screener/
├── data/
│   └── database/
│       └── nifty100.db
├── docs/
├── output/
├── reports/
├── tests/
├── pyproject.toml
└── README.md
"""

story.append(Paragraph(structure.replace("\n", "<br/>"), code_style))

story.append(Paragraph("Key source locations", subheading_style))

story.append(
    bullet_list(
        [
            "API entry point: src/api/main.py",
            "Dashboard entry point: src/dashboard/app.py",
            "API routers: src/api/routers/",
            "Dashboard pages: src/dashboard/pages/",
            "ETL modules: src/etl/",
            "Analytics modules: src/analytics/",
            "Reporting modules: src/reports/",
            "Screener modules: src/screener/",
            "Tests: tests/",
            "SQLite database: data/database/nifty100.db",
        ]
    )
)

story.append(PageBreak())


# ------------------------------------------------------------------
# 17. QUICK REFERENCE
# ------------------------------------------------------------------

story.append(Paragraph("17. Analyst Quick Reference", heading_style))

story.append(Paragraph("Start dashboard", subheading_style))
story.append(
    Paragraph(
        "streamlit run src/dashboard/app.py",
        code_style,
    )
)

story.append(Paragraph("Start API", subheading_style))
story.append(
    Paragraph(
        "uvicorn src.api.main:app --reload --port 8000",
        code_style,
    )
)

story.append(Paragraph("API documentation", subheading_style))
story.append(
    Paragraph(
        "http://127.0.0.1:8000/docs",
        code_style,
    )
)

story.append(Paragraph("Run tests", subheading_style))
story.append(
    Paragraph(
        "python -m pytest tests/",
        code_style,
    )
)

story.append(Paragraph("Generate a TCS tearsheet", subheading_style))
story.append(
    Paragraph(
        'curl -o TCS_tearsheet.pdf '
        '"http://127.0.0.1:8000/api/v1/companies/TCS/tearsheet"',
        code_style,
    )
)

story.append(
    Paragraph(
        "<b>Final Day 43 status:</b> performance targets passed, "
        "SQLite optimisation completed and 139 tests passed.",
        body_style,
    )
)

doc.build(story, onFirstPage=footer, onLaterPages=footer)

print(f"Created {OUTPUT}")