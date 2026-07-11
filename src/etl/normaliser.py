from __future__ import annotations

import re
import pandas as pd


def normalize_year(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    match = re.search(r"(19|20)\d{2}", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):
    if pd.isna(value):
        return None

    ticker = str(value).strip().upper()
    ticker = ticker.replace(".NS", "")
    ticker = ticker.replace(".BO", "")
    ticker = ticker.replace(" ", "")

    return ticker


def normalize_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_numeric(value):
    if pd.isna(value):
        return None

    if value == "":
        return None

    if isinstance(value, str):
        value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


def normalize_percentage(value):
    if pd.isna(value):
        return None

    value = str(value).replace("%", "").strip()

    try:
        return float(value)
    except ValueError:
        return None


def normalize_url(value):
    if pd.isna(value):
        return None

    url = str(value).strip()

    if url == "":
        return None

    return url