# Quick Start - Test Frontend-Backend Integration

## Prerequisites
- Python 3.13+ with FastAPI running
- Node.js 18+ with Vite frontend
- PostgreSQL database running
- All dependencies installed (`pip install -r requirements.txt`, `npm install`)

## 1. Start Backend Server

```bash
cd backend

# Terminal 1 - Run backend
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 2. Test Backend Endpoints

### Test Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000",
  "version": "2.0.0",
  "service": "Urbix API",
  "endpoints": {
    "ranking": "/api/v1/topsis/ranking-hibrido",
    "cities": "/api/v1/topsis/cities",
    "indicators": "/api/v1/topsis/indicators",
    "snapshots": "/api/v1/topsis/snapshots/{codigo_ibge}"
  }
}
```

### Test Cities Endpoint
```bash
curl http://localhost:8000/api/v1/topsis/cities
```

Expected: Array of cities with `codigo_ibge` and `nome`

### Test Indicators Endpoint
```bash
curl http://localhost:8000/api/v1/topsis/indicators
```

Expected: 50 indicators with `indice`, `nome`, `impacto`, `peso`, `categoria`

### Test Snapshots for a City
```bash
curl http://localhost:8000/api/v1/topsis/snapshots/4101408
```

Expected: Array of snapshots (may be empty if no rankings calculated yet)

### Test Ranking Calculation
```bash
curl -X POST http://localhost:8000/api/v1/topsis/ranking-hibrido \
  -H "Content-Type: application/json" \
  -d '[
    {"codigo_ibge": "4101408", "nome_cidade": "Apucarana"},
    {"codigo_ibge": "4113700", "nome_cidade": "Londrina"}
  ]'
```

Expected: JSON with `ranking` array and `detalhes_calculo`

## 3. Start Frontend Server

```bash
cd frontend

# Terminal 2 - Run frontend
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## 4. Test Frontend Integration

### Check Browser Console
- Open http://localhost:5173 in browser
- Open DevTools → Console
- Check for any errors (should be none)

### Test API Calls from Console
```javascript
// Test health check
import { checkHealth } from './src/services/api.js'
checkHealth().then(console.log)

// Test cities list
import { getCities } from './src/services/api.js'
getCities().then(console.log)

// Test indicators
import { getIndicators } from './src/services/api.js'
getIndicators().then(data => console.log(`Loaded ${data.length} indicators`))

// Test snapshots
import { getSnapshots } from './src/services/api.js'
getSnapshots('4101408').then(console.log)
```

### Test Input Validation
```javascript
import { validateRankingInput, validateIBGECode } from './src/utils/validation.js'

// Valid IBGE code
validateIBGECode('4101408')  // {valid: true}

// Invalid IBGE code
validateIBGECode('123')      // {valid: false, error: "..."}

// Valid ranking input
validateRankingInput([
  {codigo_ibge: '4101408', nome_cidade: 'Apucarana'},
  {codigo_ibge: '4113700', nome_cidade: 'Londrina'}
])  // {valid: true, errors: []}

// Invalid ranking (only 1 city)
validateRankingInput([
  {codigo_ibge: '4101408', nome_cidade: 'Apucarana'}
])  // {valid: false, errors: [...]}
```

## 5. Test Complete Ranking Workflow

### In Frontend Console:
```javascript
import { validateRankingInput, validateAPIResponse } from './src/utils/validation.js'
import { getHybridRanking } from './src/services/api.js'

const cities = [
  {codigo_ibge: '4101408', nome_cidade: 'Apucarana'},
  {codigo_ibge: '4113700', nome_cidade: 'Londrina'}
]

// Validate input
const validation = validateRankingInput(cities)
console.log('Input valid?', validation.valid)

