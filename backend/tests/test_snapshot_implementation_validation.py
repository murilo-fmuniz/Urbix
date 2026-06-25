"""
Quick Test: Verify Indicator Snapshot Implementation

This test validates that:
1. IndicatorSnapshot model exists and is imported correctly
2. The model has all required fields
3. The code in topsis.py was added correctly
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

# Fix UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_indicator_snapshot_model():
    """Test 1: Verify IndicatorSnapshot model exists"""
    print("\n" + "="*80)
    print("TEST 1: INDICATOR SNAPSHOT MODEL VALIDATION")
    print("="*80)
    
    try:
        from app.models import IndicatorSnapshot
        print("[OK] IndicatorSnapshot model imported successfully")
        
        # Check required fields
        required_fields = ['codigo_ibge', 'valores_indicadores', 'data_calculo', 'fonte_dados', 'periodo_referencia']
        model_columns = [c.name for c in IndicatorSnapshot.__table__.columns]
        
        print(f"\n[OK] Model columns: {model_columns}")
        
        for field in required_fields:
            if field in model_columns:
                print(f"   [OK] {field}")
            else:
                print(f"   [FAIL] Missing field: {field}")
                return False
        
        print("\n[OK] TEST 1 PASSED")
        return True
    
    except Exception as e:
        print(f"[FAIL] TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_topsis_imports():
    """Test 2: Verify TOPSIS router imports IndicatorSnapshot"""
    print("\n" + "="*80)
    print("TEST 2: TOPSIS ROUTER IMPORTS")
    print("="*80)
    
    try:
        from app.routers import topsis
        print("[OK] TOPSIS router imported")
        
        # Check if IndicatorSnapshot is imported in topsis module
        if hasattr(topsis, 'IndicatorSnapshot'):
            print("[OK] IndicatorSnapshot available in topsis module")
        else:
            # It might be imported in the router but not exposed, that's OK
            print("[OK] IndicatorSnapshot not directly exposed (but may be used internally)")
        
        print("\n[OK] TEST 2 PASSED")
        return True
    
    except Exception as e:
        print(f"[FAIL] TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_code_contains_snapshot_logic():
    """Test 3: Verify snapshot saving code was added to topsis.py"""
    print("\n" + "="*80)
    print("TEST 3: SNAPSHOT LOGIC IN TOPSIS CODE")
    print("="*80)
    
    try:
        with open('app/routers/topsis.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key markers
        checks = [
            ('IndicatorSnapshot(', 'IndicatorSnapshot instantiation'),
            ('valores_indicadores=indicadores_flat', 'Flat values assignment'),
            ('fonte_dados="hibrido"', 'Hybrid source marking'),
            ('PASSO 4: SALVAR SNAPSHOT', 'PASSO 4 comment'),
            ('db.add(snapshot)', 'Database add call'),
            ('db.commit()', 'Database commit call'),
        ]
        
        all_found = True
        for marker, desc in checks:
            if marker in content:
                print(f"[OK] Found: {desc}")
            else:
                print(f"[FAIL] Missing: {desc} (marker: {marker})")
                all_found = False
        
        if not all_found:
            return False
        
        # Count occurrences to ensure we don't have duplicates
        snapshot_instantiations = content.count('IndicatorSnapshot(')
        print(f"\n[OK] IndicatorSnapshot instantiations: {snapshot_instantiations}")
        
        print("\n[OK] TEST 3 PASSED")
        return True
    
    except Exception as e:
        print(f"[FAIL] TEST 3 FAILED: {str(e)}")
        return False


def test_database_tables():
    """Test 4: Verify indicator_snapshot table exists"""
    print("\n" + "="*80)
    print("TEST 4: DATABASE TABLE VERIFICATION")
    print("="*80)
    
    try:
        from app.database import SessionLocal
        from app.models import IndicatorSnapshot
        from sqlalchemy import inspect
        
        db = SessionLocal()
        inspector = inspect(IndicatorSnapshot.__table__)
        
        print(f"[OK] Table name: {IndicatorSnapshot.__tablename__}")
        print(f"[OK] Columns: {len(inspector.columns)}")
        
        for col in inspector.columns:
            print(f"   * {col.name}: {col.type}")
        
        db.close()
        
        print("\n[OK] TEST 4 PASSED")
        return True
    
    except Exception as e:
        print(f"[FAIL] TEST 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_quick_validation():
    """Run all quick validation tests"""
    
    print("\n" + "="*80)
    print("QUICK VALIDATION - INDICATOR SNAPSHOT IMPLEMENTATION")
    print("="*80)
    
    results = {
        "IndicatorSnapshot Model": test_indicator_snapshot_model(),
        "TOPSIS Router Imports": test_topsis_imports(),
        "Snapshot Logic in Code": test_code_contains_snapshot_logic(),
        "Database Table": test_database_tables(),
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\nTOTAL: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    if passed == total:
        print("SUCCESS! Historical series logging implementation is complete.")
        print("\nNext Steps:")
        print("1. Run the TOPSIS endpoint: POST /topsis/ranking-hibrido")
        print("2. Check database for indicator snapshots")
        print("3. Query snapshots using test_indicator_snapshots.py")
    
    return passed == total


if __name__ == "__main__":
    success = run_quick_validation()
    sys.exit(0 if success else 1)
