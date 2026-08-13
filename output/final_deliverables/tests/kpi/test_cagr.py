from src.analytics.cagr import calculate_cagr, compute_cagr


def test_normal_cagr():
    value, flag = calculate_cagr(100, 200, 5)
    assert round(value, 2) == 14.87
    assert flag is None


def test_decline_to_loss():
    value, flag = calculate_cagr(100, -50, 5)
    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():
    value, flag = calculate_cagr(-100, 50, 5)
    assert value is None
    assert flag == "TURNAROUND"


def test_both_negative():
    value, flag = calculate_cagr(-100, -50, 5)
    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():
    value, flag = calculate_cagr(0, 100, 5)
    assert value is None
    assert flag == "ZERO_BASE"


def test_insufficient_years():
    value, flag = calculate_cagr(100, 200, 0)
    assert value is None
    assert flag == "INSUFFICIENT"


def test_compute_cagr_3yr():
    value, flag = compute_cagr([100, 110, 120, 130], 3)
    assert round(value, 2) == 9.14
    assert flag is None


def test_compute_cagr_5yr():
    value, flag = compute_cagr([100, 120, 140, 160, 180, 200], 5)
    assert round(value, 2) == 14.87
    assert flag is None


def test_compute_insufficient():
    value, flag = compute_cagr([100, 120], 5)
    assert value is None
    assert flag == "INSUFFICIENT"


def test_compute_zero_base():
    value, flag = compute_cagr([0, 20, 40, 60], 3)
    assert value is None
    assert flag == "ZERO_BASE"