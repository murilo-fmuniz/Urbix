# Frontend-Backend Integration - Implementation Complete ✅

## Overview
This document describes the frontend-backend integration fixes implemented for the Urbix Smart Cities platform.

## Changes Made

### 1. Backend - main.py (CORS & Health Endpoint)
**File**: `backend/app/main.py`

#### CORS Configuration Updates
- ✅ Added production Vercel domain support
- Added: `https://urbix.vercel.app`
- Added: `https://*.vercel.app` (wildcard for all Vercel deployments)
- Kept localhost for development

#### Enhanced Health Endpoint
- Improved `/api/v1/health` endpoint
- Now returns detailed status with:
  - `status`: health status
  - `timestamp`: server timestamp
  - `version`: API version
  - `service`: service name
  - `endpoints`: list of all main endpoints

### 2. Backend - topsis.py (New Endpoints)
**File**: `backend/app/routers/topsis.py`

#### New Endpoints Added:

##### GET `/topsis/cities`
- Returns list of all 31 available municipalities
- Format: `[{codigo_ibge: string, nome: string}, ...]`
- Status codes: 200 (success), 500 (error)

##### GET `/topsis/indicators`  
- Returns all 50 indicators with metadata
- Format: 
  ```json
  [{
    "indice": 0,
    "nome": "Taxa Desemprego (%)",
    "impacto": "minimize",
    "peso": 0.02,
    "categoria": "ISO 37120"
  }, ...]
  ```
- Status codes: 200 (success), 500 (error)

##### GET `/topsis/snapshots/{codigo_ibge}`
- Returns historical snapshots for a city
- Validates IBGE code (8 digits)
- Format:
  ```json
  [{
    "data_calculo": "2024-01-15T10:30:00",
    "periodo_referencia": "2024-01",
    "fonte_dados": "hibrido",
    "quantidade_indicadores": 50,
    "valores_indicadores": [...]
  }, ...]
  ```
- Status codes: 200 (success), 400 (invalid IBGE), 500 (error)

### 3. Frontend - API Service (src/services/api.js)
**File**: `frontend/src/services/api.js`

#### Improvements:
- ✅ Environment variable support (`VITE_API_URL`)
- ✅ 30-second timeout configuration
- ✅ Response interceptor for error handling
- ✅ New health check function
- ✅ New cities list function  
- ✅ New indicators list function
- ✅ New snapshots query function
- ✅ Proper error handling with specific messages

#### Key Functions:
```javascript
// Health check
checkHealth() → {status, timestamp, version}

// Cities
getCities() → [{codigo_ibge, nome}, ...]

// Indicators
getIndicators() → [{indice, nome, impacto, peso, categoria}, ...]

// Snapshots
getSnapshots(codigoIBGE) → [{data_calculo, periodo_referencia, ...}, ...]

// Existing - Ranking
getHybridRanking(cities) → {ranking, detalhes_calculo}
```

### 4. Frontend - Environment Variables
**Files**: 
- `frontend/.env.local` (development)
- `frontend/.env.production` (production)

#### Development (.env.local):
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_ENABLE_LOGGING=true
VITE_DEBUG_MODE=true
```

#### Production (.env.production):
```env
VITE_API_URL=https://urbix-backend.fly.dev/api/v1
VITE_ENABLE_LOGGING=false
VITE_DEBUG_MODE=false
```

> Note: Update `VITE_API_URL` in production when backend is deployed

### 5. Frontend - Input Validation
**File**: `frontend/src/utils/validation.js`

#### Validation Functions:
- `validateIBGECode()` - Validates 8-digit IBGE code
- `validateCityName()` - Validates city name (2-100 chars, Portuguese chars allowed)
- `validateIndicatorValue()` - Validates numeric indicator (0-100)
- `validateCityInput()` - Validates single city object
- `validateRankingInput()` - Validates array of cities (minimum 2, maximum 50)
- `validateAPIResponse()` - Validates API responses by type

#### Usage Example:
```javascript
import { validateRankingInput, validateIBGECode } from '@/utils/validation.js';

// Validate input before sending
const validation = validateRankingInput(citiesArray);
if (!validation.valid) {
  // Display validation.errors to user
  console.error(validation.errors);
}

