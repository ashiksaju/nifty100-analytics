import pytest

from src.etl.normaliser import normalize_ticker, normalize_year


@pytest.mark.parametrize(
    "value, expected",
    [
        (2023, 2023),
        ("2023", 2023),
        ("2022", 2022),
        ("FY2021", 2021),
        ("FY 2020", 2020),
        ("2019-20", 2019),
        ("2024-25", 2024),
        (" 2025 ", 2025),
        ("Year 2026", 2026),
        ("FY2018-19", 2018),
        ("2027 Annual", 2027),
        (None, None),
        ("", None),
        ("ABC", None),
        ("FY", None),
        ("20", None),
        ("1999", 1999),
        ("2000", 2000),
        ("2035", 2035),
        ("FY2030", 2030),
    ],
)
def test_normalize_year(value, expected):
    assert normalize_year(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("tcs", "TCS"),
        ("TCS", "TCS"),
        ("infy.ns", "INFY"),
        ("INFY.NS", "INFY"),
        ("reliance.bo", "RELIANCE"),
        ("HDFCBANK.BO", "HDFCBANK"),
        (" axisbank ", "AXISBANK"),
        ("SBIN", "SBIN"),
        ("lt.ns", "LT"),
        ("M&M", "M&M"),
        ("", ""),
        (None, None),
        ("   ", ""),
        ("abc.ns", "ABC"),
        ("xyz.bo", "XYZ"),
    ],
)
def test_normalize_ticker(value, expected):
    assert normalize_ticker(value) == expected