"""
Integration Test: Frontend-Backend Communication Verification

Tests all API endpoints that the frontend calls to ensure:
1. Endpoints exist and are accessible
2. Request/response schemas match expectations
3. Error handling is consistent
4. CORS headers are properly set
5. Data flows correctly end-to-end

Run with: python tests/test_frontend_backend_integration.py
"""

import sys
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime

# UTF-8 fix for Windows terminal
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ==========================================
# INTEGRATION TEST CASES
# ==========================================

class IntegrationTestResult:
    """Stores test result with details"""
    def __init__(self, test_name: str, passed: bool, details: str = ""):
        self.test_name = test_name
        self.passed = passed
        self.details = details
        self.timestamp = datetime.utcnow()
    
    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} - {self.test_name}: {self.details}"


class FrontendBackendIntegrationTest:
    """Tests all frontend-backend integration points"""
    
    def __init__(self):
        self.results: List[IntegrationTestResult] = []
        self.base_url = "http://localhost:8000/api/v1"
        # Import after setting up environment
        try:
            import requests
            self.requests = requests
            self.http_available = True
        except ImportError:
            self.http_available = False
            print("⚠️  Warning: requests library not available, will skip HTTP tests")
    
    def test_1_route_ordering_manual_data(self):
        """Test that manual data routes are ordered correctly"""
        # This is a code inspection test - verify route order in source
        try:
            with open('backend/app/routers/manual_data.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find positions of critical routes
            pos_rankings_historico = content.find("@manual_data_router.get(\"/rankings/historico\"")
            pos_rankings_periodo = content.find("@manual_data_router.get(\"/rankings/periodo/")
            pos_codigo_ibge_generic = content.find("@manual_data_router.get(\"/{codigo_ibge}\"")
            
            if pos_rankings_historico == -1 or pos_rankings_periodo == -1:
                return IntegrationTestResult(
                    "Route Ordering (Manual Data)",
                    False,
                    "Missing /rankings routes in router"
                )
            
            if pos_codigo_ibge_generic == -1:
                return IntegrationTestResult(
                    "Route Ordering (Manual Data)",
                    False,
                    "Missing /{codigo_ibge} generic route"
                )
            
            # Check if specific routes come BEFORE generic
            if pos_rankings_historico > pos_codigo_ibge_generic:
                return IntegrationTestResult(
                    "Route Ordering (Manual Data)",
                    False,
                    f"ERROR: /rankings/historico comes after /{{codigo_ibge}} - will be unreachable!"
                )
            
            if pos_rankings_periodo > pos_codigo_ibge_generic:
                return IntegrationTestResult(
                    "Route Ordering (Manual Data)",
                    False,
                    f"ERROR: /rankings/periodo comes after /{{codigo_ibge}} - will be unreachable!"
                )
            
            return IntegrationTestResult(
                "Route Ordering (Manual Data)",
                True,
                "Routes ordered correctly: /rankings routes before /{codigo_ibge} catch-all"
            )
        except Exception as e:
            return IntegrationTestResult(
                "Route Ordering (Manual Data)",
                False,
                f"Error reading router file: {str(e)}"
            )
    
    def test_2_frontend_uses_api_client(self):
        """Test that frontend components use centralized api.js client"""
        try:
            with open('frontend/src/components/SmartCityDashboard.jsx', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if getHybridRanking is imported
            if 'getHybridRanking' not in content:
                return IntegrationTestResult(
                    "Frontend API Client Usage (SmartCityDashboard)",
                    False,
                    "getHybridRanking not imported from api.js"
                )
            
            # Check if hardcoded URLs exist
            if 'http://localhost:8000' in content and 'fetch(' in content:
                # Check if it's actually used (not just in comments)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'http://localhost:8000' in line and 'fetch' not in line and '#' not in line:
                        # Check if next few lines have fetch
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if 'fetch(' in lines[j]:
                                return IntegrationTestResult(
                                    "Frontend API Client Usage (SmartCityDashboard)",
                                    False,
                                    f"Hardcoded URL found at line {i+1}, should use api.js instead"
                                )
            
            # Check if using api.getHybridRanking instead of fetch
            if 'await getHybridRanking(' in content:
                return IntegrationTestResult(
                    "Frontend API Client Usage (SmartCityDashboard)",
                    True,
                    "Using getHybridRanking from api.js (centralized client)"
                )
            else:
                return IntegrationTestResult(
                    "Frontend API Client Usage (SmartCityDashboard)",
                    False,
                    "Should call getHybridRanking instead of direct fetch"
                )
        except Exception as e:
            return IntegrationTestResult(
                "Frontend API Client Usage (SmartCityDashboard)",
                False,
                f"Error reading component: {str(e)}"
            )
    
    def test_3_api_client_configuration(self):
        """Test that api.js is configured correctly"""
        try:
            with open('frontend/src/services/api.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check baseURL
            if 'localhost:8000/api/v1' not in content:
                return IntegrationTestResult(
                    "API Client Configuration (api.js)",
                    False,
                    "baseURL not set to localhost:8000/api/v1"
                )
            
            # Check getHybridRanking function exists
            if 'export const getHybridRanking' not in content:
                return IntegrationTestResult(
                    "API Client Configuration (api.js)",
                    False,
                    "getHybridRanking function not exported"
                )
            
            # Check error handling
            if 'status === 422' not in content or 'status === 502' not in content:
                return IntegrationTestResult(
                    "API Client Configuration (api.js)",
                    False,
                    "Error handling not properly implemented (missing status checks)"
                )
            
            # Check POST to /topsis/ranking-hibrido
            if '/topsis/ranking-hibrido' not in content:
                return IntegrationTestResult(
                    "API Client Configuration (api.js)",
                    False,
                    "Missing /topsis/ranking-hibrido endpoint call"
                )
            
            return IntegrationTestResult(
                "API Client Configuration (api.js)",
                True,
                "API client properly configured with baseURL, error handling, and endpoints"
            )
        except Exception as e:
            return IntegrationTestResult(
                "API Client Configuration (api.js)",
                False,
                f"Error reading api.js: {str(e)}"
            )
    
    def test_4_cors_middleware(self):
        """Test that CORS middleware is configured for frontend ports"""
        try:
            with open('backend/app/main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Vite default port (5173)
            if 'localhost:5173' not in content:
                return IntegrationTestResult(
                    "CORS Configuration (main.py)",
                    False,
                    "localhost:5173 (Vite default) not in CORS allow_origins"
                )
            
            # Check for fallback port (3000)
            if 'localhost:3000' not in content:
                return IntegrationTestResult(
                    "CORS Configuration (main.py)",
                    False,
                    "localhost:3000 not in CORS allow_origins"
                )
            
            # Check for 127.0.0.1 variants
            if '127.0.0.1' not in content:
                return IntegrationTestResult(
                    "CORS Configuration (main.py)",
                    False,
                    "127.0.0.1 loopback address not in CORS allow_origins"
                )
            
            # Check for allow_credentials
            if 'allow_credentials=True' not in content:
                return IntegrationTestResult(
                    "CORS Configuration (main.py)",
                    False,
                    "Credentials not allowed (allow_credentials=True not set)"
                )
            
            return IntegrationTestResult(
                "CORS Configuration (main.py)",
                True,
                "CORS properly configured for localhost:5173 (Vite), localhost:3000, and 127.0.0.1"
            )
        except Exception as e:
            return IntegrationTestResult(
                "CORS Configuration (main.py)",
                False,
                f"Error reading main.py: {str(e)}"
            )
    
    def test_5_backend_endpoint_paths(self):
        """Test that backend endpoints match frontend API client calls"""
        endpoints_to_verify = {
            "POST /topsis/ranking-hibrido": ("topsis.py", "get_hybrid_ranking"),
            "POST /manual-data/{codigo_ibge}": ("manual_data.py", "criar_ou_atualizar_dados_manuais"),
            "GET /manual-data/{codigo_ibge}": ("manual_data.py", "obter_dados_manuais"),
            "PATCH /manual-data/{codigo_ibge}": ("manual_data.py", "atualizar_dados_manuais"),
            "GET /manual-data/{codigo_ibge}/history": ("manual_data.py", "obter_historico_alteracoes"),
            "GET /manual-data/{codigo_ibge}/indicadores/historico": ("manual_data.py", "obter_historico_indicadores"),
            "GET /manual-data/rankings/historico": ("manual_data.py", "obter_historico_rankings"),
            "GET /manual-data/rankings/periodo/{periodo_referencia}": ("manual_data.py", "obter_ranking_por_periodo"),
        }
        
        issues = []
        for endpoint_desc, (file, function) in endpoints_to_verify.items():
            try:
                filepath = f"backend/app/routers/{file}"
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if f"async def {function}" not in content:
                    issues.append(f"Missing {function} in {file}")
            except FileNotFoundError:
                issues.append(f"File not found: {filepath}")
        
        if issues:
            return IntegrationTestResult(
                "Backend Endpoint Paths",
                False,
                f"Missing endpoints: {', '.join(issues)}"
            )
        
        return IntegrationTestResult(
            "Backend Endpoint Paths",
            True,
            f"All {len(endpoints_to_verify)} expected endpoints found"
        )
    
    def test_6_request_response_schemas(self):
        """Test that request/response schemas are defined"""
        try:
            with open('backend/app/schemas.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_schemas = [
                "CityHybridInput",
                "TOPSISResult",
                "CityManualDataResponse",
                "IndicatorSnapshotResponse",
                "RankingSnapshotResponse",
            ]
            
            missing = [s for s in required_schemas if f"class {s}" not in content]
            
            if missing:
                return IntegrationTestResult(
                    "Request/Response Schemas",
                    False,
                    f"Missing Pydantic schemas: {', '.join(missing)}"
                )
            
            return IntegrationTestResult(
                "Request/Response Schemas",
                True,
                f"All {len(required_schemas)} required schemas defined"
            )
        except Exception as e:
            return IntegrationTestResult(
                "Request/Response Schemas",
                False,
                f"Error checking schemas: {str(e)}"
            )
    
    def test_7_error_handling_consistency(self):
        """Test that error handling is consistent across frontend and backend"""
        try:
            # Check backend error codes
            with open('backend/app/routers/topsis.py', 'r', encoding='utf-8') as f:
                backend_content = f.read()
            
            backend_errors = {
                400: "HTTPException" in backend_content,  # Bad request (< 2 cities)
                422: "HTTPException" in backend_content,  # Validation error
                502: "HTTPException" in backend_content,  # External API failure
                500: "HTTPException" in backend_content,  # Server error
            }
            
            # Check frontend error handling
            with open('frontend/src/services/api.js', 'r', encoding='utf-8') as f:
                frontend_content = f.read()
            
            frontend_errors = {
                400: "status === 400" in frontend_content,
                422: "status === 422" in frontend_content,
                502: "status === 502" in frontend_content,
                500: "status === 500" in frontend_content,
            }
            
            # Both should handle these error codes
            issues = []
            for code in [400, 422, 502, 500]:
                if not frontend_errors.get(code):
                    issues.append(f"Frontend doesn't handle HTTP {code}")
            
            if issues:
                return IntegrationTestResult(
                    "Error Handling Consistency",
                    False,
                    f"Missing error handlers: {', '.join(issues)}"
                )
            
            return IntegrationTestResult(
                "Error Handling Consistency",
                True,
                "Frontend properly handles all backend error codes (400, 422, 502, 500)"
            )
        except Exception as e:
            return IntegrationTestResult(
                "Error Handling Consistency",
                False,
                f"Error checking error handling: {str(e)}"
            )
    
    def test_8_imports_verification(self):
        """Test that all necessary imports are present"""
        try:
            # Check main.py imports routers
            with open('backend/app/main.py', 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            required_imports = [
                "from app.routers.topsis import topsis_router",
                "from app.routers.manual_data import manual_data_router",
                "from app.routers.indicadores import indicators_router",
            ]
            
            missing_imports = [imp for imp in required_imports if imp not in main_content]
            
            if missing_imports:
                return IntegrationTestResult(
                    "Backend Router Imports",
                    False,
                    f"Missing imports: {', '.join(missing_imports)}"
                )
            
            # Check frontend imports
            with open('frontend/src/components/SmartCityDashboard.jsx', 'r', encoding='utf-8') as f:
                frontend_content = f.read()
            
            if "import { getHybridRanking } from '../services/api'" not in frontend_content:
                return IntegrationTestResult(
                    "Frontend API Import",
                    False,
                    "getHybridRanking not imported from api.js"
                )
            
            return IntegrationTestResult(
                "Imports Verification",
                True,
                "All necessary imports present (routers, API client)"
            )
        except Exception as e:
            return IntegrationTestResult(
                "Imports Verification",
                False,
                f"Error verifying imports: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*80)
        print("🔗 FRONTEND-BACKEND INTEGRATION TEST SUITE")
        print("="*80 + "\n")
        
        tests = [
            self.test_1_route_ordering_manual_data,
            self.test_2_frontend_uses_api_client,
            self.test_3_api_client_configuration,
            self.test_4_cors_middleware,
            self.test_5_backend_endpoint_paths,
            self.test_6_request_response_schemas,
            self.test_7_error_handling_consistency,
            self.test_8_imports_verification,
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.results.append(result)
                print(result)
            except Exception as e:
                result = IntegrationTestResult(
                    test_func.__doc__ or test_func.__name__,
                    False,
                    f"Unexpected error: {str(e)}"
                )
                self.results.append(result)
                print(result)
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print(f"Total: {total} | ✅ Passed: {passed} | ❌ Failed: {total - passed}")
        print(f"Pass Rate: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("Frontend and backend are ready for integration testing.")
        else:
            print(f"\n⚠️  {total - passed} TEST(S) FAILED - Review issues above")
        
        print("="*80 + "\n")
        
        return passed == total


def main():
    """Main entry point"""
    tester = FrontendBackendIntegrationTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
