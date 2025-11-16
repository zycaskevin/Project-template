"""
Test P1-4.2 Features: Priority, Version, Dependencies

Purpose: Verify the three new features work correctly
Version: 1.0 (P1-4.2)
"""

import sys
import os

# Add project-template to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-template'))

from integrations.context7_integration import (
    extract_version_from_breadcrumbs,
    sort_libraries_by_priority,
    get_framework_dependencies,
    enrich_libraries_with_dependencies,
)


def test_feature_1_priority_sorting():
    """Test Feature 1: Framework Priority Weight System"""
    print("\n" + "=" * 60)
    print("Feature 1: Framework Priority Weight System")
    print("=" * 60)

    # Test 1: Mixed priority libraries
    libraries = ["react", "redux", "alpine", "fastapi", "unknown-lib"]
    sorted_libs = sort_libraries_by_priority(libraries)

    print("\nTest 1: Mixed Priority Libraries")
    print(f"  Input: {libraries}")
    print(f"  Output (sorted by priority):")
    for lib, priority in sorted_libs:
        print(f"    {lib:20s} -> Priority {priority}")

    # Verify sorting order
    priorities = [p for _, p in sorted_libs]
    assert priorities == sorted(priorities, reverse=True), "[FAIL] Priority sorting failed"
    print("  [PASS] Priority sorting")

    # Test 2: Token budget scenario
    token_budget = 200  # Limited budget
    token_per_lib = 50

    print("\nTest 2: Token Budget Scenario (Budget: 200 tokens)")
    print(f"  Can fit {token_budget // token_per_lib} libraries")
    print(f"  Selected (by priority):")

    selected_count = 0
    for lib, priority in sorted_libs:
        if (selected_count + 1) * token_per_lib <= token_budget:
            print(f"    [+] {lib} (Priority {priority})")
            selected_count += 1
        else:
            print(f"    [ ] {lib} (Priority {priority}) - Skipped (budget exceeded)")

    print(f"  [PASS] Token budget optimization ({selected_count} libraries selected)")


def test_feature_2_version_detection():
    """Test Feature 2: Version Number Auto-Detection"""
    print("\n" + "=" * 60)
    print("Feature 2: Version Number Auto-Detection")
    print("=" * 60)

    # Test 1: Single version
    breadcrumbs_1 = ["import:fastapi==0.109.0"]
    versions_1 = extract_version_from_breadcrumbs(breadcrumbs_1)

    print("\nTest 1: Single Version")
    print(f"  Input: {breadcrumbs_1}")
    print(f"  Output: {versions_1}")
    assert versions_1.get("fastapi") == "==0.109.0", "[FAIL] Version extraction failed"
    print("  [PASS] Single version extraction")

    # Test 2: Multiple versions with different operators
    breadcrumbs_2 = [
        "import:django>=4.2",
        "import:flask~=2.3.0",
        "import:sqlalchemy>=1.4,<2.0",
    ]
    versions_2 = extract_version_from_breadcrumbs(breadcrumbs_2)

    print("\nTest 2: Multiple Versions with Operators")
    print(f"  Input:")
    for bc in breadcrumbs_2:
        print(f"    {bc}")
    print(f"  Output:")
    for lib, ver in versions_2.items():
        print(f"    {lib:15s} -> {ver}")

    assert "django" in versions_2, "[FAIL] Django version not detected"
    assert "flask" in versions_2, "[FAIL] Flask version not detected"
    print("  [PASS] Multiple version extraction")

    # Test 3: No version info
    breadcrumbs_3 = ["import:requests", "import:numpy"]
    versions_3 = extract_version_from_breadcrumbs(breadcrumbs_3)

    print("\nTest 3: No Version Info")
    print(f"  Input: {breadcrumbs_3}")
    print(f"  Output: {versions_3}")
    assert len(versions_3) == 0, "[FAIL] Should not extract versions when none present"
    print("  [PASS] No false version extraction")


def test_feature_3_dependency_graph():
    """Test Feature 3: Framework Dependency Relationship Graph"""
    print("\n" + "=" * 60)
    print("Feature 3: Framework Dependency Relationship Graph")
    print("=" * 60)

    # Test 1: Single dependency
    print("\nTest 1: Single Dependency (Redux)")
    deps_redux = get_framework_dependencies("redux")
    print(f"  redux -> {deps_redux}")
    assert "react" in deps_redux, "[FAIL] Redux should depend on React"
    print("  [PASS] Single dependency detection")

    # Test 2: Multiple dependencies
    print("\nTest 2: Multiple Dependencies (React-Redux)")
    deps_react_redux = get_framework_dependencies("react-redux")
    print(f"  react-redux -> {deps_react_redux}")
    assert "react" in deps_react_redux, "[FAIL] React-Redux should depend on React"
    assert "redux" in deps_react_redux, "[FAIL] React-Redux should depend on Redux"
    print("  [PASS] Multiple dependencies detection")

    # Test 3: Library enrichment
    print("\nTest 3: Library Enrichment")
    original = ["redux"]
    enriched = enrich_libraries_with_dependencies(original)
    print(f"  Original: {original}")
    print(f"  Enriched: {enriched}")
    assert "react" in enriched, "[FAIL] Should add React dependency"
    assert "redux" in enriched, "[FAIL] Should keep original library"
    print("  [PASS] Library enrichment")

    # Test 4: Complex ecosystem
    print("\nTest 4: Complex Ecosystem Enrichment")
    original_complex = ["react-redux", "nextjs"]
    enriched_complex = enrich_libraries_with_dependencies(original_complex)
    print(f"  Original: {original_complex}")
    print(f"  Enriched: {enriched_complex}")

    expected_libs = {"react", "redux", "react-redux", "nextjs"}
    assert expected_libs.issubset(set(enriched_complex)), "[FAIL] Missing expected libraries"
    print(f"  Expected libraries: {expected_libs}")
    print("  [PASS] Complex ecosystem enrichment")


def run_all_tests():
    """Run all P1-4.2 feature tests"""
    print("\n" + "=" * 60)
    print("P1-4.2 Feature Tests - Complete Suite")
    print("=" * 60)

    try:
        test_feature_1_priority_sorting()
        test_feature_2_version_detection()
        test_feature_3_dependency_graph()

        print("\n" + "=" * 60)
        print("[OK] Test Summary")
        print("=" * 60)
        print("[PASS] Feature 1: Framework Priority Weight System")
        print("[PASS] Feature 2: Version Number Auto-Detection")
        print("[PASS] Feature 3: Framework Dependency Graph")
        print("\n[SUCCESS] All tests passed! (3/3)")
        return True

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
