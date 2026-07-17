def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow (FCF)

    Formula:
        Operating Activity + Investing Activity

    Note:
        Investing Activity is usually negative.
        Negative FCF is allowed.
    """

    return operating_activity + investing_activity
def cfo_quality_score(cfo, pat):
    """
    CFO Quality Score

    Formula:
        CFO / PAT

    Returns:
        (ratio, label)

    Labels:
        High Quality
        Moderate
        Accrual Risk
    """

    if pat == 0:
        return None, None

    ratio = cfo / pat

    if ratio > 1.0:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return ratio, label
def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity

    Formula:
        abs(Investing Activity) / Sales * 100

    Returns:
        (percentage, label)
    """

    if sales == 0:
        return None, None

    percentage = abs(investing_activity) / sales * 100

    if percentage < 3:
        label = "Asset Light"
    elif percentage <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return percentage, label
def fcf_conversion_rate(free_cash_flow, operating_profit):
    """
    FCF Conversion Rate

    Formula:
        FCF / Operating Profit * 100

    Returns:
        None if operating_profit is 0.
    """

    if operating_profit == 0:
        return None

    return (free_cash_flow / operating_profit) * 100

def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None,
):
    """
    Classify capital allocation pattern based on
    CFO, CFI and CFF signs.
    """

    cfo_positive = cfo >= 0
    cfi_positive = cfi >= 0
    cff_positive = cff >= 0

    if cfo_positive and not cfi_positive and not cff_positive:
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    if cfo_positive and cfi_positive and not cff_positive:
        return "Liquidating Assets"

    if not cfo_positive and cfi_positive and cff_positive:
        return "Distress Signal"

    if not cfo_positive and not cfi_positive and cff_positive:
        return "Growth Funded by Debt"

    if cfo_positive and cfi_positive and cff_positive:
        return "Cash Accumulator"

    if not cfo_positive and not cfi_positive and not cff_positive:
        return "Pre-Revenue"

    if cfo_positive and not cfi_positive and cff_positive:
        return "Mixed"

    return "Unknown"