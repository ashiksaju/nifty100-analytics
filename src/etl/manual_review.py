import random

from src.etl.loader import load_all_data


def main():
    datasets = load_all_data()

    companies = datasets["companies"]
    profit_loss = datasets["profit_loss"]

    random_companies = companies.sample(n=5, random_state=42)

    print("\nRandom Companies\n")

    for _, company in random_companies.iterrows():
        company_id = company["id"]

        years = (
            profit_loss[
                profit_loss["company_id"] == company_id
            ]["year"]
            .dropna()
            .tolist()
        )

        print(f"\n{company_id}")
        print(years)

    coverage = (
        profit_loss.groupby("company_id")["year"]
        .nunique()
        .reset_index(name="years")
    )

    print("\nCompanies with Less Than 5 Years of Data\n")

    low_coverage = coverage[coverage["years"] < 5]

    if low_coverage.empty:
        print("None")
    else:
        print(low_coverage)


if __name__ == "__main__":
    main()