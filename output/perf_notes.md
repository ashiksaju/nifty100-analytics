# Day 43 — Performance Notes

## Screener API Load Test

10 concurrent screener API requests were executed using Python threading.

- Requests: 10
- Successful requests: 10
- Failed requests: 0
- Total completion time: 0.234 seconds
- Target: less than 10 seconds
- Result: PASS

## Company Profile Performance

Company Profile API performance was tested for 5 tickers.

- TCS: PASS
- INFY: PASS
- HCLTECH: PASS
- LTIM: PASS
- TECHM: PASS
- Target: less than 3 seconds per ticker
- Result: PASS

## End-to-End Service Test

FastAPI and Streamlit were started simultaneously.

- FastAPI: port 8000
- Streamlit: port 8501
- Port conflict: None
- FastAPI health endpoint: PASS
- Streamlit availability: PASS
- Result: PASS

## Performance Bottlenecks

No significant performance bottlenecks were identified during Day 43 testing.

The screener API completed 10 concurrent requests in 0.234 seconds, which is well below the 10-second target.

Company Profile API requests also remained below the required 3-second threshold.

## SQLite Optimisation

No optimisation was required based on the measured performance results.

SQLite indexes should be added only where query profiling identifies frequent filtering or joining on `company_id` and `year`.