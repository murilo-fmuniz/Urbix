"""
Integration Test: Historical Series Logging via TOPSIS Endpoint

This test:
1. Calls the /ranking-hibrido endpoint to generate indicator calculations
2. Verifies that IndicatorSnapshot records are created
3. Validates all 50 indicators are stored
4. Checks the historical series is properly logged
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
import json
from datetime import datetime
from sqlalchemy import func, desc

# FastAPI test imports
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import IndicatorSnapshot, CityManualData
from app.schemas import ManualCityIndicators


def test_topsis_creates_snapshots():
    """Integration Test: Verify TOPSIS endpoint creates indicator snapshots"""
    
    print("\n" + "="*100)
    print("INTEGRATION TEST: TOPSIS -> HISTORICAL SERIES LOGGING")
    print("="*100)
    
    db = SessionLocal()
    client = TestClient(app)
    
    try:
        # Get count of snapshots BEFORE
        snapshots_before = db.query(IndicatorSnapshot).count()
        print(f"\n[DATA] Snapshots BEFORE: {snapshots_before}")
        
        # Create test payload with 3 cities
        payload = [
            {
                "codigo_ibge": "4101408",
                "nome_cidade": "Apucarana",
                "manual_indicators": ManualCityIndicators().model_dump()
            },
            {
                "codigo_ibge": "3550308",
                "nome_cidade": "São Paulo",
                "manual_indicators": ManualCityIndicators().model_dump()
            },
            {
                "codigo_ibge": "4106902",
                "nome_cidade": "Londrina",
                "manual_indicators": ManualCityIndicators().model_dump()
            }
        ]
        
        print(f"\n[TEST] Calling /ranking-hibrido with {len(payload)} cities...")
        
        # Call TOPSIS endpoint
        response = client.post(
            "/topsis/ranking-hibrido",
            json=payload,
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   [FAIL] Error response: {response.text}")
            return False
        
        result = response.json()
        print(f"   [OK] Ranking calculated with {len(result.get('ranking', []))} cities")
        
        # Get count of snapshots AFTER
        snapshots_after = db.query(IndicatorSnapshot).count()
        new_snapshots = snapshots_after - snapshots_before
        
        print(f"\n[DATA] Snapshots AFTER: {snapshots_after}")
        print(f"[OK] NEW snapshots created: {new_snapshots}")
        
        if new_snapshots == 0:
            print("[WARN] No new snapshots created!")
            return False
        
        # Verify each snapshot
        print(f"\n[TEST] Verifying {new_snapshots} snapshot(s)...")
        
        latest_snapshots = db.query(IndicatorSnapshot).order_by(
            desc(IndicatorSnapshot.id)
        ).limit(new_snapshots).all()
        
        all_valid = True
        
        for idx, snap in enumerate(latest_snapshots, 1):
            print(f"\n   Snapshot {idx}:")
            print(f"   * City: {snap.codigo_ibge}")
            print(f"   * Indicators: {len(snap.valores_indicadores)}")
            print(f"   * Created: {snap.data_calculo}")
            print(f"   * Source: {snap.fonte_dados}")
            
            # Validate
            if len(snap.valores_indicadores) != 50:
                print(f"   [FAIL] Expected 50 indicators, got {len(snap.valores_indicadores)}")
                all_valid = False
            else:
                print(f"   [OK] Exactly 50 indicators")
            
            non_zero = len([v for v in snap.valores_indicadores if v > 0])
            print(f"   [OK] Non-zero indicators: {non_zero}/50")
        
        if not all_valid:
            return False
        
        print(f"\n{'='*100}")
        print("[OK] INTEGRATION TEST PASSED - Historical series logging is working!")
        print(f"{'='*100}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] INTEGRATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_snapshot_time_series():
    """Test: Verify historical time series can be queried"""
    
    print("\n" + "="*100)
    print("TIME SERIES QUERY TEST")
    print("="*100)
    
    db = SessionLocal()
    
    try:
        # Find a city with multiple snapshots
        city_snapshot_counts = db.query(
            IndicatorSnapshot.codigo_ibge,
            func.count(IndicatorSnapshot.id).label("count")
        ).group_by(IndicatorSnapshot.codigo_ibge).all()
        
        if not city_snapshot_counts:
            print("⚠️  No snapshots found")
            return False
        
        # Get city with most snapshots
        city_with_history = max(city_snapshot_counts, key=lambda x: x[1])
        codigo_ibge = city_with_history[0]
        count = city_with_history[1]
        
        print(f"\n[DATA] City {codigo_ibge} has {count} snapshot(s)")
        
        # Query time series
        snapshots = db.query(IndicatorSnapshot).filter_by(
            codigo_ibge=codigo_ibge
        ).order_by(IndicatorSnapshot.data_calculo).all()
        
        print(f"[OK] Retrieved {len(snapshots)} snapshot(s)")
        
        if len(snapshots) >= 2:
            # Show evolution of first 5 indicators
            print(f"\n[DATA] Evolution of first 3 indicators over time:")
            
            for snap in snapshots:
                valores = snap.valores_indicadores
                print(f"   {snap.data_calculo}: [{valores[0]:.2f}, {valores[1]:.2f}, {valores[2]:.2f}]")
        
        print(f"\n[OK] TIME SERIES QUERY TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ TIME SERIES QUERY TEST FAILED: {str(e)}")
        return False
    finally:
        db.close()


def run_integration_tests():
    """Run all integration tests"""
    
    print("\n" + "="*100)
    print("RUNNING INTEGRATION TESTS FOR HISTORICAL SERIES LOGGING")
    print("="*100)
    
    results = {
        "TOPSIS -> Snapshots": test_topsis_creates_snapshots(),
        "Time Series Query": test_snapshot_time_series(),
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\n" + "="*100)
    print("INTEGRATION TEST SUMMARY")
    print("="*100)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\nTOTAL: {passed}/{total} tests passed")
    print("="*100 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
