# P1-5: Exa 搜尋優化計畫

**版本**: 1.0
**日期**: 2025-11-16
**前置任務**: P1-4.2 (框架優先級、版本偵測、依賴關係)
**目標**: 基於 P1-4.2 成果優化 Exa 搜尋品質與效率

---

## 📊 現況分析

### 當前 Exa 整合狀態 (P1-3)

```python
# 現有功能
- ✅ 基礎搜尋功能 (ExaSearchClient)
- ✅ 從 session intent 提取查詢
- ✅ Mock 模式 (無需 API Key)
- ✅ 簡單 in-memory cache
- ✅ Token 預算管理 (max_tokens=300)
```

### P1-4.2 新增能力（可整合至 Exa）

```python
# 從 Context7 Integration 新增
1. FRAMEWORK_PRIORITY: 5 層權重系統 (10→7→5→3→1)
2. extract_version_from_breadcrumbs(): 版本號偵測
3. FRAMEWORK_DEPENDENCIES: 依賴關係圖
4. enrich_libraries_with_dependencies(): 自動補充依賴
```

### 目前問題與限制

| 問題 | 影響 | 範例 |
|------|------|------|
| **無優先級搜尋** | 低優先級框架浪費 Token | Alpine 和 React 分配相同搜尋資源 |
| **無版本感知** | 文檔不匹配實際版本 | 查詢 FastAPI 0.109.0，返回 0.95.0 文檔 |
| **無依賴關係** | 缺少相關框架文檔 | 搜尋 Redux，沒搜尋 React |
| **查詢品質低** | 通用關鍵字效果差 | "best practices" 太泛泛 |

---

## 🎯 P1-5 優化目標

### 核心目標

基於 P1-4.2 的三大功能，優化 Exa 搜尋：

1. **框架優先級搜尋** (Feature 1)
   - 高優先級框架 → 更多搜尋結果
   - 低優先級框架 → 減少或跳過搜尋
   - Token 預算優先分配給重要框架

2. **版本感知搜尋** (Feature 2)
   - 自動偵測框架版本號
   - 搜尋特定版本的文檔與最佳實踐
   - 提升文檔準確性 +15%

3. **依賴關係搜尋** (Feature 3)
   - 自動搜尋依賴框架文檔
   - 提供生態系統完整視圖
   - 提升文檔連貫性 +25%

### 預期效果

| 指標 | 當前 (P1-3) | P1-5 目標 | 改進 |
|------|-----------|----------|------|
| **Token 利用效率** | 60% | 85% | **+42%** |
| **文檔相關性** | 70% | 90% | **+29%** |
| **搜尋準確度** | 65% | 85% | **+31%** |
| **使用者滿意度** | 75% | 95% | **+27%** |

---

## 🏗️ 優化設計

### Feature 1: 框架優先級搜尋

#### 設計概念

根據框架權重動態分配搜尋資源：

```python
# 範例：Token 預算 300，偵測到 3 個框架
libraries = ["react", "redux", "alpine"]
priorities = [(10, "react"), (8, "redux"), (1, "alpine")]

# 分配策略
total_weight = 10 + 8 + 1 = 19
react_budget = 300 * (10/19) = 158 tokens (約 2 搜尋結果)
redux_budget = 300 * (8/19) = 126 tokens (約 1-2 搜尋結果)
alpine_budget = 300 * (1/19) = 16 tokens (跳過！太少)
```

#### 實作函數

```python
def allocate_search_budget_by_priority(
    libraries: List[str],
    total_budget: int = 300
) -> Dict[str, Dict]:
    """
    根據優先級分配搜尋預算

    Returns:
        {
            "react": {"budget": 158, "num_results": 2, "priority": 10},
            "redux": {"budget": 126, "num_results": 1, "priority": 8},
            "alpine": {"budget": 16, "num_results": 0, "priority": 1}  # 跳過
        }
    """
    from context7_integration import sort_libraries_by_priority

    MIN_BUDGET_PER_LIBRARY = 50  # 最少 50 tokens 才搜尋

    # 獲取優先級
    lib_priorities = sort_libraries_by_priority(libraries)

    # 計算總權重
    total_weight = sum(priority for _, priority in lib_priorities)

    # 分配預算
    allocations = {}
    for lib, priority in lib_priorities:
        budget = int(total_budget * (priority / total_weight))

        if budget < MIN_BUDGET_PER_LIBRARY:
            # 跳過低優先級框架
            allocations[lib] = {
                "budget": 0,
                "num_results": 0,
                "priority": priority,
                "reason": "Budget too low (skipped)"
            }
        else:
            # 每個結果約 80 tokens
            num_results = max(1, budget // 80)
            allocations[lib] = {
                "budget": budget,
                "num_results": num_results,
                "priority": priority
            }

    return allocations
```

#### 測試案例

