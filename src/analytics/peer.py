import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"


METRICS = [
    "roe_percentage",
    "roce_percentage",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


def load_tables():

    conn = sqlite3.connect(DATABASE)

    financial = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    peer = pd.read_sql(
        "SELECT * FROM peer_groups",
        conn,
    )

    conn.close()

    return financial, peer


def latest_financials(financial):

    latest = (
        financial
        .copy()
    )

    latest["year_num"] = (
        latest["year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .astype(float)
    )

    latest = latest.sort_values(
        [
            "company_id",
            "year_num",
        ]
    )

    latest = (
        latest
        .groupby("company_id")
        .tail(1)
        .drop(columns="year_num")
    )

    return latest


def merge_peer_groups(financial, peer):

    latest = latest_financials(financial)

    merged = latest.merge(
        peer,
        on="company_id",
        how="left",
    )

    return merged


def clean_numeric(df):

    for metric in METRICS:

        df[metric] = pd.to_numeric(
            df[metric],
            errors="coerce",
        )

    return df

def calculate_percentiles(merged):

    rows = []

    grouped = merged.groupby("peer_group_name")

    for peer_name, peer_df in grouped:

        for metric in METRICS:

            ascending = False

            if metric == "debt_to_equity":
                ascending = True

            ranked = (
                peer_df[["company_id", "year", metric]]
                .copy()
            )

            ranked = ranked.dropna(
                subset=[metric]
            )

            if len(ranked) == 0:
                continue

            ranked["percentile_rank"] = ranked[metric].rank(
            pct=True,
            ascending=True,
)           * 100

            if metric != "debt_to_equity":
             ranked["percentile_rank"] = 100 - ranked["percentile_rank"] + (100 / len(ranked))

            ranked["metric"] = metric

            ranked["peer_group_name"] = peer_name

            ranked.rename(
                columns={
                    metric: "value",
                },
                inplace=True,
            )

            rows.append(ranked)

    result = pd.concat(
        rows,
        ignore_index=True,
    )

    return result

def add_missing_companies(result, merged):

    missing = merged[
        merged["peer_group_name"].isna()
    ]

    if len(missing) == 0:
        return result

    rows = []

    for _, company in missing.iterrows():

        for metric in METRICS:

            rows.append(
                {
                    "company_id": company["company_id"],
                    "year": company["year"],
                    "peer_group_name": "No peer group assigned",
                    "metric": metric,
                    "value": company.get(metric),
                    "percentile_rank": None,
                }
            )

    missing_df = pd.DataFrame(rows)

    result = pd.concat(
        [
            result,
            missing_df,
        ],
        ignore_index=True,
    )

    return result

def save_results(result):

    conn = sqlite3.connect(DATABASE)

    result.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

def main():

    financial, peer = load_tables()

    merged = merge_peer_groups(
        financial,
        peer,
)

    merged = clean_numeric(
        merged,
)
    result = calculate_percentiles(
    merged,
)

    result = add_missing_companies(
    result,
    merged,
)

    save_results(
     result,
     
)

    print()

    print(result.head())

    print()

    print("Rows :", len(result))

    print("Metrics :", result["metric"].nunique())

    print("Peer Groups :", result["peer_group_name"].nunique())


    conn = sqlite3.connect(DATABASE)

    check = pd.read_sql(
    "SELECT * FROM peer_percentiles LIMIT 10",
    conn,
)

    conn.close()

    print(check)


if __name__ == "__main__":
    main()