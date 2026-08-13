import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)

from src.analytics.cagr import compute_cagr

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
)


# ---------------------------------------------------------
# 1. NET PROFIT MARGIN
# ---------------------------------------------------------

def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(200, 0) is None


# ---------------------------------------------------------
# 2. OPERATING PROFIT MARGIN
# ---------------------------------------------------------

def test_operating_profit_margin():
    assert operating_profit_margin(300, 1000) == 30


def test_operating_profit_margin_zero_sales():
    assert operating_profit_margin(300, 0) is None


# ---------------------------------------------------------
# 3. ROE
# ---------------------------------------------------------

def test_roe_positive_equity():
    result = return_on_equity(200, 500, 500)
    assert result == 20


def test_roe_negative_equity():
    result = return_on_equity(200, -600, 500)
    assert result is None


# ---------------------------------------------------------
# 4. DEBT TO EQUITY
# ---------------------------------------------------------

def test_debt_to_equity():
    result = debt_to_equity(500, 500, 500)
    assert result == 0.5


def test_debt_free_company():
    result = debt_to_equity(0, 500, 500)
    assert result == 0


# ---------------------------------------------------------
# 5. INTEREST COVERAGE RATIO
# ---------------------------------------------------------

def test_interest_coverage_ratio():
    result = interest_coverage_ratio(300, 100, 100)
    assert result == 4


def test_interest_zero_returns_none():
    result = interest_coverage_ratio(300, 100, 0)
    assert result is None


# ---------------------------------------------------------
# 6. HIGH LEVERAGE FLAG
# ---------------------------------------------------------

def test_high_leverage_non_financial_company():
    assert high_leverage_flag(6, "Industrials") is True


def test_high_leverage_financial_company_exempt():
    assert high_leverage_flag(6, "Financials") is False


# ---------------------------------------------------------
# 7. CAGR
# ---------------------------------------------------------

def test_normal_cagr_calculation():
    result, flag = compute_cagr(
        [100, 110, 121, 133.1, 146.41, 161.051],
        5,
    )

    assert round(result, 2) == 10.00
    assert flag is None


def test_cagr_insufficient_history():
    result, flag = compute_cagr(
        [100, 110, 121],
        5,
    )

    assert result is None
    assert flag == "INSUFFICIENT"


def test_cagr_decline_to_loss():
    result, flag = compute_cagr(
        [100, 120, 140, 80, 20, -10],
        5,
    )

    assert result is None
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_turnaround():
    result, flag = compute_cagr(
        [-100, -50, 0, 50, 100, 200],
        5,
    )

    assert result is None
    assert flag == "TURNAROUND"


# ---------------------------------------------------------
# 8. OPM CROSS CHECK
# ---------------------------------------------------------

def test_opm_cross_check_within_threshold():
    assert opm_cross_check(20, 20.5) is True


def test_opm_cross_check_divergence():
    assert opm_cross_check(20, 25) is False


# ---------------------------------------------------------
# 9. CFO QUALITY SCORE
# ---------------------------------------------------------

def test_cfo_quality_score_positive():
    score, label = cfo_quality_score(150, 100)

    assert score is not None
    assert label is not None


def test_cfo_quality_score_negative():
    score, label = cfo_quality_score(-150, 100)

    assert score is not None
    assert label is not None


# ---------------------------------------------------------
# 10. ADDITIONAL KPI TESTS
# ---------------------------------------------------------

def test_free_cash_flow():
    assert free_cash_flow(500, -200) == 300


def test_net_debt():
    assert net_debt(500, 100) == 400


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2


def test_asset_turnover_invalid_assets():
    assert asset_turnover(1000, 0) is None