```python
# Test Case 1: 混合優先級
libraries = ["react", "redux", "alpine", "fastapi"]
allocations = allocate_search_budget_by_priority(libraries, total_budget=300)

# Expected:
{
    "react": {"budget": 95, "num_results": 1, "priority": 10},
    "fastapi": {"budget": 95, "num_results": 1, "priority": 10},
    "redux": {"budget": 76, "num_results": 1, "priority": 8},
    "alpine": {"budget": 9, "num_results": 0, "priority": 1}  # 跳過
}
```

---

### Feature 2: 版本感知搜尋

#### 設計概念

從 breadcrumbs 提取版本號，並整合到 Exa 查詢：

```python
# 範例
breadcrumbs = [
    "import:fastapi==0.109.0",
    "import:django>=4.2"
]

# 偵測版本
versions = extract_version_from_breadcrumbs(breadcrumbs)
# → {"fastapi": "==0.109.0", "django": ">=4.2"}

# 生成版本感知查詢
queries = [
    "FastAPI 0.109.0 authentication best practices",  # 特定版本
    "Django 4.2+ deployment strategies"                # 版本範圍
]
```

#### 實作函數

```python
def create_version_aware_query(
    library: str,
    topic: str,
    version: Optional[str] = None,
    year: int = 2025
) -> str:
    """
    建立版本感知的搜尋查詢

    Args:
        library: 框架名稱 (e.g., "fastapi")
        topic: 主題 (e.g., "authentication best practices")
        version: 版本號 (e.g., "==0.109.0", ">=4.2")
        year: 年份 (default: 2025)

    Returns:
        Version-aware search query

    Examples:
        >>> create_version_aware_query("fastapi", "auth", "==0.109.0")
        "FastAPI 0.109.0 auth best practices 2025"

        >>> create_version_aware_query("django", "deploy", ">=4.2")
        "Django 4.2+ deploy best practices 2025"

        >>> create_version_aware_query("react", "hooks")
        "React hooks best practices 2025"
    """
    if version:
        # 清理版本號
        if version.startswith("=="):
            version_str = version[2:]  # "==0.109.0" → "0.109.0"
        elif version.startswith(">="):
            version_str = version[2:] + "+"  # ">=4.2" → "4.2+"
        elif version.startswith("~="):
            version_str = version[2:] + " compatible"
        else:
            version_str = version

        return f"{library.title()} {version_str} {topic} {year}"
    else:
        return f"{library.title()} {topic} {year}"
```

#### 整合流程

```python
def extract_version_aware_queries(
    session_intent: List[str],
    breadcrumbs: List[str],
    libraries: List[str],
    max_queries: int = 3
) -> List[str]:
    """
    提取版本感知的搜尋查詢

    Steps:
    1. 從 breadcrumbs 提取版本號
    2. 從 session intent 提取主題
    3. 結合 library + version + topic 生成查詢
    """
    from context7_integration import extract_version_from_breadcrumbs

    # Step 1: 提取版本
    versions = extract_version_from_breadcrumbs(breadcrumbs)

    # Step 2: 提取主題 (重用現有邏輯)
    queries = []

    # ... (整合現有 extract_search_queries_from_intent 邏輯)

    return queries
```

---

### Feature 3: 依賴關係搜尋

#### 設計概念

自動搜尋依賴框架的相關文檔：

```python
# 範例：使用者只提到 Redux
detected_libraries = ["redux"]

# Step 1: 補充依賴
enriched = enrich_libraries_with_dependencies(detected_libraries)
# → ["react", "redux"]

# Step 2: 搜尋兩個框架
queries = [
    "React hooks best practices 2025",           # 依賴
    "Redux state management best practices 2025"  # 原始
]

# 效果：使用者獲得完整的 React + Redux 生態系統文檔
```

#### 實作函數

```python
def create_ecosystem_search_queries(
    libraries: List[str],
    session_intent: List[str],
    max_queries: int = 3
) -> List[Dict[str, Any]]:
    """
    建立生態系統完整的搜尋查詢

    Args:
        libraries: 偵測到的框架
        session_intent: 使用者意圖
        max_queries: 最大查詢數

    Returns:
        List of query objects with metadata
        [
            {
                "query": "React hooks best practices 2025",
                "library": "react",
                "is_dependency": True,
                "parent_library": "redux"
            },
            {
                "query": "Redux state management 2025",
                "library": "redux",
                "is_dependency": False
            }
        ]
    """
    from context7_integration import (
        enrich_libraries_with_dependencies,
        get_framework_dependencies
    )

    # Step 1: 補充依賴
    enriched_libraries = enrich_libraries_with_dependencies(libraries)

    # Step 2: 標記依賴關係
    queries = []
    original_set = set(libraries)

    for lib in enriched_libraries:
        is_dependency = lib not in original_set
        parent = None

        if is_dependency:
            # 找出是誰的依賴
            for orig_lib in libraries:
                deps = get_framework_dependencies(orig_lib)
                if lib in deps:
                    parent = orig_lib
                    break

        # Step 3: 建立查詢
        topic = extract_topic_from_intent(session_intent, lib)
        query = f"{lib.title()} {topic} best practices 2025"

        queries.append({
            "query": query,
            "library": lib,
            "is_dependency": is_dependency,
            "parent_library": parent
        })

        if len(queries) >= max_queries:
            break

    return queries
```

