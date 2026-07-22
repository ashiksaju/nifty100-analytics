import pandas as pd

file_path = "data/raw/financial_ratios.xlsx"

df = pd.read_excel(file_path)

before = len(df)

df = df.drop_duplicates(
    subset=["company_id", "year"],
    keep="first",
)

after = len(df)

with pd.ExcelWriter(
    file_path,
    engine="openpyxl",
) as writer:
    df.to_excel(
        writer,
        index=False,
    )

print(f"File      : {file_path}")
print(f"Before    : {before}")
print(f"After     : {after}")
print(f"Removed   : {before - after}")
print("Financial ratios cleaned successfully.")