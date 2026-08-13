import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "database" / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load companies, financial ratios, and sector information."""

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query(
        "SELECT id AS company_id FROM companies",
        conn,
    )

    financial_ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        conn,
    )

    sectors = pd.read_sql_query(
        "SELECT company_id, broad_sector FROM sectors",
        conn,
    )

    conn.close()

    # Keep only the 92-company universe
    financial_ratios = financial_ratios[
        financial_ratios["company_id"].isin(
            companies["company_id"]
        )
    ].copy()

    # Add sector information
    financial_ratios = financial_ratios.merge(
        sectors[
            ["company_id", "broad_sector"]
        ].drop_duplicates(),
        on="company_id",
        how="left",
    )

    return companies, financial_ratios


# ============================================================
# FCF CAGR
# ============================================================

def calculate_fcf_cagr(financial_ratios):
    """Calculate five-year FCF CAGR for each company."""

    fcf = financial_ratios[
        [
            "company_id",
            "year",
            "free_cash_flow_cr",
        ]
    ].copy()

    # Remove TTM
    fcf = fcf[
        ~fcf["year"].str.contains(
            "TTM",
            na=False,
        )
    ].copy()

    # Convert year
    fcf["year_date"] = pd.to_datetime(
        fcf["year"],
        format="%b %Y",
        errors="coerce",
    )

    results = []

    for company_id, group in fcf.groupby(
        "company_id"
    ):

        group = group.dropna(
            subset=[
                "year_date",
                "free_cash_flow_cr",
            ]
        ).sort_values("year_date")

        if len(group) < 2:
            results.append(
                [
                    company_id,
                    np.nan,
                ]
            )
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

        start_fcf = previous[
            "free_cash_flow_cr"
        ]

        end_fcf = latest[
            "free_cash_flow_cr"
        ]

        # CAGR is meaningful only when
        # both values are positive.
        if (
            start_fcf > 0
            and end_fcf > 0
        ):
            cagr = (
                (
                    end_fcf
                    / start_fcf
                )
                ** (1 / 5)
                - 1
            ) * 100

        else:
            cagr = np.nan

        results.append(
            [
                company_id,
                cagr,
            ]
        )

    return pd.DataFrame(
        results,
        columns=[
            "company_id",
            "fcf_cagr_5yr",
        ],
    )


# ============================================================
# PREPARE LATEST DATA
# ============================================================

def prepare_latest_data(
    financial_ratios,
    fcf_cagr,
):
    """Prepare one latest financial row for each company."""

    data = financial_ratios.copy()

    # Convert dates
    data["year_date"] = pd.to_datetime(
        data["year"],
        format="%b %Y",
        errors="coerce",
    )

    # Remove TTM
    data = data[
        ~data["year"].str.contains(
            "TTM",
            na=False,
        )
    ].copy()

    # Sort chronologically
    data = data.sort_values(
        [
            "company_id",
            "year_date",
        ]
    )

    # Latest row for every company
    latest = (
        data
        .groupby(
            "company_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    # Keep clustering features
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

    # Add FCF CAGR
    latest = latest.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )

    # Convert all features to numeric
    for feature in FEATURES:
        latest[feature] = pd.to_numeric(
            latest[feature],
            errors="coerce",
        )

    return latest


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================

def impute_sector_medians(
    data,
):
    """Impute missing feature values using sector medians."""

    data = data.copy()

    for feature in FEATURES:

        # Calculate sector median
        sector_medians = (
            data
            .groupby("broad_sector")[
                feature
            ]
            .median()
        )

        # Fill missing values
        data[feature] = (
            data[feature]
            .fillna(
                data[
                    "broad_sector"
                ].map(
                    sector_medians
                )
            )
        )

    return data


# ============================================================
# FINAL MISSING VALUE HANDLING
# ============================================================

def fill_remaining_missing_values(
    data,
):
    """Fill values that remain missing after sector imputation."""

    data = data.copy()

    for feature in FEATURES:

        # If a sector has no valid median,
        # use the overall median.
        overall_median = data[
            feature
        ].median()

        data[feature] = data[
            feature
        ].fillna(
            overall_median
        )

    return data


# ============================================================
# STANDARD SCALING
# ============================================================

def scale_features(data):
    """Standardize clustering features using StandardScaler."""

    scaler = StandardScaler()

    scaled_values = scaler.fit_transform(
        data[FEATURES]
    )

    scaled_data = pd.DataFrame(
        scaled_values,
        columns=FEATURES,
        index=data.index,
    )

    return scaled_data, scaler


# ============================================================
# KMEANS
# ============================================================

def run_kmeans(
    scaled_data,
):
    """Run KMeans clustering with five reproducible clusters."""

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(
        scaled_data
    )

    distances = model.transform(
        scaled_data
    )

    min_distances = distances.min(
        axis=1
    )

    return (
        model,
        labels,
        min_distances,
    )


# ============================================================
# ELBOW ANALYSIS
# ============================================================

def generate_elbow_plot(
    scaled_data,
):
    """Generate and save the KMeans elbow plot."""

    import matplotlib.pyplot as plt

    inertias = []

    k_values = range(2, 11)

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        model.fit(
            scaled_data
        )

        inertias.append(
            model.inertia_
        )

    plt.figure(
        figsize=(8, 5)
    )

    plt.plot(
        list(k_values),
        inertias,
        marker="o",
    )

    plt.xlabel(
        "Number of Clusters (k)"
    )

    plt.ylabel(
        "Inertia"
    )

    plt.title(
        "KMeans Elbow Analysis"
    )

    plt.xticks(
        list(k_values)
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    output_path = (
        REPORTS_DIR
        / "elbow_plot.png"
    )

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()

    return output_path


# ============================================================
# CLUSTER NAMES
# ============================================================

def assign_cluster_names(
    data,
    labels,
):
    """Assign descriptive names to the five financial clusters."""

    result = data[
        ["company_id"]
    ].copy()

    result["cluster_id"] = labels

    # Temporary names.
    # These can be refined after profiling clusters.
    cluster_names = {
        0: "High-Quality Compounders",
        1: "Defensive Dividend Payers",
        2: "Value Cyclicals",
        3: "Distressed or Turnaround",
        4: "Emerging Growth",
    }

    result["cluster_name"] = (
        result["cluster_id"]
        .map(cluster_names)
    )

    return result

def profile_clusters(data, cluster_results):
    """Calculate mean and median statistics for each cluster."""

    profile_data = data[
        ["company_id"] + FEATURES
    ].copy()

    profile_data = profile_data.merge(
        cluster_results[
            [
                "company_id",
                "cluster_id",
            ]
        ],
        on="company_id",
        how="left",
    )

    mean_profile = (
        profile_data
        .groupby("cluster_id")[FEATURES]
        .mean()
        .round(2)
    )

    median_profile = (
        profile_data
        .groupby("cluster_id")[FEATURES]
        .median()
        .round(2)
    )

    return mean_profile, median_profile


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NIFTY100 KMEANS CLUSTERING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    companies, financial_ratios = (
        load_data()
    )

    print(
        "\nCompanies:",
        companies["company_id"].nunique(),
    )

    print(
        "Financial ratio rows:",
        len(financial_ratios),
    )

    # --------------------------------------------------------
    # FCF CAGR
    # --------------------------------------------------------

    fcf_cagr = calculate_fcf_cagr(
        financial_ratios
    )

    print(
        "Companies with FCF CAGR:",
        fcf_cagr[
            "fcf_cagr_5yr"
        ].notna().sum(),
    )

    # --------------------------------------------------------
    # Prepare latest data
    # --------------------------------------------------------

    latest_data = prepare_latest_data(
        financial_ratios,
        fcf_cagr,
    )

    print(
        "\nLatest financial data:"
    )

    print(
        latest_data[
            ["company_id"] + FEATURES
        ]
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nTotal companies:",
        latest_data[
            "company_id"
        ].nunique(),
    )

    # --------------------------------------------------------
    # Missing values BEFORE imputation
    # --------------------------------------------------------

    print(
        "\nMissing values BEFORE imputation:"
    )

    print(
        latest_data[
            FEATURES
        ].isna().sum()
    )

    # --------------------------------------------------------
    # Sector median imputation
    # --------------------------------------------------------

    latest_data = (
        impute_sector_medians(
            latest_data
        )
    )

    # --------------------------------------------------------
    # Fill remaining missing values
    # --------------------------------------------------------

    latest_data = (
        fill_remaining_missing_values(
            latest_data
        )
    )

    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    print(
        "\nMissing values AFTER imputation:"
    )

    print(
        latest_data[
            FEATURES
        ].isna().sum()
    )

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaled_data, scaler = (
        scale_features(
            latest_data
        )
    )

    print(
        "\nScaled feature preview:"
    )

    print(
        scaled_data
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nScaled means:"
    )

    print(
        scaled_data
        .mean()
        .round(6)
    )

    print(
        "\nScaled standard deviations:"
    )

    print(
        scaled_data
        .std()
        .round(6)
    )

    # --------------------------------------------------------
    # Elbow plot
    # --------------------------------------------------------

    elbow_path = (
        generate_elbow_plot(
            scaled_data
        )
    )

    print(
        "\nElbow plot saved to:"
    )

    print(
        elbow_path
    )

    # --------------------------------------------------------
    # KMeans
    # --------------------------------------------------------

    model, labels, distances = (
        run_kmeans(
            scaled_data
        )
    )

    # --------------------------------------------------------
    # Cluster labels
    # --------------------------------------------------------

    cluster_results = (
        assign_cluster_names(
            latest_data,
            labels,
        )
    )

    cluster_results[
        "distance_from_centroid"
    ] = distances

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    output_path = (
        OUTPUT_DIR
        / "cluster_labels.csv"
    )

    cluster_results.to_csv(
        output_path,
        index=False,
    )

    print(
        "\nCluster labels saved to:"
    )

    print(
        output_path
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print(
        "\nCluster distribution:"
    )

    print(
        cluster_results[
            "cluster_id"
        ]
        .value_counts()
        .sort_index()
    )

    # --------------------------------------------------------
# Cluster profiling
# --------------------------------------------------------

    mean_profile, median_profile = profile_clusters(
    latest_data,
    cluster_results,
)

    print("\n" + "=" * 60)
    print("CLUSTER MEAN PROFILE")
    print("=" * 60)

    print(
    mean_profile.to_string()
)

    print("\n" + "=" * 60)
    print("CLUSTER MEDIAN PROFILE")
    print("=" * 60)

    print(
        median_profile.to_string()
)

    print(
        "\nDay 36 KMeans clustering completed."
    )
