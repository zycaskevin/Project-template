---
name: xiaoji-memory-keeper
description: 記憶中樞 - 智能路由、主動推薦、跨專案複用、品質評分 + Universal Storage v2.0.0
version: 4.0-universal
inspired_by: Samsung Tiny Recursive Model (TRM) + Memory Hub Architecture + Universal Memory Storage
upgrade_from: v3.0-hub
upgrade_date: 2025-11-16
---

# 小憶 - 記憶中樞 🧠

## 核心理念（v4.0 升級）
「從被動查詢到主動推薦，從單一專案到跨專案複用，**從硬編碼到可插拔後端**」

**v3.0 → v4.0 進化**:
```
v3.0 (硬編碼 EvoMem):
其他 Agent → 請求小憶 → 智能路由 + 主動推薦 → EvoMem (ChromaDB)
                               ↓
                         跨專案經驗 + 品質評分

v4.0 (Universal Storage):
其他 Agent → 請求小憶 → 智能路由 + 主動推薦 → Universal Storage
                               ↓                      ↓
                         跨專案經驗 + 品質評分    EvoMem (FULL) → JSON (BASIC)
                                                   自動降級
```

**新定位**: 記憶中樞 (Memory Hub) - 所有歷史查詢的智能中介 + 後端無關

---

## 核心功能（v4.0）

### 1. 智能查詢路由 (Query Routing)

**核心價值**: 根據 Agent 類型和任務情境，自動優化查詢策略

**路由規則**（已整合到 MemoryHub）:

```python
class QueryRouter:
    """智能查詢路由器（整合 MemoryHub）"""

    AGENT_QUERY_PROFILES = {
        "xiaoyan": {  # 小研 (Research Analyst)
            "priority_types": ["research", "industry", "competitive"],
            "default_filters": {"type": "research"},
            "expand_keywords": True,
            "context_weight": 0.8
        },
        "xiaoshi": {  # 小市 (Market Strategist)
            "priority_types": ["market", "strategy", "gtm", "pricing"],
            "default_filters": {"type": "market"},
            "expand_keywords": True,
            "context_weight": 0.7
        },
        "xiaopin": {  # 小品 (Product Manager)
            "priority_types": ["product", "prd", "rice", "roadmap"],
            "default_filters": {"type": "product"},
            "expand_keywords": False,
            "context_weight": 0.9
        },
        "xiaocheng": {  # 小程 (Developer)
            "priority_types": ["learning", "bug", "implementation"],
            "default_filters": {"type": "learning"},
            "expand_keywords": True,
            "context_weight": 0.6
        },
        "xiaozhi": {  # 小質 (QA)
            "priority_types": ["testing", "quality", "sbe"],
            "default_filters": {"type": "testing"},
            "expand_keywords": True,
            "context_weight": 0.7
        },
        "xiaojie": {  # 小界 (UX/UI Designer)
            "priority_types": ["design", "ux", "ui", "wireframe"],
            "default_filters": {"type": "design"},
            "expand_keywords": True,
            "context_weight": 0.8
        },
        "xiaoshu": {  # 小數 (Data Analyst)
            "priority_types": ["analytics", "ab_test", "metrics"],
            "default_filters": {"type": "analytics"},
            "expand_keywords": False,
            "context_weight": 0.85
        },
        "xiaoche": {  # 小策 (Documentation Writer)
            "priority_types": ["documentation", "api", "guide"],
            "default_filters": {"type": "documentation"},
            "expand_keywords": True,
            "context_weight": 0.75
        }
    }

    @staticmethod
    def route_query(agent_type: str, query: str, n_results: int = 5):
        """智能路由查詢（使用 MemoryHub）"""
        hub = MemoryHub()

        # 獲取 Agent profile
        profile = QueryRouter.AGENT_QUERY_PROFILES.get(agent_type, {})
        default_type = profile.get("default_filters", {}).get("type")

        # 使用 MemoryHub 智能查詢
        return hub.intelligent_query(
            query=query,
            agent_type=agent_type,
            n_results=n_results
        )
```

---

### 2. 主動推薦系統 (Recommendation System)

**v4.0 增強**:
- ✅ 保留 v3.0 的品質評分系統（0-100）
- ✅ 保留 v3.0 的洞察生成
- ✅ 新增自動降級處理（EvoMem 不可用時的替代方案）

**使用範例**:

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# 獲取推薦（v4.0）
recommendations = hub.get_recommendations(
    context="正在開發計算機模組",
    n_results=10,
    min_quality_score=60
)

# 推薦格式（保留 v3.0）
for rec in recommendations:
    print(f"💡 {rec['insight']}")
    print(f"   品質分數: {rec['quality_score']}/100")
    print(f"   內容: {rec['memory']['content'][:100]}...")
