import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "radar_charts"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

METRICS = {
    "ROE": "roe_percentage",
    "ROCE": "roce_percentage",
    "NPM": "net_profit_margin_pct",
    "D/E": "debt_to_equity",
    "FCF Score": "cfo_quality_score",
    "PAT CAGR": "pat_cagr_5yr",
    "Revenue CAGR": "revenue_cagr_5yr",
    "Composite": "composite_quality_score",
}

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

def latest_records(df):

    df = df.copy()

    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .astype(float)
    )

    df = (
        df
        .sort_values(
            ["company_id", "year_num"]
        )
        .groupby("company_id")
        .tail(1)
    )

    return df.drop(
        columns="year_num"
    )

def merge_peer_groups(financial, peer):

    latest = latest_records(financial)

    merged = latest.merge(
        peer,
        on="company_id",
        how="left",
    )

    return merged

def get_peer_average(df, peer_group):

    peer_df = df[
        df["peer_group_name"] == peer_group
    ]

    averages = []

    for column in METRICS.values():

        averages.append(
            pd.to_numeric(
                peer_df[column],
                errors="coerce",
            ).mean()
        )

    return averages

def get_nifty_average(df):

    averages = []

    for column in METRICS.values():

        averages.append(
            pd.to_numeric(
                df[column],
                errors="coerce",
            ).mean()
        )

    return averages

def company_values(company):

    values = []

    for column in METRICS.values():

        values.append(
            pd.to_numeric(
                company[column],
                errors="coerce",
            )
        )

    return values   

def clean(values):

    return [
        0 if pd.isna(v) else float(v)
        for v in values
    ]

def create_radar_chart(company, reference, peer_name):

    labels = list(METRICS.keys())

    company = clean(company)
    reference = clean(reference)

    company.append(company[0])
    reference.append(reference[0])

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    ).tolist()

    angles.append(angles[0])

    fig = plt.figure(figsize=(8, 8))

    ax = plt.subplot(
        111,
        polar=True,
    )

    ax.plot(
        angles,
        company,
        linewidth=2,
    )

    ax.fill(
        angles,
        company,
        alpha=0.25,
    )

    ax.plot(
        angles,
        reference,
        linestyle="--",
        linewidth=2,
    )

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(
        labels,
        fontsize=10,
    )

    ax.set_title(
        peer_name,
        fontsize=12,
    )

    plt.tight_layout()

def save_chart(company_id):

    plt.savefig(
        OUTPUT_DIR / f"{company_id}_radar.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

def generate_charts(df):

    for _, row in df.iterrows():

        company = company_values(row)

        if pd.isna(row["peer_group_name"]):

            reference = get_nifty_average(df)

            title = (
                f"{row['company_id']} (Nifty 100 Average)"
            )

        else:

            reference = get_peer_average(
                df,
                row["peer_group_name"],
            )

            title = (
                f"{row['company_id']} ({row['peer_group_name']})"
            )

        create_radar_chart(
            company,
            reference,
            title,
        )

        save_chart(
            row["company_id"],
        )

def main():

    financial, peer = load_tables()

    merged = merge_peer_groups(
        financial,
        peer,
    )

    generate_charts(
        merged,
    )

    print()

    print("Radar charts generated successfully.")

    print()

    print("Location:")

    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()