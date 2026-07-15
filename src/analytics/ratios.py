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

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity Ratio

    Formula:
        Borrowings / (Equity Capital + Reserves)

    Rules:
        - Return 0 if borrowings == 0 (Debt Free)
        - Return None if equity <= 0
    """

    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return borrowings / equity

def high_leverage_flag(debt_to_equity_ratio, broad_sector):
    """
    High Leverage Flag

    Rules:
        - Financials sector is exempt.
        - Return True if D/E > 5.
        - Otherwise return False.
    """

    if debt_to_equity_ratio is None:
        return False

    if broad_sector == "Financials":
        return False

    return debt_to_equity_ratio > 5

def interest_coverage_ratio(
    operating_profit,
    other_income,
    interest,
):
    """
    Interest Coverage Ratio (ICR)

    Formula:
        (Operating Profit + Other Income) / Interest

    Returns:
        None if interest == 0
    """

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest

def icr_label(interest_coverage):
    """
    Display label for Interest Coverage Ratio.
    """

    if interest_coverage is None:
        return "Debt Free"

    return ""

def icr_warning_flag(interest_coverage):
    """
    Warning flag for low Interest Coverage Ratio.
    """

    if interest_coverage is None:
        return False

    return interest_coverage < 1.5

def net_debt(borrowings, investments):
    """
    Net Debt

    Formula:
        Borrowings - Investments
    """

    return borrowings - investments

def asset_turnover(sales, total_assets):
    """
    Asset Turnover

    Formula:
        Sales / Total Assets

    Returns:
        None if total_assets <= 0
    """

    if total_assets <= 0:
        return None

    return sales / total_assets