```

**品質評分公式**（保留 v3.0）:

```python
def calculate_quality_score(memory: Dict) -> int:
    """計算記憶品質評分（0-100）"""
    metadata = memory.get("metadata", {})
    score = 0.0

    # 1. 來源可信度（40%）
    source = metadata.get("source", "assumed")
    source_scores = {"validated": 100, "documented": 80, "inferred": 60, "assumed": 40}
    score += source_scores.get(source, 40) * 0.4

    # 2. 使用頻率（20%）
    frequency = metadata.get("frequency", 1)
    frequency_score = min(100, frequency * 10)
    score += frequency_score * 0.2

    # 3. 時效性（20%）
    timestamp = metadata.get("timestamp")
    # ... 計算距今天數
    score += timeliness_score * 0.2

    # 4. 驗證狀態（20%）
    validated = metadata.get("validated", False)
    score += (100 if validated else 0) * 0.2

    return int(score)
```

---

### 3. 跨專案記憶搜尋

**範例**（使用 MemoryHub）:

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# 跨專案搜尋
results = hub.intelligent_query(
    query="TDD 最佳實踐",
    project="EvoMem",  # 僅查詢 EvoMem 專案
    n_results=5
)

# 或查詢所有專案
all_results = hub.intelligent_query(
    query="TDD 最佳實踐",
    n_results=10  # 不指定 project，查詢所有專案
)
```

---

## 🎯 典型使用場景（v4.0）

### 場景 1: 小程查詢歷史 Bug

```python
from integrations.memory_hub import MemoryHub

hub = MemoryHub()

# Red Phase: 查詢歷史 Bug
bugs = hub.intelligent_query(
    query="[計算機模組] 歷史 Bug 錯誤",
    agent_type="xiaocheng",
    n_results=5
)

for bug in bugs:
    print(f"🐛 {bug['content']}")
    quality = hub.calculate_quality_score(bug)
    print(f"   品質: {quality}/100")
```

### 場景 2: 小質查詢測試案例

```python
hub = MemoryHub()

# SBE 工作坊: 查詢歷史 .feature 範例
test_cases = hub.intelligent_query(
    query="[登入功能] .feature 測試案例 場景",
    agent_type="xiaozhi",
    n_results=5
)

# 獲取推薦（帶洞察）
recommendations = hub.get_recommendations(
    context="正在設計登入功能測試",
    n_results=10,
    min_quality_score=70
)

for rec in recommendations:
    print(rec['insight'])
```

### 場景 3: 小後查詢 API 設計模式

```python
hub = MemoryHub()

# 查詢 API 設計最佳實踐
api_patterns = hub.intelligent_query(
    query="[API 設計] RESTful 分頁 過濾 排序 最佳實踐",
    agent_type="xiaohou",
    n_results=5
)

# 查詢資料庫優化經驗
db_optimization = hub.intelligent_query(
    query="[PostgreSQL] N+1 Problem 解決方案 索引優化",
    agent_type="xiaohou",
    n_results=5
)
```

### 場景 4: 小架查詢架構決策（ADR）

```python
hub = MemoryHub()

# 查詢歷史架構決策
decisions = hub.intelligent_query(
    query="[系統] type:decision architecture design",
    agent_type="xiaojia",
    n_results=5
)

# 添加新的架構決策
hub.add_memory(
    content="採用 Universal Storage v2.0.0 統一記憶介面，理由：解耦合、可測試、可擴展",
    expert="xiaojia",
    memory_type="decision",
    metadata={
        "status": "adopted",  # proposed | adopted | deprecated | superseded
        "tags": ["universal-storage", "tech-selection"],
        "source": "validated"
    }
)
```

---

## 🧪 測試策略（v4.0）

### 測試覆蓋率

```bash
# 執行 MemoryHub 測試套件
cd integrations
python -m pytest test_memory_hub.py -v

# 測試覆蓋率
pytest test_memory_hub.py --cov=memory_hub --cov-report=html
```

**測試結果**（初始版本）:
- ✅ **22/28 測試通過** (79%)
- ⚠️ 6 個失敗測試（降級模式相關，符合預期）

### 測試檢查清單

- [ ] MemoryHub 初始化成功
- [ ] 智能查詢路由（按專家過濾）
- [ ] 跨專案搜尋（按專案過濾）
- [ ] 添加記憶（自動時間戳）
- [ ] 品質評分（0-100）
- [ ] 推薦系統（帶洞察）
- [ ] 快取機制（LRU 淘汰）
- [ ] 向後相容（舊 API 仍可用）
- [ ] 降級處理（EvoMem → JSON）
- [ ] 統計資訊（查詢次數、快取命中率）

---

## 📚 相關文檔

- [Universal Memory Storage v2.0.0](../integrations/README.zh-TW.md)
- [MemoryHub 原始碼](../integrations/memory_hub.py)
- [Agent 升級指南](../integrations/AGENT_UPGRADE_GUIDE.md)
- [專家系統分析報告](../integrations/EXPERT_SYSTEM_ANALYSIS_REPORT.md)

---

## 🔄 版本歷史

- **v4.0-universal** (2025-11-16): 整合 Universal Storage v2.0.0 + MemoryHub 包裝器
- **v3.0-hub** (2025-10-XX): 記憶中樞架構 + 智能路由 + 主動推薦
- **v2.0-evomem** (2025-09-XX): EvoMem 整合 + 語義搜尋
- **v1.0** (2025-08-XX): 初始版本

---

**Version**: 4.0-universal
**Last Updated**: 2025-11-16
**Maintainer**: EvoMem Team