// Get ranking if valid
if (validation.valid) {
  getHybridRanking(cities)
    .then(response => {
      console.log('Response valid?', validateAPIResponse(response, 'ranking').valid)
      console.log('Ranking:', response.ranking)
      console.log('Top city:', response.ranking[0].nome_cidade)
    })
    .catch(error => console.error('Error:', error.message))
}
```

## 6. Environment Variables Testing

### Development (.env.local)
```bash
# Check that frontend loads from localhost
echo $VITE_API_URL  # Should be http://localhost:8000/api/v1
```

### Production (.env.production)
```bash
# This will be used when deployed to Vercel
VITE_API_URL=https://urbix-backend.fly.dev/api/v1
```

## 7. Error Handling Tests

### Test Invalid IBGE Code
```javascript
import { getSnapshots } from './src/services/api.js'

// Should throw error
getSnapshots('123')
  .catch(error => console.error(error.message))
```

### Test Less Than 2 Cities
```javascript
import { getHybridRanking } from './src/services/api.js'

// Should throw HTTPException 400
getHybridRanking([
  {codigo_ibge: '4101408', nome_cidade: 'Apucarana'}
])
  .catch(error => console.error(error.message))
```

### Test API Timeout
```javascript
// Artificially slow API response
// Should timeout after 30 seconds
```

## 8. CORS Testing

### Verify Frontend Can Access Backend
- [ ] No CORS errors in browser console
- [ ] API calls return data
- [ ] Error responses include proper headers

### Test from Different Domains (optional)
```bash
# Test with curl
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:8000/api/v1/health -v
```

Should see:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

## 9. Database Snapshot Verification

### Check Snapshots Saved
```bash
# In psql or database client
SELECT * FROM indicator_snapshots 
ORDER BY data_calculo DESC 
LIMIT 5;
```

Should see recent snapshots with:
- `codigo_ibge`: City code
- `valores_indicadores`: JSON array of 50 values
- `data_calculo`: Calculation timestamp
- `fonte_dados`: "hibrido"

## 10. Production Checklist

### Before Deploying
- [ ] Backend syntax errors fixed: `python -m py_compile app/main.py`
- [ ] Frontend syntax errors fixed: `node -c src/services/api.js`
- [ ] All tests pass: `pytest tests/`
- [ ] CORS configured for production domain
- [ ] Environment variables set in Vercel
- [ ] Database migrations applied
- [ ] Backend deployed to Fly.io
- [ ] Frontend deployed to Vercel
- [ ] Health check responds
- [ ] All endpoints accessible from frontend

### Monitor Deployment
1. Check Fly.io logs: `flyctl logs`
2. Check Vercel logs: Vercel dashboard
3. Test production endpoints
4. Monitor error rates

## Troubleshooting

### Frontend Can't Connect to Backend
- [ ] Check CORS error in browser console
- [ ] Verify backend is running: `curl http://localhost:8000/api/v1/health`
- [ ] Check `VITE_API_URL` is correct
- [ ] Check firewall rules

### API Timeout
- [ ] Check backend is responding slowly
- [ ] Check database connection
- [ ] Check external API calls (IBGE, etc)
- [ ] Increase timeout if needed

### Validation Errors
- [ ] Check IBGE code format (must be 8 digits)
- [ ] Check city name (2-100 chars, Portuguese only)
- [ ] Check ranking has 2+ cities

### Database Snapshot Not Saved
- [ ] Check database connection in backend
- [ ] Check `IndicatorSnapshot` table exists
- [ ] Check database migrations applied

## Quick Commands

```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Database (if needed)
psql urbix_db

# Test URLs
# Health: http://localhost:8000/api/v1/health
# Cities: http://localhost:8000/api/v1/topsis/cities
# Frontend: http://localhost:5173
```

## Success Indicators

✅ Backend server running on port 8000
✅ Frontend dev server running on port 5173
✅ No CORS errors in browser console
✅ API endpoints return proper JSON
✅ Input validation works
✅ Ranking calculation completes
✅ Snapshots are saved to database
✅ All 50 indicators present in response

**When all checkmarks are complete, the integration is working! 🚀**
