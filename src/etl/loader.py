from pathlib import Path

import pandas as pd

from src.etl.normaliser import (
    normalize_numeric,
    normalize_percentage,
    normalize_text,
    normalize_url,
    normalize_year,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


FILE_MAPPING = {
    "companies": "companies.xlsx",
    "profit_loss": "profitandloss.xlsx",
    "balance_sheet": "balancesheet.xlsx",
    "cash_flow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "pros_cons": "prosandcons.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
}


def load_excel(file_name):
    file_path = RAW_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"{file_name} not found.")

    # These files have NO Bluestock title row
    if file_name in [
        "peer_groups.xlsx",
        "financial_ratios.xlsx",
    ]:
        return pd.read_excel(file_path)

    # All other Excel files have the Bluestock title row
    return pd.read_excel(
        file_path,
        skiprows=1,
    )

def load_all_data():
    datasets = {}

    for table_name, file_name in FILE_MAPPING.items():
        datasets[table_name] = load_excel(file_name)

    return datasets


if __name__ == "__main__":
    data = load_all_data()

    for name, df in data.items():
        print(f"{name:<20} {len(df):>6} rows")