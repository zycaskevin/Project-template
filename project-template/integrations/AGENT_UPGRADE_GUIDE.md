# 專家系統升級指南 (Agent System Upgrade Guide)

**版本**: 1.0.0
**建立日期**: 2025-11-16
**目標**: 將所有專家升級到 Universal Memory Storage v2.0.0

---

## 📋 目錄

- [升級概述](#升級概述)
- [升級優先級](#升級優先級)
- [通用升級模式](#通用升級模式)
- [分專家升級指南](#分專家升級指南)
  - [P0: 小憶 (Memory Keeper)](#p0-小憶-memory-keeper)
  - [P1: 小程 (Developer)](#p1-小程-developer)
  - [P1: 小質 (QA Expert)](#p1-小質-qa-expert)
  - [P1: 小後 (Backend Developer)](#p1-小後-backend-developer)
  - [P1: 小架 (Architect)](#p1-小架-architect)
- [測試驗證](#測試驗證)
- [常見問題 FAQ](#常見問題-faq)

---

## 🎯 升級概述

### 升級目標

將所有專家的記憶系統從硬編碼 `IntelligentMemorySystem` 升級到 **Universal Memory Storage v2.0.0**，實現：

✅ **自動降級** - EvoMem 不可用時自動切換到 JSON
✅ **能力感知** - 根據 StorageCapability (FULL/BASIC) 調整行為
✅ **零配置** - 開箱即用，自動檢測最佳後端
✅ **向後兼容** - 保留所有現有功能

### 核心變更

**變更前 (舊 API)**:
```python
from core.memory.intelligent_memory_system import IntelligentMemorySystem

memory = IntelligentMemorySystem(persist_directory="data/vectors/semantic_memory")
result = memory.query("查詢內容", n_results=5)
```

**變更後 (新 API)**:
```python
from integrations.universal_memory_storage import create_storage, StorageCapability

# 自動檢測最佳後端
storage = create_storage()

# 能力感知查詢
if storage.capability == StorageCapability.FULL:
    results = storage.search("查詢內容", n_results=5)
else:
    print("⚠️ 語義搜尋不可用，使用基礎模式")
    results = []
```

---

## 🚦 升級優先級

| 優先級 | 專家 | 理由 | 預估時間 |
|-------|------|------|---------|
| **🔴 P0** | 小憶 (Memory Keeper) | 記憶中樞，影響所有專家 | 4-6 小時 |
| **🟡 P1** | 小程 (Developer) | TDD 流程核心依賴 | 2-3 小時 |
| **🟡 P1** | 小質 (QA Expert) | 測試策略制定依賴 | 2-3 小時 |
| **🟡 P1** | 小後 (Backend Developer) | 後端開發模式查詢 | 2-3 小時 |
| **🟡 P1** | 小架 (Architect) | 架構決策歷史參考 | 2-3 小時 |

---

## 🔧 通用升級模式

### 升級步驟檢查清單

- [ ] **Step 1**: 讀取當前專家的 .md 檔案
- [ ] **Step 2**: 識別所有 `IntelligentMemorySystem` 使用位置
- [ ] **Step 3**: 替換為 `create_storage()` + 能力檢測
- [ ] **Step 4**: 更新範例代碼（加入降級處理）
- [ ] **Step 5**: 更新版本號與變更記錄
- [ ] **Step 6**: 撰寫測試驗證腳本
- [ ] **Step 7**: 執行測試並驗證功能

### 代碼替換模板

#### 模式 1: 基礎查詢

**替換前**:
```python
from core.memory.intelligent_memory_system import IntelligentMemorySystem

memory = IntelligentMemorySystem(persist_directory="data/vectors/semantic_memory")
result = memory.query("AI 標籤 PRD", n_results=5)
```

**替換後**:
```python
from integrations.universal_memory_storage import create_storage, StorageCapability

# 自動檢測後端
storage = create_storage()

# 能力感知查詢
if storage.capability == StorageCapability.FULL:
    result = storage.search("AI 標籤 PRD", n_results=5)
else:
    print("⚠️ EvoMem 不可用，語義搜尋功能降級")
    result = []
```

#### 模式 2: 帶 Metadata 過濾的查詢

**替換前**:
```python
# 小憶的智能路由（根據 Agent 類型過濾）
result = memory.query(
    "[模組] 歷史 Bug",
    n_results=5,
    where={"expert": "xiaocheng"}  # ⚠️ 舊 API 參數
)
```

**替換後**:
```python
# Universal Storage v2.0.0 保留 metadata
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    # EvoMem 支援 metadata 過濾
    result = storage.search(
        "[模組] 歷史 Bug",
        n_results=5
        # ⚠️ 注意: 當前版本 search() 不支援 where 參數
        # 需在結果中手動過濾 metadata
    )

    # 手動過濾 metadata
    filtered_results = [
        r for r in result
        if r.get("metadata", {}).get("expert") == "xiaocheng"
    ]
else:
    # JSON 後端降級
    filtered_results = []
```

#### 模式 3: 儲存記憶

**替換前**:
```python
memory.add_memory(
    content="[模組] 解決方案",
    metadata={"expert": "xiaocheng", "type": "learning"}
)
```

**替換後**:
```python
storage = create_storage()

# Universal Storage 統一使用 store()
memory_item = {
    "id": f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "type": "learning",
    "content": "[模組] 解決方案",
    "metadata": {
        "expert": "xiaocheng",
        "tags": ["learning", "pattern"]
    }
}

memory_id = storage.store(memory_item)
```

---

## 👥 分專家升級指南

---

### 🔴 P0: 小憶 (Memory Keeper)

**當前版本**: v3.0-hub
**升級目標**: v4.0-universal
**預估時間**: 4-6 小時

#### 核心功能與升級需求

小憶是整個專家系統的**記憶中樞**，負責：

1. ✅ **智能查詢路由** - 根據 Agent 類型路由到不同過濾器
2. ✅ **主動推薦** - 提供洞察與模式發現
3. ✅ **跨專案記憶** - 搜尋 EvoMem / Buylist / StoryForge
4. ✅ **品質評分** - 0-100 分評分機制

#### 升級挑戰

| 功能 | 當前實作 | Universal Storage | 升級策略 |
|------|---------|------------------|---------|
| **智能路由** | `where={"expert": "xxx"}` | metadata 手動過濾 | 包裝函數 |
| **主動推薦** | 基於 metadata tags | ✅ 兼容 | 無需變更 |
| **跨專案搜尋** | `metadata.project` | ✅ 兼容 | 無需變更 |
| **品質評分** | 自定義 `score` | ✅ 兼容 | 無需變更 |

#### 升級實作範例

**小憶專用包裝函數** (保留智能路由功能):

```python
from integrations.universal_memory_storage import create_storage, StorageCapability
from typing import List, Dict, Optional

class MemoryHub:
    """小憶記憶中樞 - Universal Storage 包裝器"""

    def __init__(self):
        self.storage = create_storage()
        self.capability = self.storage.capability

    def intelligent_query(
        self,
        query: str,
        agent_type: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """智能查詢路由（保留 v3.0-hub 功能）"""

        if self.capability != StorageCapability.FULL:
            print("⚠️ EvoMem 不可用，語義搜尋降級")
            return []

        # 語義搜尋
        results = self.storage.search(query, n_results=n_results * 2)  # 多取一些以便過濾

        # 手動過濾 metadata (替代舊 where 參數)
        if agent_type:
            results = [
                r for r in results
                if r.get("metadata", {}).get("expert") == agent_type
            ]

        # 限制結果數量
        return results[:n_results]

    def proactive_recommend(
        self,
        context: str,
        category: str
    ) -> List[Dict]:
        """主動推薦（基於上下文）"""

        if self.capability != StorageCapability.FULL:
            return []

        # 擴展查詢
        expanded_query = f"{context} {category} type:pattern best-practice"
        results = self.storage.search(expanded_query, n_results=3)

        return results

    def cross_project_search(
        self,
        query: str,
        projects: List[str]
    ) -> Dict[str, List[Dict]]:
        """跨專案記憶搜尋"""

        if self.capability != StorageCapability.FULL:
            return {p: [] for p in projects}

        results_by_project = {}

        for project in projects:
            results = self.storage.search(query, n_results=5)
            # 過濾專案
            filtered = [
                r for r in results
                if r.get("metadata", {}).get("project") == project
            ]
            results_by_project[project] = filtered

        return results_by_project

    def save_memory(
        self,
        content: str,
        metadata: Dict
    ) -> str:
        """儲存記憶（統一介面）"""

        memory_item = {
            "id": f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "type": metadata.get("type", "general"),
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return self.storage.store(memory_item)

# 使用範例
hub = MemoryHub()

# 智能查詢（自動路由）
results = hub.intelligent_query(
    query="計算機模塊 歷史 Bug",
    agent_type="xiaocheng",  # 路由到小程的記憶
    n_results=5
)

# 主動推薦
recommendations = hub.proactive_recommend(
    context="實作新功能",
    category="design-pattern"
)
```

#### 升級後的小憶文檔更新

在 `xiaoji-memory-keeper.md` 中需要更新的章節：

1. **版本號**: v3.0-hub → **v4.0-universal**
2. **EvoMem 整合章節**: 更新為 Universal Storage API
3. **範例代碼**: 全部替換為 `MemoryHub` 包裝器
4. **能力說明**: 新增 FULL vs BASIC capability 說明
5. **降級處理**: 新增 EvoMem 不可用時的行為說明

---

### 🟡 P1: 小程 (Developer)

**當前版本**: v2.1-optimized
**升級目標**: v2.2-universal
**預估時間**: 2-3 小時

#### TDD 流程記憶查詢升級

**Red Phase** - 查詢歷史 Bug:

```python
# 升級前
result = memory.query("[模組名稱] 歷史 Bug 錯誤", n_results=5)

# 升級後
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    result = storage.search("[模組名稱] 歷史 Bug 錯誤", n_results=5)
else:
    print("⚠️ 語義搜尋不可用，建議手動查詢歷史代碼")
    result = []
```

**Green Phase** - 查詢實作模式:

```python
# 升級前
patterns = memory.query("[功能] 實作 最佳實踐 範例", n_results=3)

# 升級後
if storage.capability == StorageCapability.FULL:
    patterns = storage.search("[功能] 實作 最佳實踐 範例", n_results=3)
else:
    print("⚠️ 無法查詢歷史模式，使用預設實作")
    patterns = []
```

**Refactor Phase** - 查詢重構模式:

```python
# 升級前
refactor_patterns = memory.query("[程式碼模式] 重構 最佳實踐", n_results=3)

# 升級後
if storage.capability == StorageCapability.FULL:
    refactor_patterns = storage.search("[程式碼模式] 重構 最佳實踐", n_results=3)
else:
    print("⚠️ 無法查詢重構模式，手動審查代碼")
    refactor_patterns = []
```

#### 文檔更新

在 `xiaocheng-developer.md` 中：

1. **版本號**: v2.1-optimized → **v2.2-universal**
2. **EvoMem 整合章節**: 更新所有範例代碼
3. **降級說明**: 新增 BASIC capability 下的工作流程
4. **最佳實踐**: 建議在 Red Phase 前檢查 storage.capability

---

### 🟡 P1: 小質 (QA Expert)

**當前版本**: v2.0-evomem
**升級目標**: v2.1-universal
**預估時間**: 2-3 小時

#### 測試策略查詢升級

**查詢歷史測試案例**:

```python
# 升級前
test_cases = memory.query("[功能] .feature 測試案例 場景", n_results=5)

# 升級後
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    test_cases = storage.search("[功能] .feature 測試案例 場景", n_results=5)
else:
    print("⚠️ 無法語義搜尋歷史測試，建議手動檢視")
    test_cases = []
```

**查詢遺漏測試**:

```python
# 升級前
missed_tests = memory.query("[功能] 遺漏測試 Bug 邊界", n_results=3)

# 升級後
if storage.capability == StorageCapability.FULL:
    missed_tests = storage.search("[功能] 遺漏測試 Bug 邊界", n_results=3)
else:
    print("⚠️ 無法查詢遺漏測試，請手動審查")
    missed_tests = []
```

#### 文檔更新

在 `xiaozhi-quality.md` 中：

1. **版本號**: v2.0-evomem → **v2.1-universal**
2. **範例代碼**: 更新所有記憶查詢
3. **測試策略**: 新增降級模式下的測試建議
4. **SBE 工作坊**: 說明 FULL capability 對測試覆蓋率的重要性

---

### 🟡 P1: 小後 (Backend Developer)

**當前版本**: v1.0
**升級目標**: v1.1-universal
**預估時間**: 2-3 小時

#### 後端模式查詢升級

**API 設計查詢**:

```python
# 升級前
api_patterns = memory.query(
    "[API 設計] RESTful 分頁 過濾 排序 最佳實踐",
    n_results=5
)

# 升級後
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    api_patterns = storage.search(
        "[API 設計] RESTful 分頁 過濾 排序 最佳實踐",
        n_results=5
    )
else:
    print("⚠️ 無法查詢 API 模式，建議參考 OpenAPI 文檔")
    api_patterns = []
```

**資料庫優化查詢**:

```python
# 升級前
db_optimization = memory.query(
    "[PostgreSQL] N+1 Problem 解決方案 索引優化",
    n_results=5
)

# 升級後
if storage.capability == StorageCapability.FULL:
    db_optimization = storage.search(
        "[PostgreSQL] N+1 Problem 解決方案 索引優化",
        n_results=5
    )
else:
    print("⚠️ 無法查詢優化模式，建議使用 EXPLAIN ANALYZE")
    db_optimization = []
```

#### 儲存後端經驗

```python
# 升級前
memory.add_memory(
    content="[API 設計] 使用複合索引優化多條件查詢...",
    metadata={
        "type": "backend_pattern",
        "expert": "xiaohou",
        "tags": ["postgresql", "optimization"]
    }
)

# 升級後
storage = create_storage()

memory_item = {
    "id": f"mem_backend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "type": "backend_pattern",
    "content": "[API 設計] 使用複合索引優化多條件查詢...",
    "metadata": {
        "expert": "xiaohou",
        "category": "database_optimization",
        "tags": ["postgresql", "optimization", "index"]
    },
    "timestamp": datetime.now(timezone.utc).isoformat()
}

memory_id = storage.store(memory_item)
```

#### 文檔更新

在 `xiaohou-backend-developer.md` 中：

1. **版本號**: v1.0 → **v1.1-universal**
2. **EvoMem 整合章節**: 完整更新
3. **範例代碼**: 所有查詢與儲存範例
4. **降級影響**: 說明 BASIC 模式下對開發效率的影響

---

### 🟡 P1: 小架 (Architect)

**當前版本**: v1.0
**升級目標**: v1.1-universal
**預估時間**: 2-3 小時

#### 架構決策查詢升級

**查詢歷史架構決策**:

```python
# 升級前
decisions = memory.query(
    "[系統] type:decision architecture design",
    n_results=5
)

# 升級後
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    decisions = storage.search(
        "[系統] type:decision architecture design",
        n_results=5
    )
else:
    print("⚠️ 無法查詢歷史決策，建議查閱 ADR 文檔")
    decisions = []
```

**查詢技術選型**:

```python
# 升級前
tech_choices = memory.query(
    "[技術名稱] type:decision tech-selection trade-off",
    n_results=3
)

# 升級後
if storage.capability == StorageCapability.FULL:
    tech_choices = storage.search(
        "[技術名稱] type:decision tech-selection trade-off",
        n_results=3
    )
else:
    print("⚠️ 無法查詢技術選型，建議手動對比")
    tech_choices = []
```

#### 儲存架構決策 (ADR)

```python
# 升級前
memory.add_memory(
    content="EvoMem 選擇 ChromaDB 作為向量資料庫，理由：輕量級...",
    metadata={
        "type": "decision",
        "expert": "xiaojia",
        "status": "adopted"
    }
)

# 升級後
storage = create_storage()

adr_item = {
    "id": f"mem_adr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "type": "decision",
    "content": "EvoMem 選擇 ChromaDB 作為向量資料庫，理由：輕量級...",
    "metadata": {
        "expert": "xiaojia",
        "module": "CoreMemory",
        "category": "database",
        "tags": ["chromadb", "vector-database", "tech-selection"],
        "status": "adopted"
    },
    "timestamp": datetime.now(timezone.utc).isoformat()
}

memory_id = storage.store(adr_item)
```

#### 文檔更新

在 `xiaojia-architect.md` 中：

1. **版本號**: v1.0 → **v1.1-universal**
2. **EvoMem 整合章節**: 全面更新
3. **ADR 範例**: 更新儲存格式
4. **降級策略**: 說明 BASIC 模式下如何使用 .md 文檔代替

---

## ✅ 測試驗證

### 測試腳本範例

創建 `test_agent_upgrade.py` 驗證升級：

```python
"""
測試專家升級到 Universal Storage v2.0.0
"""

import sys
from pathlib import Path

# Add integrations to path
sys.path.insert(0, str(Path(__file__).parent.parent / "integrations"))

from universal_memory_storage import create_storage, StorageCapability

def test_storage_initialization():
    """測試 1: Storage 初始化"""
    print("\n🧪 測試 1: Storage 初始化")

    storage = create_storage()
    assert storage is not None
    assert hasattr(storage, 'capability')

    print(f"  ✅ Storage 類型: {type(storage).__name__}")
    print(f"  ✅ Capability: {storage.capability.value}")

def test_capability_detection():
    """測試 2: Capability 檢測"""
    print("\n🧪 測試 2: Capability 檢測")

    storage = create_storage()

    if storage.capability == StorageCapability.FULL:
        print("  ✅ 檢測到 FULL capability (EvoMem 可用)")
    else:
        print("  ✅ 檢測到 BASIC capability (JSON 後端)")

def test_search_functionality():
    """測試 3: 搜尋功能"""
    print("\n🧪 測試 3: 搜尋功能")

    storage = create_storage()

    # 先儲存測試記憶
    test_memory = {
        "id": "mem_test_upgrade_001",
        "type": "test",
        "content": "測試升級功能",
        "metadata": {"expert": "test", "tags": ["upgrade"]}
    }

    memory_id = storage.store(test_memory)
    print(f"  ✅ 已儲存測試記憶: {memory_id}")

    # 測試檢索
    retrieved = storage.retrieve(memory_id)
    assert retrieved is not None
    print(f"  ✅ 檢索成功: {retrieved['id']}")

    # 測試搜尋（僅 FULL capability）
    if storage.capability == StorageCapability.FULL:
        results = storage.search("測試", n_results=1)
        print(f"  ✅ 搜尋成功: 找到 {len(results)} 個結果")
    else:
        print("  ⚠️ BASIC capability 不支援語義搜尋")

def test_degradation():
    """測試 4: 降級機制"""
    print("\n🧪 測試 4: 降級機制")

    # 嘗試明確指定 JSON 後端
    storage_json = create_storage({"type": "json"})

    assert storage_json.capability == StorageCapability.BASIC
    print("  ✅ JSON 後端降級成功")

    # 測試 search() 在 BASIC 模式下返回空列表
    results = storage_json.search("任何查詢")
    assert results == []
    print("  ✅ BASIC 模式 search() 返回空列表（預期行為）")

if __name__ == "__main__":
    print("=" * 70)
    print("專家系統升級驗證測試")
    print("=" * 70)

    test_storage_initialization()
    test_capability_detection()
    test_search_functionality()
    test_degradation()

    print("\n" + "=" * 70)
    print("✅ 所有測試通過！專家升級驗證成功")
    print("=" * 70)
```

### 執行測試

```bash
cd project-template/integrations
python test_agent_upgrade.py
```

---

## ❓ 常見問題 FAQ

### Q1: 升級後舊的 IntelligentMemorySystem 還能用嗎？

**A**: 可以。Universal Storage 是**新增**系統，不影響舊 API。但建議逐步遷移以享受自動降級功能。

### Q2: 升級後 EvoMem 不可用會怎樣？

**A**: 自動降級到 JSON 後端。所有 `store()` 和 `retrieve()` 功能正常，但 `search()` 返回空列表。

### Q3: metadata 過濾功能還支援嗎？

**A**: 支援，但需要手動過濾。建議使用 `MemoryHub` 包裝器（見小憶升級指南）。

### Q4: 升級是否需要修改所有專家檔案？

**A**: 是的。為了一致性與可靠性，建議一次性升級所有專家。可依優先級分階段進行：
- **第一階段**: 小憶 (P0)
- **第二階段**: 小程、小質、小後、小架 (P1)
- **第三階段**: 其他專家 (P2)

### Q5: 升級後如何測試？

**A**: 使用 `test_agent_upgrade.py` 驗證：
1. Storage 初始化正常
2. Capability 檢測正確
3. 搜尋功能運作（FULL 模式）
4. 降級機制正常（BASIC 模式）

### Q6: 升級失敗如何回滾？

**A**: 保留舊版本檔案備份。升級前：
```bash
cp xiaoji-memory-keeper.md xiaoji-memory-keeper.md.v3.0-hub.backup
```

回滾：
```bash
mv xiaoji-memory-keeper.md.v3.0-hub.backup xiaoji-memory-keeper.md
```

---

## 📅 升級時程建議

| 週次 | 任務 | 交付物 |
|-----|------|-------|
| **Week 1** | 升級小憶 (P0) | `xiaoji-memory-keeper.md` v4.0-universal |
| **Week 2** | 升級 P1 專家 (4位) | 4 個 .md 檔案更新 |
| **Week 3** | 升級剩餘專家 | 所有 .md 檔案更新完成 |
| **Week 4** | 整合測試與文檔 | 完整測試報告 + 升級總結 |

---

**最後更新**: 2025-11-16
**維護者**: Claude Code + zycaskevin
**版本**: 1.0.0
