import pytest

from src.etl.loader import (
    FILE_MAPPING,
    load_excel,
    load_all_data,
)


def test_file_mapping_contains_all_expected_files():
    assert len(FILE_MAPPING) == 12

    expected_tables = {
        "companies",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "analysis",
        "documents",
        "pros_cons",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "sectors",
        "stock_prices",
    }

    assert set(FILE_MAPPING.keys()) == expected_tables


def test_companies_row_count():
    df = load_excel("companies.xlsx")
    assert len(df) == 92


def test_profit_loss_row_count():
    df = load_excel("profitandloss.xlsx")
    assert len(df) == 1262


def test_balance_sheet_row_count():
    df = load_excel("balancesheet.xlsx")
    assert len(df) == 1224


def test_cash_flow_row_count():
    df = load_excel("cashflow.xlsx")
    assert len(df) == 1163


def test_documents_row_count():
    df = load_excel("documents.xlsx")
    assert len(df) == 1585


def test_financial_ratios_row_count():
    df = load_excel("financial_ratios.xlsx")
    assert len(df) == 1065


def test_market_cap_row_count():
    df = load_excel("market_cap.xlsx")
    assert len(df) == 551


def test_companies_columns():
    df = load_excel("companies.xlsx")

    expected_columns = {
        "id",
        "company_name",
        "website",
        "nse_profile",
        "bse_profile",
    }

    assert expected_columns.issubset(set(df.columns))


def test_financial_ratios_columns():
    df = load_excel("financial_ratios.xlsx")

    expected_columns = {
        "company_id",
        "year",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "free_cash_flow_cr",
    }

    assert expected_columns.issubset(set(df.columns))


def test_load_all_data_returns_all_datasets():
    data = load_all_data()

    assert len(data) == 12

    for table_name in FILE_MAPPING:
        assert table_name in data
        assert len(data[table_name]) > 0