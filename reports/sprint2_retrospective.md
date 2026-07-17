# Sprint 2 Retrospective

## Objective

Develop a reusable financial ratio engine for the Nifty100 Analytics project.

---

## KPIs Implemented

- Net Profit Margin
- Operating Profit Margin
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)
- Debt to Equity Ratio
- Interest Coverage Ratio
- Net Debt
- Asset Turnover
- Free Cash Flow
- CFO Quality Score
- Capex Intensity
- Free Cash Flow Conversion
- Revenue CAGR
- PAT CAGR
- EPS CAGR

---

## Major Decisions

- Removed duplicate company-year records before ratio calculations.
- Excluded TTM records from CAGR computation.
- Used calculated ROE instead of the source ROE values because source data contained anomalies.
- Stored CAGR values for all historical rows of each company for easier screening.

---

## Edge Cases Handled

- Division by zero
- Negative equity
- Zero sales
- Negative profits
- Missing values
- CAGR turnaround cases
- CAGR decline-to-loss cases
- Both negative CAGR cases
- Zero base CAGR cases

---

## Validation

- All unit tests passed successfully.
- Ratio outputs verified against sample companies.
- Financial ratios stored successfully in SQLite.

---

## Sprint Outcome

Sprint 2 completed successfully with reusable analytics functions, validated KPIs, and an integrated financial_ratios table.