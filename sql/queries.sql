SELECT COUNT(*) AS total_companies
FROM companies;
SELECT
    company_id,
    year,
    net_profit
FROM profit_loss
WHERE net_profit > 1000
ORDER BY net_profit DESC;
SELECT
    company_name,
    roe_percentage
FROM companies
ORDER BY roe_percentage DESC;
SELECT
    broad_sector,
    COUNT(*) AS companies
FROM sectors
GROUP BY broad_sector
ORDER BY companies DESC;
SELECT
    AVG(pe_ratio) AS average_pe
FROM market_cap;
SELECT
    company_id,
    year,
    market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;
SELECT
    company_id,
    date,
    close_price
FROM stock_prices
ORDER BY date DESC;
SELECT
    company_id,
    year,
    net_cash_flow
FROM cash_flow
WHERE net_cash_flow < 0;
SELECT
    company_id,
    year,
    debt_to_equity
FROM financial_ratios
WHERE debt_to_equity > 1;
SELECT
    c.company_name,
    p.year,
    p.sales,
    p.net_profit,
    b.total_assets,
    m.market_cap_crore
FROM companies c
JOIN profit_loss p
    ON c.id = p.company_id
JOIN balance_sheet b
    ON p.company_id = b.company_id
    AND p.year = b.year
JOIN market_cap m
    ON p.company_id = m.company_id
    AND p.year = m.year;