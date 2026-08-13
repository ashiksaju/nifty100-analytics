from pathlib import Path

import pandas as pd

from src.etl.loader import load_all_data
from src.etl.normaliser import normalize_year, normalize_ticker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


validation_results = []


def log_failure(rule, severity, table, row_id, message):
    validation_results.append(
        {
            "rule": rule,
            "severity": severity,
            "table": table,
            "row_id": row_id,
            "message": message,
        }
    )


def save_validation_results():
    df = pd.DataFrame(validation_results)
    output_file = OUTPUT_DIR / "validation_failures.csv"
    df.to_csv(output_file, index=False)

def dq01_primary_key_uniqueness(datasets):
    for table_name, df in datasets.items():
        if "id" not in df.columns:
            continue

        duplicates = df[df["id"].duplicated(keep=False)]

        for _, row in duplicates.iterrows():
            log_failure(
                rule="DQ-01",
                severity="CRITICAL",
                table=table_name,
                row_id=row["id"],
                message="Duplicate primary key found.",
            )
def dq02_company_year_uniqueness(datasets):
    for table_name, df in datasets.items():
        if not {"company_id", "year"}.issubset(df.columns):
            continue

        duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

        for _, row in duplicates.iterrows():
            log_failure(
                rule="DQ-02",
                severity="CRITICAL",
                table=table_name,
                row_id=row["id"] if "id" in df.columns else None,
                message=f"Duplicate (company_id, year): ({row['company_id']}, {row['year']})",
            )
def dq03_foreign_key_integrity(datasets):
    companies = datasets["companies"]

    valid_company_ids = set(companies["id"])

    for table_name, df in datasets.items():
        if table_name == "companies":
            continue

        if "company_id" not in df.columns:
            continue

        invalid_rows = df[~df["company_id"].isin(valid_company_ids)]

        for _, row in invalid_rows.iterrows():
            log_failure(
                rule="DQ-03",
                severity="CRITICAL",
                table=table_name,
                row_id=row["id"] if "id" in df.columns else None,
                message=f"Invalid company_id: {row['company_id']}",
            )

def dq04_balance_sheet_balance(datasets):
    if "balance_sheet" not in datasets:
        return

    df = datasets["balance_sheet"]

    required_columns = {
        "total_assets",
        "total_liabilities",
    }

    if not required_columns.issubset(df.columns):
        return

    df["balance_error_pct"] = (
        abs(df["total_assets"] - df["total_liabilities"])
        / df["total_assets"]
    ) * 100

    failures = df[df["balance_error_pct"] > 1]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-04",
            severity="WARNING",
            table="balance_sheet",
            row_id=row["id"],
            message=f"Balance sheet mismatch: {row['balance_error_pct']:.2f}%",
        )
def dq05_opm_cross_check(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"].copy()

    required_columns = {
        "sales",
        "operating_profit",
        "opm_percentage",
    }

    if not required_columns.issubset(df.columns):
        return

    df = df[df["sales"] > 0]

    df["calculated_opm"] = (
        df["operating_profit"] / df["sales"]
    ) * 100

    tolerance = 0.5

    failures = df[
        (df["calculated_opm"] - df["opm_percentage"]).abs() > tolerance
    ]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-05",
            severity="WARNING",
            table="profit_loss",
            row_id=row["id"],
            message=f"OPM mismatch. Expected {row['calculated_opm']:.2f}%, Found {row['opm_percentage']:.2f}%"
        )

def dq06_positive_sales(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"]

    if "sales" not in df.columns:
        return

    failures = df[df["sales"] <= 0]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-06",
            severity="WARNING",
            table="profit_loss",
            row_id=row["id"],
            message=f"Invalid sales value: {row['sales']}"
        )

        from src.etl.normaliser import normalize_year


def dq07_year_format(datasets):
    for table_name, df in datasets.items():

        if "year" not in df.columns:
            continue

        for _, row in df.iterrows():

            normalized = normalize_year(row["year"])

            if normalized is None:
                log_failure(
                    rule="DQ-07",
                    severity="CRITICAL",
                    table=table_name,
                    row_id=row["id"] if "id" in df.columns else None,
                    message=f"Invalid year value: {row['year']}"
                )
def dq08_ticker_format(datasets):
    for table_name, df in datasets.items():

        if "company_id" not in df.columns:
            continue

        for _, row in df.iterrows():

            normalized = normalize_ticker(row["company_id"])

            if normalized != row["company_id"]:
                log_failure(
                    rule="DQ-08",
                    severity="WARNING",
                    table=table_name,
                    row_id=row["id"] if "id" in df.columns else None,
                    message=f"Ticker not normalized: {row['company_id']}"
                )
