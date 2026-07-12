-- List all companies
SELECT * FROM companies;

-- Total companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- Companies by sector
SELECT sector, COUNT(*) AS company_count
FROM companies
GROUP BY sector
ORDER BY company_count DESC;

-- Profit & Loss records
SELECT company_id, year, sales, net_profit
FROM profit_loss
ORDER BY company_id, year;

-- Latest market capitalization
SELECT company_id, market_cap
FROM market_cap
ORDER BY market_cap DESC;

-- Financial ratios
SELECT company_id, roce_percentage, roe_percentage
FROM financial_ratios;

-- Stock prices for a company
SELECT *
FROM stock_prices
WHERE company_id = 'RELIANCE'
ORDER BY date;

-- Documents count
SELECT COUNT(*) AS total_documents
FROM documents;

-- Peer groups
SELECT *
FROM peer_groups;

-- Companies with available analysis
SELECT company_id, recommendation
FROM analysis;