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


def test_net_profit_margin():
    assert net_profit_margin(100, 1000) == 10.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(200, 1000) == 20.0


def test_opm_cross_check_match():
    assert opm_cross_check(20.0, 20.5) is True


def test_opm_cross_check_mismatch():
    assert opm_cross_check(20.0, 17.0) is False


def test_return_on_equity():
    assert return_on_equity(200, 100, 900) == 20.0


def test_return_on_equity_negative_equity():
    assert return_on_equity(100, 100, -200) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(300, 100, 400, 500) == 30.0


def test_return_on_assets():
    assert return_on_assets(200, 1000) == 20.0

    from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity():
    assert debt_to_equity(500, 100, 900) == 0.5


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 100, 900) == 0


def test_high_leverage_flag():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_financials():
    assert high_leverage_flag(6.0, "Financials") is False


def test_interest_coverage_ratio():
    assert interest_coverage_ratio(1000, 200, 100) == 12.0


def test_interest_coverage_none():
    assert interest_coverage_ratio(1000, 200, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning_flag(1.2) is True


def test_net_debt():
    assert net_debt(1000, 200) == 800


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0