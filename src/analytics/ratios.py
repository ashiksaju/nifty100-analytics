def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin (%)

    Formula:
        (Net Profit / Sales) * 100

    Returns:
        None if sales is 0 or None.
    """

    if sales in (0, None):
        return None

    return (net_profit / sales) * 100
def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin (%)

    Formula:
        (Operating Profit / Sales) * 100

    Returns:
        None if sales is 0 or None.
    """

    if sales in (0, None):
        return None

    return (operating_profit / sales) * 100
def opm_cross_check(computed_opm, source_opm):
    """
    Compare computed OPM against source OPM.

    Returns:
        True  -> difference <= 1%
        False -> difference > 1%
    """

    if computed_opm is None or source_opm is None:
        return True

    return abs(computed_opm - source_opm) <= 1
def return_on_equity(net_profit, equity_capital, reserves):
    """
    Return on Equity (ROE)

    Formula:
        (Net Profit / (Equity Capital + Reserves)) * 100

    Returns:
        None if equity + reserves <= 0
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100

def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings,
):
    """
    Return on Capital Employed (ROCE)

    Formula:
        (EBIT / (Equity Capital + Reserves + Borrowings)) * 100

    Returns:
        None if capital employed <= 0
    """

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100
def return_on_assets(net_profit, total_assets):
    """
    Return on Assets (ROA)

    Formula:
        (Net Profit / Total Assets) * 100

    Returns:
        None if total_assets <= 0
    """

    if total_assets <= 0:
        return None

    return (net_profit / total_assets) * 100