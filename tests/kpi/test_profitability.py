from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_cross_check,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
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