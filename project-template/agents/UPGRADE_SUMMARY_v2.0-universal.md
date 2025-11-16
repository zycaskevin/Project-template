---
title: 專家系統統一升級摘要 v2.0-universal
date: 2025-11-16
applies_to: [小後, 小架, 小米, 及所有其他專家]
---

# 專家系統統一升級摘要 v2.0-universal

## 🎯 升級目標

將所有專家從硬編碼 `IntelligentMemorySystem` 升級到 `MemoryHub`，整合 Universal Storage v2.0.0。

---

## 📋 升級檢查清單（適用所有專家）

### 1. Import 語句替換

**❌ 舊 (v1.0/v2.0)**:
```python
from core.memory.intelligent_memory_system import IntelligentMemorySystem
```

**✅ 新 (v2.0-universal)**:
```python
from integrations.memory_hub import MemoryHub
from integrations.universal_memory_storage import StorageCapability  # 可選
```

---

### 2. 初始化替換

**❌ 舊**:
```python
memory = IntelligentMemorySystem(persist_directory="data/vectors/semantic_memory")
```

**✅ 新**:
```python
hub = MemoryHub()

# 可選: 檢查能力
if hub.capability == StorageCapability.FULL:
    print("✅ EvoMem 可用")
else:
    print("⚠️ 降級模式")
```

---

### 3. 查詢方法替換

**❌ 舊**:
```python
results = memory.query(
    "[模組] 歷史 Bug",
    n_results=5,
    where={"expert": "xiaocheng", "type": "bug"}
)
```

**✅ 新 - 推薦方式**:
```python
results = hub.intelligent_query(
    query="[模組] 歷史 Bug",
    agent_type="xiaocheng",  # 替代 where={"expert": ...}
    n_results=5
)
# 注意: type 過濾需手動實作（或等 v2.1 支援 where 參數）
```

**✅ 新 - 向後相容方式**（暫時可用）:
```python
results = hub.query(
    "[模組] 歷史 Bug",
    n_results=5,
    where={"expert": "xiaocheng"}
)
```

---

### 4. 添加記憶替換

**❌ 舊**:
```python
memory.add_memory(
    content="學習內容",
    metadata={
        "expert": "xiaocheng",
        "type": "learning",
        "tags": ["TDD"]
    }
)
```

**✅ 新 - 推薦方式**:
```python
hub.add_memory(
    content="學習內容",
    expert="xiaocheng",
    memory_type="learning",
    tags=["TDD"]
)
```

**✅ 新 - 完全相容方式**:
```python
hub.add_memory(
    content="學習內容",
    metadata={
        "expert": "xiaocheng",
        "type": "learning",
        "tags": ["TDD"]
    }
)
```

---

## 🎯 專家特定升級指南

### 小後（Backend Developer） v1.0 → v2.0-universal

**典型使用場景**:

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# API 設計模式查詢
api_patterns = hub.intelligent_query(
    query="[API 設計] RESTful 分頁 過濾 最佳實踐",
    agent_type="xiaohou",
    n_results=5
)

# 資料庫優化查詢
db_optimization = hub.intelligent_query(
    query="[PostgreSQL] N+1 Problem 索引優化",
    agent_type="xiaohou",
    n_results=5
)

# 儲存後端經驗
hub.add_memory(
    content="API 分頁實作: cursor-based pagination 效能優於 offset，適合大數據集",
    expert="xiaohou",
    memory_type="learning",
    tags=["API", "pagination", "performance"]
)
```

**核心職責保留**:
- ✅ Clean Architecture + DDD
- ✅ API 設計 (RESTful/GraphQL)
- ✅ 資料庫優化 (索引/N+1)
- ✅ 認證授權 (JWT/OAuth)
- ✅ 效能優化

---

### 小架（Architect） v1.0 → v2.0-universal

**典型使用場景**:

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# 查詢歷史架構決策 (ADR)
decisions = hub.intelligent_query(
    query="[系統] type:decision architecture",
    agent_type="xiaojia",
    n_results=5
)

# 技術選型經驗
tech_choices = hub.intelligent_query(
    query="[技術選型] trade-off 評估",
    agent_type="xiaojia",
    n_results=3
)

# 儲存架構決策 (ADR)
hub.add_memory(
    content="採用 Universal Storage v2.0.0: 解耦合 + 可測試 + 可擴展，權衡: +30% 查詢延遲",
    expert="xiaojia",
    memory_type="decision",
    metadata={
        "status": "adopted",  # proposed | adopted | deprecated
        "tags": ["universal-storage", "tech-selection"],
        "decision_date": "2025-11-16"
    }
)
```

**核心職責保留**:
- ✅ 系統架構設計
- ✅ ADR 管理
- ✅ 技術選型
- ✅ 架構模式 (微服務/單體/Serverless)
- ✅ 非功能需求 (可擴展性/可維護性)

---

### 小米（Orchestrator） v1.0 → v2.0-universal

**典型使用場景**:

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# 查詢歷史協調模式
coordination = hub.intelligent_query(
    query="[任務類型] type:coordination workflow",
    agent_type="xiaomi",
    n_results=5
)

# 查詢 Agent 協作經驗
collaboration = hub.intelligent_query(
    query="[多 Agent] 協作模式 衝突解決",
    agent_type="xiaomi",
    n_results=3
)

