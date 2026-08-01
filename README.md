## Dashboard

Run the Streamlit dashboard using:

```bash
streamlit run src/dashboard/app.py
```

## Dashboard Screens

### 1. Dashboard
Provides an overview of the application with quick navigation and summary insights.

### 2. Company Profile
Displays key financial metrics, company information, historical performance, and interactive charts.

### 3. Stock Screener
Allows filtering companies using financial metrics such as ROE, ROCE, P/E, Debt-to-Equity, and Market Capitalization.

### 4. Trend Analysis
Shows historical financial trends with interactive line charts and multiple metric comparison.

### 5. Sector Analysis
Provides sector-wise analysis using interactive bubble charts and sector median KPI comparisons.

### 6. Capital Allocation Map
Visualizes companies grouped by capital allocation patterns using an interactive treemap.

### 7. Annual Reports
Displays available annual reports with downloadable BSE report links for each company.

### 8. Valuation Insights
Shows valuation metrics including FCF Yield, sector median P/E comparison, and valuation flags (Fair, Discount, Caution).

## Sprint 4 Retrospective

### UX Decisions

- Used Streamlit for a simple and responsive dashboard interface.
- Added interactive dropdowns and filters for better navigation.
- Used Plotly interactive charts with responsive sizing.
- Added clear KPI cards for important financial metrics.
- Kept navigation simple using separate dashboard pages.

### Data Edge Cases

- Companies with fewer than 10 years of financial history were handled without crashing.
- Missing financial values (None/NaN) are displayed as **N/A** instead of causing runtime errors.
- Stock Screener was tested using extreme filter values to ensure stable behaviour.
- Annual Reports page handles unavailable report links gracefully.

### Performance Findings

- Company Profile page loading time remained below the required 3-second limit during testing.
- Database queries were optimized by selecting only required columns.
- Interactive charts resize correctly without overflowing the dashboard layout.