// Validate IBGE code
const ibgeCheck = validateIBGECode('4101408');
if (!ibgeCheck.valid) {
  console.error(ibgeCheck.error); // "Código IBGE deve ter exatamente 8 dígitos"
}
```

## Error Handling

### Status Codes
- **200**: Success
- **400**: Bad Request (validation failure, <2 cities, invalid IBGE)
- **422**: Unprocessable Entity (Pydantic validation)
- **500**: Server Error
- **502**: Bad Gateway (API failures)

### Frontend Error Handling
- Try-catch blocks around all API calls
- Specific error messages for different status codes
- Input validation before sending to API
- Response validation after receiving from API

## Testing Checklist

### Backend Tests
- [ ] `python -m pytest tests/` - All tests pass
- [ ] `python backend/app/main.py` - Server starts on 8000
- [ ] `curl http://localhost:8000/api/v1/health` - Returns JSON status
- [ ] `curl http://localhost:8000/api/v1/topsis/cities` - Returns city list
- [ ] `curl http://localhost:8000/api/v1/topsis/indicators` - Returns 50 indicators
- [ ] `curl http://localhost:8000/api/v1/topsis/snapshots/4101408` - Returns snapshots

### Frontend Tests
- [ ] `npm run dev` - Frontend starts on 5173
- [ ] Frontend can call API health endpoint
- [ ] Frontend can fetch and display cities list
- [ ] Frontend can fetch and display indicators
- [ ] Frontend can fetch historical snapshots
- [ ] Ranking calculation works with 2+ cities
- [ ] Input validation prevents invalid submissions
- [ ] Error messages display properly

### Integration Tests
- [ ] CORS allows frontend to call backend
- [ ] API timeout handling works (30 seconds)
- [ ] Error responses format correctly
- [ ] IBGE validation works (8 digits required)
- [ ] Snapshots are persisted in database

## Deployment Configuration

### Vercel (Frontend)
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set start command: `npm run preview`
4. Environment variables:
   - `VITE_API_URL`: Production backend URL

### Fly.io (Backend)
1. Create app: `flyctl app create urbix-backend`
2. Deploy: `flyctl deploy`
3. Database connection string in environment

### Production URLs
- Frontend: `https://urbix.vercel.app`
- Backend: `https://urbix-backend.fly.dev`
- API: `https://urbix-backend.fly.dev/api/v1`

## Migration Notes

### For Frontend Developers
1. Use `VITE_API_URL` from environment instead of hardcoded URLs
2. Always import validation functions for user input
3. Wrap API calls with try-catch and display user-friendly errors
4. Check API response with `validateAPIResponse()` before using data

### For Backend Developers
1. New endpoints follow REST conventions
2. All endpoints return 400/500 status codes on errors
3. Snapshots are automatically saved in TOPSIS calculation
4. Cities and indicators are queried from database

## Known Limitations

- IBGE codes must be exactly 8 digits (no validation for real/fake codes)
- City names must contain only Portuguese characters (a-z, ñ, ç, accents)
- Indicators must be 0-100 range
- Maximum 50 cities per ranking calculation
- Minimum 2 cities required for TOPSIS

## Future Improvements

- [ ] Implement city search/filter endpoint
- [ ] Add pagination to cities and indicators endpoints
- [ ] Implement caching for indicators list (changes rarely)
- [ ] Add batch snapshots query (multiple cities)
- [ ] Implement webhook for ranking notifications
- [ ] Add GraphQL API alongside REST

## Files Changed

### Backend
- ✅ `backend/app/main.py` - CORS + Health endpoint
- ✅ `backend/app/routers/topsis.py` - 3 new endpoints

### Frontend
- ✅ `frontend/src/services/api.js` - Enhanced with new functions
- ✅ `frontend/.env.local` - Development configuration
- ✅ `frontend/.env.production` - Production configuration
- ✅ `frontend/src/utils/validation.js` - Validation utilities

## Summary

All 10 frontend-backend integration fix points have been implemented:

1. ✅ CORS Configuration - Updated for production
2. ✅ Health Check Endpoint - Enhanced with details
3. ✅ Error Response Status Codes - Implemented consistently
4. ✅ Response Format Consistency - All endpoints follow REST
5. ✅ Input Validation - Comprehensive validation utilities
6. ✅ Cities List Endpoint - GET /topsis/cities
7. ✅ Indicators List Endpoint - GET /topsis/indicators (50 indicators)
8. ✅ Snapshot Query Endpoint - GET /topsis/snapshots/{codigo_ibge}
9. ✅ Frontend API Client - Enhanced api.js with new functions
10. ✅ Environment Configuration - .env files for dev and production

**Status**: Integration complete and ready for testing and deployment.
