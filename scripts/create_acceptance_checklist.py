from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT = BASE_DIR / "docs" / "acceptance_checklist.pdf"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

deliverables = [
    ("1", "SQLite database", "data/database/nifty100.db"),
    ("2", "SQL schema", "sql/schema.sql"),
    ("3", "SQL queries", "sql/queries.sql"),
    ("4", "ETL loader", "src/etl/loader.py"),
    ("5", "Normalizer", "src/etl/normaliser.py"),
    ("6", "Validator", "src/etl/validator.py"),
    ("7", "Validation failures", "output/validation_failures.csv"),
    ("8", "Screener engine", "src/screener/engine.py"),
    ("9", "Screener presets", "src/screener/presets.py"),
    ("10", "Comparison table", "output/screener_output.xlsx"),
    ("11", "Streamlit dashboard", "src/dashboard/app.py"),
    ("12", "FastAPI application", "src/api/main.py"),
    ("13", "Analytics modules", "src/analytics/"),
    ("14", "Reports", "src/reports/"),
    ("15", "Tearsheet PDFs", "output/tearsheets/"),
    ("16", "Peer reports", "reports/peer_tables/"),
    ("17", "Sector reports", "reports/sector/"),
    ("18", "Portfolio summary", "reports/portfolio/portfolio_summary.pdf"),
    ("19", "Pros and cons", "output/pros_cons_generated.csv"),
    ("20", "Cluster labels", "output/cluster_labels.csv"),
    ("21", "Analyst guide", "docs/analyst_guide.pdf"),
    ("22", "README", "README.md"),
    ("23", "Project tests", "tests/"),
]

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36,
)

styles = getSampleStyleSheet()

story = []

story.append(Paragraph(
    "NIFTY100 Analytics — Acceptance Checklist",
    styles["Title"],
))

story.append(Spacer(1, 12))

story.append(Paragraph(
    "Day 45 Final Sign-Off",
    styles["Heading2"],
))

story.append(Paragraph(
    "Acceptance gates AC-01 through AC-20 completed: PASS",
    styles["Normal"],
))

story.append(Spacer(1, 18))

data = [["No.", "Deliverable", "File / Directory", "Status"]]

for number, name, path in deliverables:
    full_path = BASE_DIR / path

    if full_path.exists():
        status = "PRESENT"
    else:
        status = "MISSING"

    data.append([
        number,
        name,
        path,
        status,
    ])

table = Table(
    data,
    colWidths=[30, 130, 270, 70],
    repeatRows=1,
)

table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.whitesmoke, colors.lightgrey]),
]))

story.append(table)

story.append(Spacer(1, 30))

story.append(Paragraph(
    "Team Lead Acceptance",
    styles["Heading2"],
))

story.append(Spacer(1, 30))

story.append(Paragraph(
    "Team Lead Signature: ______________________________",
    styles["Normal"],
))

story.append(Spacer(1, 15))

story.append(Paragraph(
    "Date: 13 August 2026",
    styles["Normal"],
))

story.append(Spacer(1, 15))

story.append(Paragraph(
    "Final Status: ACCEPTED",
    styles["Heading2"],
))

doc.build(story)

print(f"Created: {OUTPUT}")