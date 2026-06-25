# API Data Quality Issues - Diagnostic & Fix Plan

## Issues Found

### 1. SICONFI RGF Returns 0 Items
**Problem**: RGF endpoint returns empty `items: []` for Apucarana
- City didn't submit RGF data for Q3 2023
- DC (Dívida Consolidada) defaults to 0.0
- Makes municipal debt data unavailable

**Solution**: Implement fallback period strategy
```python
# Try Q3 first, then Q2, Q1 of same year
# If all fail, try previous year Q3
periods_to_try = [
    (2023, 3),  # Q3 2023 (current)
    (2023, 2),  # Q2 2023
    (2023, 1),  # Q1 2023
    (2022, 3),  # Q3 2022 (fallback year)
]
```

### 2. DataSUS Timeout (ReadError)
**Problem**: API call fails with `httpx.ReadError`
- Timeout set to 10 seconds (too short)
- Endpoint is slow and unreliable
- Falls back to "5 hospitais" for all cities

**Solution**: Increase timeout + add retry logic
```python
# Current: timeout=10.0 (too short)
# Fix: timeout=30.0 (accept endpoint is slow)
# Add: @retry decorator with exponential backoff
```

### 3. INEP Always Using Fallback
**Problem**: INEP API returns "dados inválidos", always uses Censo Escolar
- Real-time education data not being fetched
- Fallback values are generic, not city-specific

**Solution**: Improve INEP error handling
```python
# Check if API error is transient (retry) vs permanent (fallback)
# Use Censo 2023 data specifically for each city
```

### 4. Fallback Values Are Global (Not City-Specific)
**Problem**: When APIs fail, same fallback values used for all cities
- Results in identical or near-identical scores
- Doesn't reflect real differences between cities
- TOPSIS rankings become meaningless

**Solution**: Use city-specific fallback data
```python
# FALLBACK_SICONFI, FALLBACK_DATASUS, etc should have data for ~50 cities
# Not just 3-5 cities
```

## Implementation Priority

### HIGH PRIORITY (Fixes Data Quality Issues)
1. ✅ Increase DataSUS timeout to 30s
2. ✅ Add @retry decorator to DataSUS
3. ✅ Implement SICONFI period fallback strategy
4. ✅ Expand fallback databases with ~50 cities

### MEDIUM PRIORITY (Improves Robustness)
5. ✅ Add request retry loop in topsis.py
6. ✅ Log which fallback is being used
7. ✅ Add health check endpoint to verify API status

### LOW PRIORITY (Nice-to-Have)
8. Redis caching for API responses
9. Alert system when APIs are down
10. Real-time API status dashboard
