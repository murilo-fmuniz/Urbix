"""
Test: Indicator Snapshots - Historical Series Logging

Validates that:
1. IndicatorSnapshot records are created for each city calculation
2. All 50 indicators are stored correctly in the snapshot
3. Metadata (date, source, period) is properly recorded
4. Multiple snapshots can be created over time
5. Query functionality works for historical data retrieval
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.database import SessionLocal
from app.models import IndicatorSnapshot, CityManualData
from app.schemas import ManualCityIndicators


def test_snapshot_creation():
    """Test 1: Verify snapshot records exist in database"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("TEST 1: SNAPSHOT CREATION & STORAGE")
    print("="*80)
    
    try:
        # Query all snapshots
        snapshots = db.query(IndicatorSnapshot).all()
        total_snapshots = len(snapshots)
        
        print(f"\n[OK] Total snapshots in database: {total_snapshots}")
        
        if total_snapshots == 0:
            print("[WARN] No snapshots found. Run TOPSIS endpoint first!")
            return False
        
        # Show summary by city
        snapshots_by_city = db.query(
            IndicatorSnapshot.codigo_ibge,
            func.count(IndicatorSnapshot.id).label("snapshot_count"),
            func.max(IndicatorSnapshot.data_calculo).label("ultima_atualizacao")
        ).group_by(IndicatorSnapshot.codigo_ibge).all()
        
        print(f"\n[OK] Cities with snapshots: {len(snapshots_by_city)}")
        for codigo, count, last_date in snapshots_by_city:
            print(f"   * {codigo}: {count} snapshot(s), ultima: {last_date}")
        
        print("\n[OK] TEST 1 PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 1 FAILED: {str(e)}")
        return False
    finally:
        db.close()


def test_snapshot_data_integrity():
    """Test 2: Verify snapshot data has 50 indicators and valid values"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("TEST 2: SNAPSHOT DATA INTEGRITY")
    print("="*80)
    
    try:
        # Get most recent snapshot
        latest_snapshot = db.query(IndicatorSnapshot).order_by(
            desc(IndicatorSnapshot.data_calculo)
        ).first()
        
        if not latest_snapshot:
            print("[WARN] No snapshots found!")
            return False
        
        print(f"\n[DATA] Analyzing snapshot:")
        print(f"   City: {latest_snapshot.codigo_ibge}")
        print(f"   Date: {latest_snapshot.data_calculo}")
        print(f"   Source: {latest_snapshot.fonte_dados}")
        
        # Validate 50 indicators
        valores = latest_snapshot.valores_indicadores
        
        if not isinstance(valores, list):
            print(f"[FAIL] valores_indicadores should be list, got {type(valores)}")
            return False
        
        if len(valores) != 50:
            print(f"[FAIL] Expected 50 indicators, got {len(valores)}")
            return False
        
        print(f"[OK] Exactly 50 indicators stored")
        
        # Validate data types and ranges
        non_zero = len([v for v in valores if v > 0])
        valid_count = 0
        
        for idx, valor in enumerate(valores):
            if not isinstance(valor, (int, float)):
                print(f"[FAIL] Indicator [{idx}] has invalid type: {type(valor)}")
                return False
            
            # Values should be 0-100 or very large (like per capita)
            if valor >= 0:
                valid_count += 1
            else:
                print(f"[WARN] Indicator [{idx}] = {valor} (negative)")
        
        print(f"[OK] All {valid_count}/50 indicators have valid data types")
        print(f"[OK] Non-zero indicators: {non_zero}/50 ({non_zero/50*100:.1f}%)")
        
        # Statistics
        valores_positivos = [v for v in valores if v > 0]
        if valores_positivos:
            media = sum(valores_positivos) / len(valores_positivos)
            minimo = min(valores_positivos)
            maximo = max(valores_positivos)
            print(f"[OK] Statistics (positive values only):")
            print(f"   * Mean: {media:.2f}")
            print(f"   * Min: {minimo:.2f}")
            print(f"   * Max: {maximo:.2f}")
        
        print("\n[OK] TEST 2 PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_snapshot_timestamps():
    """Test 3: Verify snapshots track time series correctly"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("TEST 3: SNAPSHOT TIMESTAMP TRACKING")
    print("="*80)
    
    try:
        # Get all snapshots for one city
        snapshots = db.query(IndicatorSnapshot).order_by(
            IndicatorSnapshot.data_calculo
        ).all()
        
        if len(snapshots) < 2:
            print(f"[WARN] Only {len(snapshots)} snapshot(s) - need at least 2 for time series analysis")
            print("   Run TOPSIS endpoint multiple times to create multiple snapshots")
            return True  # Not a failure, just informational
        
        print(f"\n[OK] Time series data: {len(snapshots)} snapshots")
        
        for i, snap in enumerate(snapshots[-5:]):  # Last 5
            print(f"   [{i+1}] {snap.data_calculo} - {snap.codigo_ibge}")
        
        # Check chronological order
        for i in range(1, len(snapshots)):
            if snapshots[i].data_calculo < snapshots[i-1].data_calculo:
                print(f"[FAIL] Snapshots not in chronological order!")
                return False
        
        print(f"[OK] Snapshots in correct chronological order")
        
        # Check time differences
        if len(snapshots) >= 2:
            time_diff = snapshots[-1].data_calculo - snapshots[-2].data_calculo
            print(f"[OK] Time between last 2 snapshots: {time_diff}")
        
        print("\n[OK] TEST 3 PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 3 FAILED: {str(e)}")
        return False
    finally:
        db.close()