def dq09_net_cash_check(datasets):
    if "cash_flow" not in datasets:
        return

    df = datasets["cash_flow"].copy()

    required_columns = {
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    }

    if not required_columns.issubset(df.columns):
        return

    df["calculated_net_cash"] = (
        df["operating_activity"]
        + df["investing_activity"]
        + df["financing_activity"]
    )

    tolerance = 10

    failures = df[
        (df["calculated_net_cash"] - df["net_cash_flow"]).abs() > tolerance
    ]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-09",
            severity="WARNING",
            table="cash_flow",
            row_id=row["id"],
            message=(
                f"Net cash mismatch. Expected {row['calculated_net_cash']:.2f}, "
                f"Found {row['net_cash_flow']:.2f}"
            ),
        )
def dq10_non_negative_fixed_assets(datasets):
    if "balance_sheet" not in datasets:
        return

    df = datasets["balance_sheet"]

    if "fixed_assets" not in df.columns:
        return

    failures = df[df["fixed_assets"] < 0]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-10",
            severity="WARNING",
            table="balance_sheet",
            row_id=row["id"],
            message=f"Negative fixed assets: {row['fixed_assets']}"
        )
def dq11_tax_rate_range(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"]

    if "tax_percentage" not in df.columns:
        return

    failures = df[
        (df["tax_percentage"] < 0) |
        (df["tax_percentage"] > 60)
    ]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-11",
            severity="WARNING",
            table="profit_loss",
            row_id=row["id"],
            message=f"Invalid tax percentage: {row['tax_percentage']}"
        )

def dq12_dividend_payout_cap(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"]

    if "divident_payout" not in df.columns:
        return

    failures = df[df["divident_payout"] > 200]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-12",
            severity="WARNING",
            table="profit_loss",
            row_id=row["id"],
            message=f"Dividend payout exceeds limit: {row['divident_payout']}"
        )
def dq13_url_validity(datasets):
    if "documents" not in datasets:
        return

    df = datasets["documents"]

    if "Annual_Report" not in df.columns:
        return

    failures = df[
        df["Annual_Report"].notna() &
        ~df["Annual_Report"].astype(str).str.startswith("http")
    ]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-13",
            severity="INFO",
            table="documents",
            row_id=row["id"],
            message=f"Malformed URL: {row['Annual_Report']}"
        )
def dq14_eps_sign_consistency(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"]

    required_columns = {"net_profit", "eps"}

    if not required_columns.issubset(df.columns):
        return

    failures = df[
        (
            (df["net_profit"] < 0) & (df["eps"] >= 0)
        ) |
        (
            (df["net_profit"] >= 0) & (df["eps"] < 0)
        )
    ]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-14",
            severity="WARNING",
            table="profit_loss",
            row_id=row["id"],
            message=(
                f"EPS sign inconsistent with Net Profit "
                f"(Net Profit={row['net_profit']}, EPS={row['eps']})"
            )
        )
def dq15_balance_sheet_extended(datasets):
    if "balance_sheet" not in datasets:
        return

    df = datasets["balance_sheet"].copy()

    required_columns = {"total_assets", "total_liabilities"}

    if not required_columns.issubset(df.columns):
        return

    tolerance = 0.01

    for _, row in df.iterrows():

        liabilities = row["total_liabilities"]

        if liabilities == 0:
            continue

        difference = abs(row["total_assets"] - liabilities) / abs(liabilities)

        if difference > tolerance:
            log_failure(
                rule="DQ-15",
                severity="INFO",
                table="balance_sheet",
                row_id=row["id"],
                message=f"Assets/Liabilities differ by {difference*100:.2f}%"
            )
def dq16_coverage_check(datasets):
    if "profit_loss" not in datasets:
        return

    df = datasets["profit_loss"]

    if not {"company_id", "year"}.issubset(df.columns):
        return

    coverage = (
        df.groupby("company_id")["year"]
        .nunique()
        .reset_index(name="years")
    )

    failures = coverage[coverage["years"] < 5]

    for _, row in failures.iterrows():
        log_failure(
            rule="DQ-16",
            severity="WARNING",
            table="profit_loss",
            row_id=None,
            message=f"{row['company_id']} has only {row['years']} years of data"
        )


def main():
    datasets = load_all_data()
    print(datasets["companies"].columns.tolist())

    dq01_primary_key_uniqueness(datasets)

    dq02_company_year_uniqueness(datasets)

    dq03_foreign_key_integrity(datasets)

    dq04_balance_sheet_balance(datasets)

    dq05_opm_cross_check(datasets)

    dq06_positive_sales(datasets)

    dq07_year_format(datasets)

    dq08_ticker_format(datasets)

    dq09_net_cash_check(datasets)

    dq10_non_negative_fixed_assets(datasets)

    dq11_tax_rate_range(datasets)

    dq12_dividend_payout_cap(datasets)

    dq13_url_validity(datasets)

    dq14_eps_sign_consistency(datasets)

    dq15_balance_sheet_extended(datasets)

    dq16_coverage_check(datasets)

    print("Datasets loaded successfully.")

    save_validation_results()

    print(f"Validation report saved to: {OUTPUT_DIR / 'validation_failures.csv'}")


if __name__ == "__main__":
    main()