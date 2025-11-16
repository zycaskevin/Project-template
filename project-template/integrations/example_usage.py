"""
通用記憶存儲系統 - 實用範例代碼

本檔案包含各種常見使用場景的範例代碼。

範例列表:
1. 基礎使用 - 零配置快速開始
2. 完整記憶交接流程
3. 語義搜尋（EvoMem）
4. 條件性功能使用
5. 批次處理
6. 環境感知配置
7. 健康監控
8. 備份與恢復

執行方式:
    python example_usage.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict

# Add integrations to path
sys.path.insert(0, str(Path(__file__).parent))

from universal_memory_storage import (
    create_storage,
    MemoryStorageFactory,
    StorageCapability,
    EvoMemStorage,
    JSONStorage
)


# ============================================================
# 範例 1: 基礎使用 - 零配置快速開始
# ============================================================

def example_1_basic_usage():
    """範例 1: 最簡單的使用方式"""
    print("\n" + "=" * 70)
    print("範例 1: 基礎使用 - 零配置快速開始")
    print("=" * 70)

    # 零配置 - 自動檢測最佳後端
    storage = create_storage()

    # 創建測試記憶
    memory_item = {
        "id": "mem_example1_001",
        "type": "handoff",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": "這是一個測試記憶",
        "metadata": {
            "project": "範例專案",
            "tags": ["test", "example"]
        }
    }

    # 存儲
    memory_id = storage.store(memory_item)
    print(f"✅ 已存儲記憶: {memory_id}")

    # 檢索
    retrieved = storage.retrieve(memory_id)
    if retrieved:
        print(f"✅ 檢索成功: {retrieved['id']}")
        print(f"   內容: {retrieved['content']}")
    else:
        print("❌ 檢索失敗")

    # 檢查能力
    print(f"\n後端資訊:")
    print(f"  類型: {type(storage).__name__}")
    print(f"  能力: {storage.capability.value}")


# ============================================================
# 範例 2: 完整記憶交接流程
# ============================================================

def example_2_full_handoff():
    """範例 2: 使用記憶交接系統"""
    print("\n" + "=" * 70)
    print("範例 2: 完整記憶交接流程")
    print("=" * 70)

    try:
        from memory_handoff_integration import MemoryHandoffOrchestrator

        # 創建 Orchestrator
        orchestrator = MemoryHandoffOrchestrator()

        # 模擬對話內容
        conversation = """
        使用者: 請實作通用記憶存儲系統
        助手: 好的，我將設計一個支援多種後端的通用存儲架構
        使用者: 確保有降級機制
        助手: 已實作 EvoMem → JSON 降級
        """

        # 模擬 TODOs
        todos = [
            {"content": "設計架構", "status": "completed"},
            {"content": "實作代碼", "status": "completed"},
            {"content": "撰寫測試", "status": "completed"}
        ]

        # 執行記憶交接
        result = orchestrator.execute_handoff(
            conversation=conversation,
            current_tokens=145000,
            max_tokens=200000,
            todos=todos,
            metadata={
                "project": "範例專案",
                "phase": "P1-Example",
                "phase_completed": True
            }
        )

        # 檢查結果
        if result['success']:
            print(f"\n✅ 記憶交接成功!")
            print(f"   記憶 ID: {result['memory_id']}")
            print(f"   壓縮率: {result['compression_ratio']:.1%}")
            print(f"   交接文檔: {result['handoff_doc']}")
            print(f"   TODO 文檔: {result['todo_next']}")
        else:
            print(f"❌ 記憶交接失敗: {result.get('reason')}")

    except ImportError as e:
        print(f"⚠️ 無法執行範例 2: {e}")
        print("   請確保 memory_handoff_integration.py 可用")


# ============================================================
# 範例 3: 語義搜尋（EvoMem）
# ============================================================

def example_3_semantic_search():
    """範例 3: 使用語義搜尋功能（需要 EvoMem）"""
    print("\n" + "=" * 70)
    print("範例 3: 語義搜尋（EvoMem）")
    print("=" * 70)

    # 嘗試使用 EvoMem
    storage = create_storage({"type": "auto"})

    if storage.capability == StorageCapability.FULL:
        print("✅ 使用 EvoMem 後端，支援語義搜尋")

        # 先存儲一些測試記憶
        test_memories = [
            {
                "id": "mem_perf_001",
                "content": "使用 Redis 快取提升效能 50%",
                "metadata": {"tags": ["performance", "caching"]}
            },
            {
                "id": "mem_perf_002",
                "content": "PostgreSQL 索引優化查詢速度",
                "metadata": {"tags": ["performance", "database"]}
            },
            {
                "id": "mem_arch_001",
                "content": "微服務架構設計模式",
                "metadata": {"tags": ["architecture", "microservices"]}
            }
        ]

        for memory in test_memories:
            storage.store(memory)
            print(f"  已存儲: {memory['id']}")

        # 語義搜尋
        print("\n搜尋: '效能優化'")
        results = storage.search("效能優化", n_results=3)

        if results:
            print(f"找到 {len(results)} 個相關記憶:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('metadata', {}).get('memory_id', 'N/A')}")
        else:
            print("  未找到相關記憶")

    else:
        print("⚠️ 當前使用 JSON 後端，不支援語義搜尋")
        print("   安裝 EvoMem 以啟用此功能: pip install -e EvoMem/")


# ============================================================
# 範例 4: 條件性功能使用
# ============================================================

def example_4_conditional_features():
    """範例 4: 根據後端能力條件性使用功能"""
    print("\n" + "=" * 70)
    print("範例 4: 條件性功能使用")
    print("=" * 70)

    def smart_search(query: str) -> List[Dict]:
        """智能搜尋：自動適配後端能力"""
        storage = create_storage()

        if storage.capability == StorageCapability.FULL:
            # 使用語義搜尋
            print(f"🔍 使用語義搜尋: {query}")
            return storage.search(query, n_results=5)
        else:
            # 降級方案：返回空結果並提示
            print(f"⚠️ 語義搜尋不可用")
            print(f"   降級方案：返回空結果")
            return []

    # 測試智能搜尋
    results = smart_search("效能優化")
    print(f"搜尋結果: {len(results)} 個")


# ============================================================
# 範例 5: 批次處理
# ============================================================

def example_5_batch_processing():
    """範例 5: 批次存儲與檢索"""
    print("\n" + "=" * 70)
    print("範例 5: 批次處理")
    print("=" * 70)

    storage = create_storage()

    # 批次存儲
    memories_to_store = [
        {
            "id": f"mem_batch_{i:03d}",
            "content": f"批次記憶 {i}",
            "metadata": {"batch": "example5"}
        }
        for i in range(1, 6)
    ]

    print("批次存儲:")
    stored_ids = []
    for memory in memories_to_store:
        memory_id = storage.store(memory)
        stored_ids.append(memory_id)
        print(f"  ✅ {memory_id}")

    # 批次檢索
    print("\n批次檢索:")
    for memory_id in stored_ids:
        retrieved = storage.retrieve(memory_id)
        if retrieved:
            print(f"  ✅ {memory_id}: {retrieved['content']}")
        else:
            print(f"  ❌ {memory_id}: 檢索失敗")


# ============================================================
# 範例 6: 環境感知配置
# ============================================================

def example_6_environment_aware():
    """範例 6: 根據環境自動選擇存儲後端"""
    print("\n" + "=" * 70)
    print("範例 6: 環境感知配置")
    print("=" * 70)

    import os

    def create_env_aware_storage():
        """根據環境變數選擇後端"""
        env = os.getenv("ENVIRONMENT", "development")

        configs = {
            "production": {
                "type": "evomem",
                "evomem": {"persist_directory": "data/vectors/prod_memory"}
            },
            "staging": {
                "type": "evomem",
                "evomem": {"persist_directory": "data/vectors/staging_memory"}
            },
            "development": {
                "type": "json",
                "json": {"storage_dir": "data/memory/dev"}
            },
            "testing": {
                "type": "json",
                "json": {"storage_dir": "/tmp/test_memory"}
            }
        }

        config = configs.get(env, configs["development"])
        print(f"環境: {env}")
        print(f"配置: {config}")

        return create_storage(config)

    # 測試
    storage = create_env_aware_storage()
    print(f"後端: {type(storage).__name__} ({storage.capability.value})")


# ============================================================
# 範例 7: 健康監控
# ============================================================

def example_7_health_monitoring():
    """範例 7: 存儲健康檢查與監控"""
    print("\n" + "=" * 70)
    print("範例 7: 健康監控")
    print("=" * 70)

    def check_storage_health() -> bool:
        """檢查存儲健康狀態"""
        storage = create_storage()

        print(f"檢查存儲後端: {type(storage).__name__}")

        if storage.health_check():
            print("  ✅ 存儲健康正常")
            return True
        else:
            print("  ❌ 存儲健康異常")
            # 在實際應用中，這裡可以:
            # - 發送警報
            # - 切換到備用後端
            # - 記錄到日誌
            return False

    # 執行健康檢查
    is_healthy = check_storage_health()

    if is_healthy:
        print("\n系統狀態: 正常運作")
    else:
        print("\n系統狀態: 需要注意")


# ============================================================
# 範例 8: 備份與恢復
# ============================================================

def example_8_backup_restore():
    """範例 8: 記憶備份與恢復"""
    print("\n" + "=" * 70)
    print("範例 8: 備份與恢復")
    print("=" * 70)

    import json

    def backup_memories(memory_ids: List[str], backup_dir: str):
        """備份指定記憶到目錄"""
        storage = create_storage()
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        print(f"備份目錄: {backup_dir}")

        for memory_id in memory_ids:
            memory = storage.retrieve(memory_id)
            if memory:
                backup_file = backup_path / f"{memory_id}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(memory, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 已備份: {memory_id}")
            else:
                print(f"  ❌ 不存在: {memory_id}")

    def restore_memories(backup_dir: str):
        """從備份目錄恢復記憶"""
        storage = create_storage()
        backup_path = Path(backup_dir)

        print(f"恢復目錄: {backup_dir}")

        if not backup_path.exists():
            print("  ❌ 備份目錄不存在")
            return

        for backup_file in backup_path.glob("*.json"):
            with open(backup_file, 'r', encoding='utf-8') as f:
                memory = json.load(f)

            memory_id = storage.store(memory)
            print(f"  ✅ 已恢復: {memory_id}")

    # 測試備份
    test_ids = ["mem_example1_001", "mem_batch_001"]
    backup_memories(test_ids, "data/backup/memories")

    # 測試恢復（實際使用時小心，會覆蓋現有記憶）
    # restore_memories("data/backup/memories")
    print("\n（恢復功能已註解，避免覆蓋現有記憶）")


# ============================================================
# 主程式
# ============================================================

def main():
    """執行所有範例"""
    print("=" * 70)
    print("通用記憶存儲系統 - 實用範例代碼")
    print("=" * 70)

    examples = [
        ("基礎使用", example_1_basic_usage),
        ("完整記憶交接", example_2_full_handoff),
        ("語義搜尋", example_3_semantic_search),
        ("條件性功能使用", example_4_conditional_features),
        ("批次處理", example_5_batch_processing),
        ("環境感知配置", example_6_environment_aware),
        ("健康監控", example_7_health_monitoring),
        ("備份與恢復", example_8_backup_restore),
    ]

    print(f"\n共 {len(examples)} 個範例\n")

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n❌ 範例 {i} ({name}) 執行失敗: {e}")

    print("\n" + "=" * 70)
    print("所有範例執行完畢")
    print("=" * 70)


if __name__ == "__main__":
    main()
