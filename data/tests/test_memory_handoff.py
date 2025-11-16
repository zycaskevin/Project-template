"""
Test Memory Handoff Integration

Purpose: 驗證小憶記憶交接功能的核心組件
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add project-template to path
sys.path.insert(0, str(Path(__file__).parent / 'project-template' / 'integrations'))

from memory_handoff_integration import (
    MemoryHandoffTrigger,
    InformationExtractor,
    ContextEnhancer,
    MemoryStorage,
    HandoffDocumenter,
    MemoryHandoffOrchestrator
)


def test_trigger_detection():
    """測試觸發條件偵測"""
    print("\n" + "=" * 60)
    print("Test 1: Trigger Detection")
    print("=" * 60)

    trigger = MemoryHandoffTrigger()

    # Case 1: Token 超過 70%
    should_trigger, reasons = trigger.should_trigger_handoff({
        'current_tokens': 145000,
        'max_tokens': 200000,
        'todos': []
    })

    print(f"\nCase 1: Token 72.5% (145K/200K)")
    print(f"  Should trigger: {should_trigger}")
    print(f"  Reasons: {reasons}")
    assert should_trigger == True, "Should trigger when token > 70%"
    assert 'token_usage' in str(reasons), "Should include token_usage reason"
    print("  [PASS] Token trigger detection")

    # Case 2: TODO 完成 5 個
    should_trigger, reasons = trigger.should_trigger_handoff({
        'current_tokens': 50000,
        'max_tokens': 200000,
        'todos': [
            {"status": "completed", "task": "Task 1"},
            {"status": "completed", "task": "Task 2"},
            {"status": "completed", "task": "Task 3"},
            {"status": "completed", "task": "Task 4"},
            {"status": "completed", "task": "Task 5"},
        ]
    })

    print(f"\nCase 2: 5 TODOs completed")
    print(f"  Should trigger: {should_trigger}")
    print(f"  Reasons: {reasons}")
    assert should_trigger == True, "Should trigger when 5+ TODOs completed"
    assert 'todo_completed' in str(reasons), "Should include todo_completed reason"
    print("  [PASS] TODO trigger detection")

    # Case 3: Phase 完成
    should_trigger, reasons = trigger.should_trigger_handoff({
        'current_tokens': 50000,
        'max_tokens': 200000,
        'todos': [],
        'phase_completed': True
    })

    print(f"\nCase 3: Phase completed")
    print(f"  Should trigger: {should_trigger}")
    print(f"  Reasons: {reasons}")
    assert should_trigger == True, "Should trigger when phase completed"
    assert 'phase_completed' in str(reasons), "Should include phase_completed reason"
    print("  [PASS] Phase trigger detection")

    print("\n[SUCCESS] All trigger detection tests passed!")


def test_information_extraction():
    """測試資訊提取"""
    print("\n" + "=" * 60)
    print("Test 2: Information Extraction")
    print("=" * 60)

    extractor = InformationExtractor()

    test_conversation = """
User: Implement P1-4.2 features
Assistant: Starting implementation...
Created: context7_integration.py
Implemented: sort_libraries_by_priority function
Implemented: extract_version_from_breadcrumbs function

Decision: Use 5-tier priority system
Rationale: Balance importance and flexibility

Fixed: Version detection regex
Optimized: Token allocation by priority
"""

    test_todos = [
        {"status": "completed", "task": "Task 1"},
        {"status": "pending", "task": "Task 2"}
    ]

    extracted = extractor.extract(test_conversation, test_todos)

    print(f"\nExtracted Information:")
    print(f"  Session Intent: {len(extracted.get('sessionIntent', []))} items")
    print(f"  Play by Play: {len(extracted.get('playByPlay', []))} actions")
    print(f"  TODOs: {len(extracted.get('todos', []))} items")
    print(f"  Decisions: {len(extracted.get('decisions', []))} decisions")
    print(f"  Learnings: {len(extracted.get('learnings', []))} learnings")
    print(f"  Code Patterns: {len(extracted.get('code_patterns', []))} patterns")

    # Verify extraction
    assert len(extracted.get('playByPlay', [])) > 0, "Should extract play-by-play"
    assert len(extracted.get('todos', [])) == 2, "Should preserve TODOs"
    assert len(extracted.get('decisions', [])) > 0, "Should extract decisions"

    print("\n[SUCCESS] Information extraction tests passed!")


def test_storage():
    """測試記憶存儲"""
    print("\n" + "=" * 60)
    print("Test 3: Memory Storage")
    print("=" * 60)

    storage = MemoryStorage(storage_dir="data/memory_test")

    test_memory_item = {
        "type": "handoff",
        "session_memory": {
            "sessionIntent": ["Test intent"],
            "playByPlay": ["Test action"]
        },
        "metadata": {
            "project": "Test Project",
            "phase": "Test Phase"
        }
    }

    # Store
    memory_id = storage.store(test_memory_item)
    print(f"\nStored memory: {memory_id}")
    assert memory_id is not None, "Should return memory ID"
    assert memory_id.startswith("mem_"), "Memory ID should start with 'mem_'"

    # Retrieve
    retrieved = storage.retrieve(memory_id)
    print(f"Retrieved memory: {retrieved.get('id', 'Unknown')}")
    assert retrieved is not None, "Should retrieve memory"
    assert retrieved.get('id') == memory_id, "Retrieved ID should match"

    print("\n[SUCCESS] Storage tests passed!")


def test_documentation():
    """測試文檔生成"""
    print("\n" + "=" * 60)
    print("Test 4: Documentation Generation")
    print("=" * 60)

    documenter = HandoffDocumenter()

    test_memory_item = {
        "id": "test_mem_001",
        "timestamp": "2025-11-16T00:00:00Z",
        "session_memory": {
            "sessionIntent": ["Test intent"],
            "playByPlay": ["Test action"],
            "artifacts": ["test.py"],
            "todos": [
                {"status": "completed", "task": "Task 1"},
                {"status": "pending", "task": "Task 2"}
            ],
            "decisions": [{
                "decision": "Test decision",
                "rationale": "Test rationale",
                "source": "test"
            }]
        },
        "long_term_memory": {
            "learnings": [{
                "pattern": "Test pattern",
                "type": "solution",
                "context": "Test context"
            }]
        },
        "metadata": {
            "project": "Test Project",
            "phase": "Test Phase",
            "token_before": 100000,
            "token_after": 5000,
            "compression_ratio": 0.95,
            "quality_score": 9.0
        }
    }

    # Generate handoff doc
    handoff_filename = documenter.generate_handoff(
        test_memory_item,
        output_dir="."
    )
    print(f"\nHandoff doc: {handoff_filename}")
    assert handoff_filename.endswith(".md"), "Should generate .md file"

    # Generate TODO next
    todo_filename = documenter.generate_todo_next(
        test_memory_item,
        output_dir="."
    )
    print(f"TODO doc: {todo_filename}")
    assert todo_filename == "TODO_NEXT.md", "Should generate TODO_NEXT.md"

    print("\n[SUCCESS] Documentation tests passed!")


def run_all_tests():
    """執行所有測試"""
    print("\n" + "=" * 60)
    print("Memory Handoff Integration - Test Suite")
    print("=" * 60)

    try:
        test_trigger_detection()
        test_information_extraction()
        test_storage()
        test_documentation()

        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed! (4/4)")
        print("=" * 60)
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
