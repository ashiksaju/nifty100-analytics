from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow():
    assert free_cash_flow(1000, -300) == 700


def test_negative_free_cash_flow():
    assert free_cash_flow(500, -700) == -200


def test_cfo_quality_high():
    ratio, label = cfo_quality_score(1200, 1000)
    assert round(ratio, 2) == 1.20
    assert label == "High Quality"


def test_cfo_quality_moderate():
    ratio, label = cfo_quality_score(700, 1000)
    assert round(ratio, 2) == 0.70
    assert label == "Moderate"


def test_cfo_quality_accrual():
    ratio, label = cfo_quality_score(300, 1000)
    assert round(ratio, 2) == 0.30
    assert label == "Accrual Risk"


def test_cfo_quality_pat_zero():
    ratio, label = cfo_quality_score(100, 0)
    assert ratio is None
    assert label is None


def test_capex_asset_light():
    pct, label = capex_intensity(-20, 1000)
    assert round(pct, 2) == 2.00
    assert label == "Asset Light"


def test_capex_capital_intensive():
    pct, label = capex_intensity(-150, 1000)
    assert round(pct, 2) == 15.00
    assert label == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion_rate(700, 1000) == 70.0


def test_fcf_conversion_none():
    assert fcf_conversion_rate(100, 0) is None


def test_pattern_reinvestor():
    assert capital_allocation_pattern(100, -50, -20) == "Reinvestor"


def test_pattern_shareholder_returns():
    assert (
        capital_allocation_pattern(100, -50, -20, 1.2)
        == "Shareholder Returns"
    )


def test_pattern_distress():
    assert (
        capital_allocation_pattern(-100, 50, 30)
        == "Distress Signal"
    )


def test_pattern_cash_accumulator():
    assert (
        capital_allocation_pattern(100, 50, 30)
        == "Cash Accumulator"
    )