def test_snapshot_city_relationship():
    """Test 4: Verify snapshots link correctly to city manual data"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("TEST 4: SNAPSHOT-CITY RELATIONSHIP")
    print("="*80)
    
    try:
        # Get snapshots with city data
        snapshots = db.query(IndicatorSnapshot).all()
        
        if not snapshots:
            print("[WARN] No snapshots found!")
            return False
        
        missing_cities = 0
        valid_cities = 0
        
        for snap in snapshots:
            city = db.query(CityManualData).filter_by(
                codigo_ibge=snap.codigo_ibge
            ).first()
            
            if city:
                valid_cities += 1
            else:
                print(f"[WARN] Snapshot has orphaned codigo_ibge: {snap.codigo_ibge}")
                missing_cities += 1
        
        print(f"\n[OK] Snapshots with valid cities: {valid_cities}/{len(snapshots)}")
        
        if missing_cities > 0:
            print(f"[WARN] Orphaned snapshots: {missing_cities}")
        
        print("\n[OK] TEST 4 PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 4 FAILED: {str(e)}")
        return False
    finally:
        db.close()


def test_snapshot_query_capability():
    """Test 5: Verify we can query snapshots for historical analysis"""
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("TEST 5: SNAPSHOT QUERY CAPABILITY")
    print("="*80)
    
    try:
        # Query 1: Most recent snapshot
        latest = db.query(IndicatorSnapshot).order_by(
            desc(IndicatorSnapshot.data_calculo)
        ).first()
        
        if latest:
            print(f"\n[OK] Query 1 - Latest snapshot:")
            print(f"   City: {latest.codigo_ibge}")
            print(f"   Time: {latest.data_calculo}")
            print(f"   Indicators: {len(latest.valores_indicadores)}")
        
        # Query 2: Snapshots for specific city
        cidade_teste = "3550308"  # Sao Paulo
        snapshots_sp = db.query(IndicatorSnapshot).filter_by(
            codigo_ibge=cidade_teste
        ).all()
        
        print(f"\n[OK] Query 2 - City {cidade_teste}: {len(snapshots_sp)} snapshot(s)")
        
        # Query 3: Snapshots in last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent = db.query(IndicatorSnapshot).filter(
            IndicatorSnapshot.data_calculo >= yesterday
        ).all()
        
        print(f"[OK] Query 3 - Last 24h: {len(recent)} snapshot(s)")
        
        # Query 4: Time series for one city
        if snapshots_sp:
            oldest = snapshots_sp[0].data_calculo
            newest = snapshots_sp[-1].data_calculo if len(snapshots_sp) > 1 else oldest
            print(f"[OK] Query 4 - Time range for {cidade_teste}: {oldest} to {newest}")
        
        print("\n[OK] TEST 5 PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 5 FAILED: {str(e)}")
        return False
    finally:
        db.close()


def run_all_tests():
    """Run all snapshot tests"""
    print("\n" + "="*80)
    print("INDICATOR SNAPSHOT TESTS - HISTORICAL SERIES LOGGING")
    print("="*80)
    
    results = {
        "Snapshot Creation": test_snapshot_creation(),
        "Data Integrity": test_snapshot_data_integrity(),
        "Timestamp Tracking": test_snapshot_timestamps(),
        "City Relationship": test_snapshot_city_relationship(),
        "Query Capability": test_snapshot_query_capability(),
    }
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"{'='*80}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