# 儲存協調經驗
hub.add_memory(
    content="TDD 開發任務協調: 小質 SBE → 小程 Red-Green-Refactor，成功率 100%，平均時間 2小時",
    expert="xiaomi",
    memory_type="coordination",
    tags=["TDD", "workflow"],
    metadata={
        "agents_involved": ["xiaozhi", "xiaocheng"],
        "success_rate": 1.0,
        "avg_duration_hours": 2
    }
)
```

**核心職責保留**:
- ✅ 任務分解與路由
- ✅ Agent 衝突仲裁
- ✅ 工作流程編排
- ✅ 4-Layer 權限架構
  - Level 1: 小米（戰略）
  - Level 2: 領域專家
  - Level 3: 執行層
  - Level 4: 支援層（小憶/小查）

---

## 📊 通用升級效益

### 所有專家獲得

| 特性 | v1.0/v2.0 | v2.0-universal | 改善 |
|------|----------|---------------|------|
| **後端耦合度** | 🔴 緊耦合 EvoMem | 🟢 鬆耦合 | ↑ 80% |
| **可測試性** | 🟡 需實際 DB | 🟢 可 Mock | ↑ 60% |
| **降級保護** | ❌ 無 | ✅ 自動 | ↑ 100% |
| **快取層** | ❌ 無 | ✅ 50%+ 命中 | 新增 |
| **查詢延遲** | 45ms | 60ms (+33%) | 可接受 |

### 新增能力

1. **智能推薦**:
   ```python
   recommendations = hub.get_recommendations(
       context="當前任務情境",
       n_results=10,
       min_quality_score=70
   )
   ```

2. **品質評分**:
   ```python
   score = hub.calculate_quality_score(memory)
   # 0-100 分（來源/頻率/時效性/驗證）
   ```

3. **統計資訊**:
   ```python
   stats = hub.get_statistics()
   # total_queries, cache_hit_rate, avg_latency_ms
   ```

---

## ⚠️ 通用已知限制

### 1. metadata 過濾功能變更

**問題**: `where` 參數不支援複雜過濾

**影響**: 2x 查詢開銷（手動過濾）

**緩解**:
- 短期: 使用 `intelligent_query(agent_type=...)` 過濾專家
- 中期: v2.1 將支援原生 `where` 參數

### 2. 降級模式限制

**EvoMem 不可用時**:
- ❌ 無語義搜尋（返回空列表）
- ✅ 可添加記憶（存入 JSON）
- ✅ 品質評分仍可用

**緩解**:
```python
if hub.capability == StorageCapability.FULL:
    results = hub.intelligent_query("查詢", n_results=5)
else:
    # 使用離線快取
    results = load_offline_cache("查詢")
```

---

## 🧪 通用測試策略

### 測試檢查清單

- [ ] MemoryHub 初始化
- [ ] 專家特定查詢（按 agent_type 過濾）
- [ ] 添加記憶（專家 metadata）
- [ ] 快取機制運作
- [ ] 降級模式處理
- [ ] 向後相容（舊 API 仍可用）
- [ ] 統計資訊正確

### 測試範例

```python
def test_expert_memory_integration():
    """測試專家記憶整合"""
    hub = MemoryHub()

    # 添加專家記憶
    hub.add_memory(
        content="測試內容",
        expert="xiaocheng",
        memory_type="learning"
    )

    # 查詢專家記憶
    results = hub.intelligent_query(
        query="測試",
        agent_type="xiaocheng",
        n_results=5
    )

    # 驗證
    assert isinstance(results, list)
    # 注意: 實際結果取決於 EvoMem 是否可用
```

---

## 📚 通用文檔參考

- [Universal Memory Storage v2.0.0](../integrations/README.zh-TW.md)
- [MemoryHub API](../integrations/memory_hub.py)
- [MemoryHub 測試套件](../integrations/test_memory_hub.py)
- [小憶 v4.0-universal](xiaoji-memory-keeper-v4.md)
- [小程 v3.0-universal](xiaocheng-developer-v3.md)
- [小質 v3.0-universal](xiaozhi-quality-v3.md)

---

## 🔄 升級時程建議

| 專家 | 優先級 | 預估時間 | 理由 |
|------|-------|---------|------|
| 小憶 | P0 | 4-6 小時 | 記憶中樞，影響所有專家 |
| 小程, 小質 | P1 | 6 小時 | TDD 核心流程 |
| 小後, 小架, 小米 | P1 | 9 小時 | 架構與協調專家 |
| 其他專家 | P2 | 12+ 小時 | 輔助專家 |

---

**🎯 所有專家升級到 v2.0-universal 後，將獲得**:
- ✅ 統一 MemoryHub API
- ✅ 自動降級保護
- ✅ 快取層（50%+ 命中率）
- ✅ 智能推薦系統
- ✅ 品質評分
- ✅ 向後相容
- ✅ 後端可插拔（未來可輕鬆切換 Redis/PostgreSQL/雲端向量資料庫）

---

**版本**: 1.0
**日期**: 2025-11-16
**維護者**: Multi-Expert Team (小米 + 小架 + 小憶 + 小程 + 小質)
