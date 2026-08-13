def calculate_cagr(start_value, end_value, years):
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula:
        ((End / Start) ** (1 / Years) - 1) * 100

    Returns:
        (value, flag)

    Flags:
        None
        DECLINE_TO_LOSS
        TURNAROUND
        BOTH_NEGATIVE
        ZERO_BASE
        INSUFFICIENT
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

    return cagr, None

def compute_cagr(values, years):
    """
    Compute CAGR from a list of yearly values.

    Returns:
        (cagr, flag)
    """

    if len(values) < years + 1:
        return None, "INSUFFICIENT"

    start_value = values[-(years + 1)]
    end_value = values[-1]

    return calculate_cagr(start_value, end_value, years)