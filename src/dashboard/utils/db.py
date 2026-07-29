import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[3]

DATABASE = (
    BASE_DIR
    / "data"
    / "database"
    / "nifty100.db"
)

@st.cache_data(ttl=600)
def get_companies():

    conn = sqlite3.connect(DATABASE)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn,
    )

    comparison = pd.read_sql(
        "SELECT * FROM comparison_table",
        conn,
    )

    conn.close()

    companies = companies.merge(
        comparison,
        on="company_name",
        how="left",
    )

    return companies

@st.cache_data(ttl=600)
@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):

    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT *
    FROM financial_ratios
    """

    params = []

    if ticker is not None:

        query += " WHERE company_id = ?"

        params.append(ticker)

        if year is not None:
            query += " AND year = ?"
            params.append(year)

    elif year is not None:

        query += " WHERE year = ?"

        params.append(year)

    query += " ORDER BY company_id, year"

    df = pd.read_sql(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM profit_loss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM balance_sheet
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM cash_flow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[ticker],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sectors():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    conn.close()

    df.columns = [
        "id",
        "company_id",
        "broad_sector",
        "sub_sector",
        "weight",
        "market_cap_category",
    ]

    return df

@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        conn,
        params=[group_name],
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_valuation(ticker):

    conn = sqlite3.connect(DATABASE)

    try:

        df = pd.read_sql(
            """
            SELECT *
            FROM valuation
            WHERE company_id = ?
            """,
            conn,
            params=[ticker],
        )

    except Exception:

        df = pd.DataFrame()

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_pl(company_id):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit
        FROM profit_loss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_ratios_history(company_id):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            roe_percentage,
            roce_percentage
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_financial_history(company_id):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            year,
            roe_percentage,
            roce_percentage
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_pros_cons(company_id):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            pros,
            cons
        FROM pros_cons
        WHERE company_id = ?
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_screener_data():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM comparison_table
        """,
        conn,
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_groups():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT DISTINCT peer_group_name
        FROM peer_groups
        ORDER BY peer_group_name
        """,
        conn,
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peer_data(group_name):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT *
        FROM comparison_table
        WHERE peer_group_name = ?
        """,
        conn,
        params=(group_name,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_profit_loss(company_id):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            year,
            sales,
            net_profit,
            eps
        FROM profit_loss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_sector_data():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
    """
    SELECT
        c.company_name,
        s.broad_sector,
        s.sub_sector,
        p.sales,
        f.roe_percentage,
        m.market_cap_crore
    FROM companies c
    JOIN sectors s
        ON c.id = s.company_id
    JOIN financial_ratios f
        ON c.id = f.company_id
    JOIN market_cap m
        ON c.id = m.company_id
    JOIN profit_loss p
        ON c.id = p.company_id
    """,
    conn,
)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_capital_allocation():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            c.company_name,
            c.capex_label,
            m.market_cap_crore
        FROM comparison_table c
        JOIN market_cap m
            ON c.company_id = m.company_id
        WHERE c.capex_label IS NOT NULL
        """,
        conn,
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_annual_reports():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            Year,
            Annual_Report
        FROM documents
        ORDER BY company_id, Year DESC
        """,
        conn,
    )

    conn.close()

    return df