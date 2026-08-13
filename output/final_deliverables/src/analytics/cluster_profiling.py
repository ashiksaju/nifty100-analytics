import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore


DB_PATH = "data/database/nifty100.db"

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


def calculate_fcf_cagr(financial_ratios):
    fcf = financial_ratios[
        ["company_id", "year", "free_cash_flow_cr"]
    ].copy()

    fcf = fcf[
        ~fcf["year"].str.contains("TTM", na=False)
    ].copy()

    fcf["year_date"] = pd.to_datetime(
        fcf["year"],
        format="%b %Y",
        errors="coerce",
    )

    results = []

    for company_id, group in fcf.groupby("company_id"):

        group = group.dropna(
            subset=["year_date", "free_cash_flow_cr"]
        ).sort_values("year_date")

        if len(group) < 2:
            results.append([company_id, np.nan])
            continue

        latest = group.iloc[-1]

        target_date = (
            latest["year_date"]
            - pd.DateOffset(years=5)
        )

        previous = group.iloc[
            (
                group["year_date"]
                - target_date
            )
            .abs()
            .argsort()[:1]
        ].iloc[0]

        start_fcf = previous["free_cash_flow_cr"]
        end_fcf = latest["free_cash_flow_cr"]

        if start_fcf > 0 and end_fcf > 0:
            cagr = (
                (end_fcf / start_fcf)
                ** (1 / 5)
                - 1
            ) * 100
        else:
            cagr = np.nan

        results.append(
            [company_id, cagr]
        )

    return pd.DataFrame(
        results,
        columns=[
            "company_id",
            "fcf_cagr_5yr",
        ],
    )


def load_data():

    conn = sqlite3.connect(DB_PATH)

    financial_ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        conn,
    )

    sectors = pd.read_sql_query(
        """
        SELECT company_id, broad_sector
        FROM sectors
        """,
        conn,
    )

    conn.close()

    financial_ratios = financial_ratios.merge(
        sectors[
            ["company_id", "broad_sector"]
        ].drop_duplicates(),
        on="company_id",
        how="left",
    )

    return financial_ratios


def prepare_latest_data(financial_ratios):

    financial_ratios["year_date"] = pd.to_datetime(
        financial_ratios["year"],
        format="%b %Y",
        errors="coerce",
    )

    historical = financial_ratios[
        ~financial_ratios["year"].str.contains(
            "TTM",
            na=False,
        )
    ].copy()

    historical = historical.sort_values(
        ["company_id", "year_date"]
    )

    latest = (
        historical
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    latest = latest[
        [
            "company_id",
            "broad_sector",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "operating_profit_margin_pct",
        ]
    ].copy()

    # Calculate FCF CAGR separately
    fcf_cagr = calculate_fcf_cagr(
        financial_ratios
    )

    # Add FCF CAGR
    latest = latest.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )

    # Convert all 5 clustering features to numeric
    for feature in FEATURES:
        latest[feature] = pd.to_numeric(
            latest[feature],
            errors="coerce",
        )

    return latest


def impute_sector_medians(data):

    data = data.copy()

    print("\nMissing values BEFORE imputation:")
    print(
        data[FEATURES].isna().sum()
    )

    for feature in FEATURES:

        sector_medians = (
            data
            .groupby("broad_sector")[feature]
            .median()
        )

        data[feature] = (
            data[feature]
            .fillna(
                data["broad_sector"]
                .map(sector_medians)
            )
        )

    # Final fallback:
    # if a whole sector has no valid value,
    # use overall median.
    for feature in FEATURES:

        overall_median = data[feature].median()

        data[feature] = data[feature].fillna(
            overall_median
        )

    print("\nMissing values AFTER imputation:")
    print(
        data[FEATURES].isna().sum()
    )

    return data


def load_cluster_labels():

    labels = pd.read_csv(
        "output/cluster_labels.csv"
    )

    return labels[
        [
            "company_id",
            "cluster_id",
        ]
    ]