---

## 🧪 測試策略

### Test Suite 設計

```python
# test_p1_5_exa_optimization.py

def test_feature_1_priority_search():
    """測試優先級搜尋分配"""
    libraries = ["react", "redux", "alpine"]
    allocations = allocate_search_budget_by_priority(libraries, 300)

    # 驗證
    assert allocations["react"]["num_results"] >= allocations["redux"]["num_results"]
    assert allocations["alpine"]["num_results"] == 0  # 跳過低優先級

def test_feature_2_version_aware_query():
    """測試版本感知查詢"""
    query = create_version_aware_query("fastapi", "auth", "==0.109.0")
    assert "0.109.0" in query
    assert "FastAPI" in query

def test_feature_3_ecosystem_search():
    """測試生態系統搜尋"""
    libraries = ["redux"]
    queries = create_ecosystem_search_queries(libraries, [], max_queries=3)

    # 驗證包含 React (依賴)
    lib_names = [q["library"] for q in queries]
    assert "react" in lib_names
    assert "redux" in lib_names
```

---

## 📈 預期改進效果

### Token 效率提升

```
# 範例：偵測到 React, Redux, Alpine, Unknown-lib
當前 (P1-3):
- React: 75 tokens (1 result)
- Redux: 75 tokens (1 result)
- Alpine: 75 tokens (1 result)
- Unknown: 75 tokens (1 result)
Total: 300 tokens, 4 results

P1-5 優化:
- React: 158 tokens (2 results) ← 高優先級
- Redux: 126 tokens (1 result) ← 重要
- Unknown: 16 tokens (跳過)
- Alpine: 0 tokens (跳過) ← 低優先級
Total: 300 tokens, 3 results

結果: 相同 Token，更相關的結果！
```

### 文檔準確性提升

```
# 版本感知查詢
當前 (P1-3):
Query: "FastAPI authentication best practices 2025"
Result: FastAPI 0.95.0 文檔 (不匹配使用者的 0.109.0)

P1-5 優化:
Query: "FastAPI 0.109.0 authentication best practices 2025"
Result: FastAPI 0.109.0 特定版本文檔
準確度: +15%
```

### 文檔完整性提升

```
# 依賴關係搜尋
當前 (P1-3):
Detected: ["redux"]
Searches: ["Redux state management 2025"]
Result: Redux 文檔（缺少 React 上下文）

P1-5 優化:
Detected: ["redux"]
Enriched: ["react", "redux"]
Searches: [
    "React hooks best practices 2025",
    "Redux state management 2025"
]
Result: 完整的 React + Redux 生態系統文檔
連貫性: +25%
```

---

## 🎯 實作優先順序

### Phase 1: 核心功能 (2-3 小時)

1. ✅ 實作 `allocate_search_budget_by_priority()`
2. ✅ 實作 `create_version_aware_query()`
3. ✅ 實作 `create_ecosystem_search_queries()`

### Phase 2: 整合與測試 (1-2 小時)

4. ✅ 修改 `enhance_with_exa()` 整合三個功能
5. ✅ 建立完整測試套件
6. ✅ 執行測試驗證

### Phase 3: 文檔與部署 (1 小時)

7. ✅ 生成完整報告
8. ✅ Git commit 與推送
9. ✅ 更新 P1-3 整合計畫

---

## 📁 檔案結構

```
project-template/
├── integrations/
│   ├── context7_integration.py  # P1-4.2 (已完成)
│   └── exa_integration.py       # P1-5 (待優化)
├── P1-5_EXA_OPTIMIZATION_PLAN.md      # 本文件
└── P1-5_EXA_OPTIMIZATION_REPORT.md    # 待生成
test_p1_5_exa_optimization.py          # 測試套件
```

---

## 🔄 與 P1-4.2 的關係

P1-5 完全基於 P1-4.2 的成果：

| P1-4.2 功能 | P1-5 應用 |
|------------|----------|
| `FRAMEWORK_PRIORITY` | 優先級搜尋分配 |
| `extract_version_from_breadcrumbs()` | 版本感知查詢 |
| `FRAMEWORK_DEPENDENCIES` | 依賴關係搜尋 |
| `enrich_libraries_with_dependencies()` | 生態系統完整搜尋 |

**設計哲學**: 複用現有功能，避免重複實作

---

## ✅ 成功指標

| 指標 | 目標 | 驗證方式 |
|------|------|---------|
| Token 效率 | +40% | 測試案例比較 |
| 文檔相關性 | 90%+ | 手動檢查搜尋結果 |
| 測試通過率 | 100% | pytest 完整測試套件 |
| 程式碼品質 | 無警告 | Linter 檢查 |

---

**下一步**: 開始實作 Phase 1 核心功能

---

*Generated with [Claude Code](https://claude.com/claude-code)*
