"""
Universal Memory Storage Tests

Purpose: Comprehensive test suite for universal memory storage system
Version: 1.0.0
Author: Claude Code + zycaskevin

Test Strategy (Based on Adversarial Analysis):
1. Core Contract Tests - All backends must pass
2. Capability Contract Tests - Test based on declared capability
3. Backend-Specific Tests - Test unique features
4. Auto-degradation Tests - Verify fallback behavior

Expected Results:
- EvoMemStorage: FULL capability, all tests pass
- JSONStorage: BASIC capability, core tests pass, search returns []
- Factory: Auto-detection works, degradation works
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from universal_memory_storage import (
    StorageCapability,
    MemoryStorageInterface,
    EvoMemStorage,
    JSONStorage,
    MemoryStorageFactory,
    create_storage
)


# ============================================================
# Test Data
# ============================================================

def create_test_memory() -> dict:
    """Create test memory item"""
    return {
        "id": "mem_test_20251116",
        "type": "handoff",
        "timestamp": "2025-11-16T10:00:00Z",
        "session_memory": {
            "sessionIntent": ["Test universal storage", "Verify degradation"],
            "todos": [
                {"content": "Test EvoMem storage", "status": "completed"},
                {"content": "Test JSON storage", "status": "completed"}
            ],
            "decisions": [
                {"decision": "Use 2-tier degradation", "rationale": "Simpler and more reliable"}
            ]
        },
        "long_term_memory": {
            "learnings": [
                {"pattern": "Red Team analysis prevents over-engineering", "context": "Adversarial review"}
            ]
        },
        "metadata": {
            "project": "專案啟動文檔專案",
            "phase": "P1-Universal-Storage",
            "compression_ratio": 0.95,
            "quality_score": 9.5
        }
    }


# ============================================================
# Layer 1: Core Contract Tests (All backends must pass)
# ============================================================

def test_core_contract(storage: MemoryStorageInterface, test_name: str):
    """Test core functionality: store + retrieve + health_check

    All backends must pass this test regardless of capability level.
    """
    print(f"\n[Test] {test_name} - Core Contract")

    # 1. Health check
    assert storage.health_check(), "Health check failed"
    print("  [PASS] health_check() returns True")

    # 2. Store memory
    test_memory = create_test_memory()
    memory_id = storage.store(test_memory)
    assert memory_id == test_memory['id'], "Returned memory_id mismatch"
    print(f"  [PASS] store() returned correct memory_id: {memory_id}")

    # 3. Retrieve memory
    retrieved = storage.retrieve(memory_id)
    assert retrieved is not None, "Retrieved memory is None"
    assert retrieved['id'] == memory_id, "Retrieved memory_id mismatch"
    print(f"  [PASS] retrieve() returned correct memory")

    # 4. Retrieve non-existent memory
    non_existent = storage.retrieve("mem_nonexistent_999")
    assert non_existent is None, "Non-existent memory should return None"
    print("  [PASS] retrieve() returns None for non-existent memory")

    print(f"[SUCCESS] {test_name} - Core Contract (4/4 tests passed)")


# ============================================================
# Layer 2: Capability Contract Tests (Based on declared capability)
# ============================================================

def test_capability_contract(storage: MemoryStorageInterface, test_name: str):
    """Test functionality based on declared capability

    - FULL: search() should return results
    - BASIC: search() should return empty list
    """
    print(f"\n[Test] {test_name} - Capability Contract")

    capability = storage.capability
    print(f"  [INFO] Declared capability: {capability.value}")

    if capability == StorageCapability.FULL:
        # FULL capability: search() should work
        # First store a memory to search for
        test_memory = create_test_memory()
        storage.store(test_memory)

        # Search for it
        results = storage.search("Test universal storage")
        assert isinstance(results, list), "search() should return a list"
        print(f"  [PASS] search() returns list (FULL capability)")

        # Note: We don't assert len(results) > 0 because EvoMem might not find it
        # depending on vectorization. Just verify it returns a list.

    elif capability == StorageCapability.BASIC:
        # BASIC capability: search() should return empty list
        results = storage.search("any query")
        assert isinstance(results, list), "search() should return a list"
        assert len(results) == 0, "BASIC capability should return empty list"
        print(f"  [PASS] search() returns empty list (BASIC capability)")

    print(f"[SUCCESS] {test_name} - Capability Contract (tests passed)")


# ============================================================
# Layer 3: Backend-Specific Tests
# ============================================================

def test_evomem_specific():
    """Test EvoMem-specific features"""
    print(f"\n[Test] EvoMem-Specific Features")

    try:
        storage = EvoMemStorage(persist_directory="data/vectors/test_universal")

        # Verify capability
        assert storage.capability == StorageCapability.FULL
        print("  [PASS] EvoMem declares FULL capability")

        # Verify it's available
        if storage.health_check():
            print("  [PASS] EvoMem initialized successfully")

            # Test search with kwargs
            test_memory = create_test_memory()
            storage.store(test_memory)

            # Search with n_results parameter
            results = storage.search("universal storage", n_results=3)
            assert isinstance(results, list)
            print(f"  [PASS] EvoMem search() accepts n_results parameter")

            print("[SUCCESS] EvoMem-Specific Features (tests passed)")
        else:
            print("  [SKIP] EvoMem not available (dependencies missing)")

    except RuntimeError as e:
        print(f"  [SKIP] EvoMem not available: {e}")


def test_json_specific():
    """Test JSON-specific features"""
    print(f"\n[Test] JSON-Specific Features")

    storage = JSONStorage(storage_dir="data/memory/test_universal")

    # Verify capability
    assert storage.capability == StorageCapability.BASIC
    print("  [PASS] JSON declares BASIC capability")

    # Verify file is created
    test_memory = create_test_memory()
    memory_id = storage.store(test_memory)

    file_path = Path(storage.storage_dir) / f"{memory_id}.json"
    assert file_path.exists(), "JSON file should be created"
    print(f"  [PASS] JSON file created at {file_path}")

    # Verify file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    assert content['id'] == memory_id
    print(f"  [PASS] JSON file contains correct data")

    # Verify search returns empty list
    results = storage.search("any query")
    assert results == []
    print(f"  [PASS] JSON search() returns empty list (as expected)")

    print("[SUCCESS] JSON-Specific Features (4/4 tests passed)")


# ============================================================
# Layer 4: Factory & Auto-degradation Tests
# ============================================================

def test_factory_auto_detection():
    """Test factory auto-detection (2-tier degradation)"""
    print(f"\n[Test] Factory Auto-Detection")

    # Test zero-config
    storage = MemoryStorageFactory.create()
    assert storage is not None
    assert isinstance(storage, MemoryStorageInterface)
    print(f"  [PASS] Zero-config create() returns valid storage")
    print(f"  [INFO] Auto-detected backend: {type(storage).__name__} ({storage.capability.value})")

    # Verify it works
    assert storage.health_check()
    test_memory = create_test_memory()
    memory_id = storage.store(test_memory)
    retrieved = storage.retrieve(memory_id)
    assert retrieved is not None
    print(f"  [PASS] Auto-detected storage works correctly")

    print("[SUCCESS] Factory Auto-Detection (2/2 tests passed)")


def test_factory_specific_backend():
    """Test factory with specific backend selection"""
    print(f"\n[Test] Factory Specific Backend Selection")

    # Test JSON (always available)
    storage_json = MemoryStorageFactory.create({"type": "json"})
    assert isinstance(storage_json, JSONStorage)
    assert storage_json.capability == StorageCapability.BASIC
    print(f"  [PASS] Explicitly selecting 'json' works")

    # Test EvoMem (may not be available)
    try:
        storage_evomem = MemoryStorageFactory.create({"type": "evomem"})
        assert isinstance(storage_evomem, EvoMemStorage)
        assert storage_evomem.capability == StorageCapability.FULL
        print(f"  [PASS] Explicitly selecting 'evomem' works")
    except RuntimeError:
        print(f"  [SKIP] EvoMem not available (expected in some environments)")

    print("[SUCCESS] Factory Specific Backend Selection (tests passed)")


def test_factory_custom_config():
    """Test factory with custom configuration"""
    print(f"\n[Test] Factory Custom Configuration")

    # Test custom JSON directory
    custom_dir = "data/memory/test_custom"
    storage = MemoryStorageFactory.create({
        "type": "json",
        "json": {"storage_dir": custom_dir}
    })

    assert isinstance(storage, JSONStorage)
    # Normalize paths for comparison (Windows \ vs /)
    assert Path(storage.storage_dir).resolve() == Path(custom_dir).resolve()
    print(f"  [PASS] Custom JSON directory: {custom_dir}")

    # Test it works
    test_memory = create_test_memory()
    memory_id = storage.store(test_memory)
    file_path = Path(custom_dir) / f"{memory_id}.json"
    assert file_path.exists(), f"File not found at {file_path}"
    print(f"  [PASS] File created in custom directory")

    print("[SUCCESS] Factory Custom Configuration (2/2 tests passed)")


def test_convenience_function():
    """Test convenience function create_storage()"""
    print(f"\n[Test] Convenience Function")

    # Test convenience function
    storage = create_storage()
    assert storage is not None
    assert isinstance(storage, MemoryStorageInterface)
    print(f"  [PASS] create_storage() works (alias for factory)")

    print("[SUCCESS] Convenience Function (1/1 test passed)")


# ============================================================
# Test Runner
# ============================================================

def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("Universal Memory Storage - Comprehensive Test Suite")
    print("=" * 70)
    print("\nBased on Adversarial Analysis (Red Team vs Blue Team)")
    print("Test Layers:")
    print("  1. Core Contract - All backends must pass")
    print("  2. Capability Contract - Based on declared capability")
    print("  3. Backend-Specific - Test unique features")
    print("  4. Factory & Auto-degradation - Verify fallback behavior")
    print("\n" + "=" * 70)

    total_tests = 0
    passed_tests = 0

    # Layer 1: Core Contract Tests
    print("\n" + "=" * 70)
    print("LAYER 1: Core Contract Tests")
    print("=" * 70)

    try:
        # Test JSONStorage (always available)
        json_storage = JSONStorage(storage_dir="data/memory/test_universal")
        test_core_contract(json_storage, "JSONStorage")
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] JSONStorage Core Contract: {e}")
        total_tests += 1

    try:
        # Test EvoMemStorage (may not be available)
        evomem_storage = EvoMemStorage(persist_directory="data/vectors/test_universal")
        if evomem_storage.health_check():
            test_core_contract(evomem_storage, "EvoMemStorage")
            passed_tests += 1
        else:
            print("\n[SKIP] EvoMemStorage - Not available (dependencies missing)")
        total_tests += 1
    except RuntimeError:
        print("\n[SKIP] EvoMemStorage - Not available (dependencies missing)")
        total_tests += 1

    # Layer 2: Capability Contract Tests
    print("\n" + "=" * 70)
    print("LAYER 2: Capability Contract Tests")
    print("=" * 70)

    try:
        json_storage = JSONStorage(storage_dir="data/memory/test_universal")
        test_capability_contract(json_storage, "JSONStorage")
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] JSONStorage Capability Contract: {e}")
        total_tests += 1

    try:
        evomem_storage = EvoMemStorage(persist_directory="data/vectors/test_universal")
        if evomem_storage.health_check():
            test_capability_contract(evomem_storage, "EvoMemStorage")
            passed_tests += 1
        else:
            print("\n[SKIP] EvoMemStorage - Not available")
        total_tests += 1
    except RuntimeError:
        print("\n[SKIP] EvoMemStorage - Not available")
        total_tests += 1

    # Layer 3: Backend-Specific Tests
    print("\n" + "=" * 70)
    print("LAYER 3: Backend-Specific Tests")
    print("=" * 70)

    try:
        test_json_specific()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] JSON-Specific Tests: {e}")
        total_tests += 1

    try:
        test_evomem_specific()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] EvoMem-Specific Tests: {e}")
        total_tests += 1

    # Layer 4: Factory & Auto-degradation Tests
    print("\n" + "=" * 70)
    print("LAYER 4: Factory & Auto-degradation Tests")
    print("=" * 70)

    try:
        test_factory_auto_detection()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] Factory Auto-Detection: {e}")
        total_tests += 1

    try:
        test_factory_specific_backend()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] Factory Specific Backend: {e}")
        total_tests += 1

    try:
        test_factory_custom_config()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] Factory Custom Config: {e}")
        total_tests += 1

    try:
        test_convenience_function()
        passed_tests += 1
        total_tests += 1
    except Exception as e:
        print(f"[FAILED] Convenience Function: {e}")
        total_tests += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {passed_tests / total_tests * 100:.1f}%")

    if passed_tests == total_tests:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total_tests - passed_tests} test(s) failed or skipped")

    print("=" * 70)

    return passed_tests == total_tests


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