def profile_clusters(data):

    cluster_labels = load_cluster_labels()

    data = data.merge(
        cluster_labels,
        on="company_id",
        how="left",
    )

    print("\nCluster distribution:")
    print(
        data["cluster_id"].value_counts()
        .sort_index()
    )

    # Mean
    cluster_mean = (
        data
        .groupby("cluster_id")[FEATURES]
        .mean()
        .round(2)
    )

    print("\nCluster Mean:")
    print(cluster_mean)

    # Median
    cluster_median = (
        data
        .groupby("cluster_id")[FEATURES]
        .median()
        .round(2)
    )

    print("\nCluster Median:")
    print(cluster_median)

    # Save profiles
    cluster_mean.to_csv(
        "output/cluster_mean.csv"
    )

    cluster_median.to_csv(
        "output/cluster_median.csv"
    )

    return data


def generate_correlation_heatmap(data):

    correlation_features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "fcf_cagr_5yr",
        "operating_profit_margin_pct",
    ]

    correlation = data[
        correlation_features
    ].corr(method="pearson")

    plt.figure(
        figsize=(10, 8)
    )

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
    )

    plt.title(
        "NIFTY100 Financial KPI Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        "reports/correlation_heatmap.png",
        dpi=300,
    )

    plt.close()

    print(
        "\nCorrelation heatmap saved to:"
    )
    print(
        "reports/correlation_heatmap.png"
    )


def generate_outlier_report(data):

    outlier_rows = []

    for sector, group in data.groupby(
        "broad_sector"
    ):

        for feature in FEATURES:

            values = group[feature]

            if values.std() == 0:
                continue

            scores = zscore(
                values,
                nan_policy="omit",
            )

            for index, score in zip(
                group.index,
                scores,
            ):

                if np.isnan(score):
                    continue

                if abs(score) > 3:

                    outlier_rows.append(
                        [
                            data.loc[
                                index,
                                "company_id",
                            ],
                            sector,
                            feature,
                            data.loc[
                                index,
                                feature,
                            ],
                            score,
                        ]
                    )

    outliers = pd.DataFrame(
        outlier_rows,
        columns=[
            "company_id",
            "broad_sector",
            "metric",
            "value",
            "z_score",
        ],
    )

    outliers.to_csv(
        "output/outlier_report.csv",
        index=False,
    )

    print(
        "\nOutlier report saved to:"
    )
    print(
        "output/outlier_report.csv"
    )

    print(
        "\nOutliers found:",
        len(outliers),
    )


def generate_portfolio_stats(data):

    rows = []

    for feature in FEATURES:

        values = data[feature]

        rows.append(
            [
                feature,
                values.quantile(0.10),
                values.quantile(0.25),
                values.quantile(0.50),
                values.quantile(0.75),
                values.quantile(0.90),
                values.mean(),
                values.std(),
            ]
        )

    stats = pd.DataFrame(
        rows,
        columns=[
            "KPI",
            "P10",
            "P25",
            "P50",
            "P75",
            "P90",
            "Mean",
            "Std",
        ],
    )

    stats = stats.round(2)

    stats.to_csv(
        "output/portfolio_stats.csv",
        index=False,
    )

    print(
        "\nPortfolio statistics saved to:"
    )
    print(
        "output/portfolio_stats.csv"
    )

    print("\nPortfolio statistics:")
    print(
        stats.to_string(index=False)
    )


if __name__ == "__main__":

    print("=" * 60)
    print("NIFTY100 CLUSTER PROFILING & STATISTICS")
    print("=" * 60)

    financial_ratios = load_data()

    print(
        "\nFinancial ratio rows:",
        len(financial_ratios),
    )

    data = prepare_latest_data(
        financial_ratios
    )

    print(
        "\nLatest companies:",
        data["company_id"].nunique(),
    )

    print("\nLatest financial data:")
    print(
        data[
            ["company_id"] + FEATURES
        ]
        .head(10)
        .to_string(index=False)
    )

    data = impute_sector_medians(
        data
    )

    print(
        "\nData ready for cluster profiling."
    )

    data = profile_clusters(
        data
    )

    generate_correlation_heatmap(
        data
    )

    generate_outlier_report(
        data
    )

    generate_portfolio_stats(
        data
    )

    print("\n" + "=" * 60)
    print("DAY 37 COMPLETED")
    print("=" * 60)