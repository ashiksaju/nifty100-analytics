import pandas as pd

from src.etl import validator


def clear_results():
    validator.validation_results.clear()


def test_dq01_primary_key_uniqueness():
    clear_results()

    datasets = {
        "companies": pd.DataFrame({
            "id": [1, 1],
            "company_id": ["TCS", "TCS"],
        })
    }

    validator.dq01_primary_key_uniqueness(datasets)

    assert any(
        x["rule"] == "DQ-01"
        and x["severity"] == "CRITICAL"
        for x in validator.validation_results
    )


def test_dq02_company_year_uniqueness():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1, 2],
            "company_id": ["TCS", "TCS"],
            "year": [2024, 2024],
        })
    }

    validator.dq02_company_year_uniqueness(datasets)

    assert any(x["rule"] == "DQ-02" for x in validator.validation_results)


def test_dq03_foreign_key_integrity():
    clear_results()

    datasets = {
        "companies": pd.DataFrame({
            "id": ["TCS"],
        }),
        "profit_loss": pd.DataFrame({
            "id": [1],
            "company_id": ["INVALID"],
        }),
    }

    validator.dq03_foreign_key_integrity(datasets)

    assert any(
        x["rule"] == "DQ-03"
        and x["severity"] == "CRITICAL"
        for x in validator.validation_results
    )


def test_dq04_balance_sheet_balance():
    clear_results()

    datasets = {
        "balance_sheet": pd.DataFrame({
            "id": [1],
            "total_assets": [1000],
            "total_liabilities": [800],
        })
    }

    validator.dq04_balance_sheet_balance(datasets)

    assert any(x["rule"] == "DQ-04" for x in validator.validation_results)


def test_dq05_opm_cross_check():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "opm_percentage": [10],
            "operating_profit": [200],
            "sales": [1000],
        })
    }

    validator.dq05_opm_cross_check(datasets)

    assert any(x["rule"] == "DQ-05" for x in validator.validation_results)


def test_dq06_positive_sales():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "sales": [0],
        })
    }

    validator.dq06_positive_sales(datasets)

    assert any(x["rule"] == "DQ-06" for x in validator.validation_results)


def test_dq07_year_format():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "company_id": ["TCS"],
            "year": ["INVALID"],
        })
    }

    validator.dq07_year_format(datasets)

    assert any(x["rule"] == "DQ-07" for x in validator.validation_results)


def test_dq08_ticker_format():
    clear_results()

    datasets = {
        "companies": pd.DataFrame({
            "id": [1],
            "company_id": ["tcs"],
        })
    }

    validator.dq08_ticker_format(datasets)

    assert any(x["rule"] == "DQ-08" for x in validator.validation_results)


def test_dq09_net_cash_check():
    clear_results()

    datasets = {
        "cash_flow": pd.DataFrame({
            "id": [1],
            "operating_activity": [100],
            "investing_activity": [-20],
            "financing_activity": [10],
            "net_cash_flow": [500],
        })
    }

    validator.dq09_net_cash_check(datasets)

    assert any(x["rule"] == "DQ-09" for x in validator.validation_results)


def test_dq10_non_negative_fixed_assets():
    clear_results()

    datasets = {
        "balance_sheet": pd.DataFrame({
            "id": [1],
            "fixed_assets": [-100],
        })
    }

    validator.dq10_non_negative_fixed_assets(datasets)

    assert any(x["rule"] == "DQ-10" for x in validator.validation_results)


def test_dq11_tax_rate_range():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "tax_percentage": [100],
        })
    }

    validator.dq11_tax_rate_range(datasets)

    assert any(x["rule"] == "DQ-11" for x in validator.validation_results)


def test_dq12_dividend_payout_cap():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "divident_payout": [250],
        })
    }

    validator.dq12_dividend_payout_cap(datasets)

    assert any(x["rule"] == "DQ-12" for x in validator.validation_results)


def test_dq13_url_validity():
    clear_results()

    datasets = {
        "documents": pd.DataFrame({
            "id": [1],
            "Annual_Report": ["not_a_url"],
        })
    }

    validator.dq13_url_validity(datasets)

    assert any(x["rule"] == "DQ-13" for x in validator.validation_results)


def test_dq14_eps_sign_consistency():
    clear_results()

    datasets = {
        "profit_loss": pd.DataFrame({
            "id": [1],
            "net_profit": [-100],
            "eps": [10],
        })
    }

    validator.dq14_eps_sign_consistency(datasets)

    assert any(x["rule"] == "DQ-14" for x in validator.validation_results)