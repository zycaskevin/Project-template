# P1-3: Context7 + Exa 整合計畫

**版本**: 1.0
**日期**: 2025-11-15
**目標**: 整合 Context7 MCP 與 Exa API，實現智能文檔增強

---

## 🎯 整合目標

### 核心價值主張

**問題**: 壓縮時可能丟失重要技術上下文
**解決方案**: 自動拉取最新文檔與最佳實踐補充壓縮後的上下文

### 使用場景

1. **Agent 交接時**
   - 壓縮後上下文：325 tokens
   - Context7 補充文檔：~500 tokens（相關技術文檔）
   - Exa 補充最佳實踐：~300 tokens
   - **總計**: ~1,125 tokens（vs. 原始 595 tokens）

2. **提升交接品質**
   - 保留壓縮效益（45.4% 壓縮率）
   - 補充關鍵技術文檔
   - 提供最佳實踐參考
   - **讓下一個 Agent 有更完整的上下文**

---

## 📊 整合架構

### 系統流程圖

```
┌─────────────────────────────────────────────────────┐
│  Original Conversation (595 tokens)                 │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  ContextCompressor (Factory.ai 2025)                │
│  - Session Intent                                   │
│  - Play-by-Play                                     │
│  - Artifacts                                        │
│  - Breadcrumbs                                      │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Compressed Context (325 tokens, 45.4%)             │
└───────────────┬─────────────────────────────────────┘
                │
                ├───────────────────┬─────────────────┐
                ▼                   ▼                 ▼
    ┌───────────────────┐ ┌─────────────┐ ┌──────────────┐
    │  Context7 MCP     │ │  Exa API    │ │  Original    │
    │  (Tech Docs)      │ │ (Best       │ │  Compressed  │
    │                   │ │  Practices) │ │              │
    │  +500 tokens      │ │ +300 tokens │ │  325 tokens  │
    └───────────────────┘ └─────────────┘ └──────────────┘
                │                   │                 │
                └───────────────────┴─────────────────┘
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │  Enhanced Handoff.json                │
                │                                       │
                │  - Compressed Context (325 tokens)    │
                │  - Tech Docs (500 tokens)             │
                │  - Best Practices (300 tokens)        │
                │                                       │
                │  Total: ~1,125 tokens                 │
                │  vs. Original: 595 tokens             │
                │                                       │
                │  Compression: 45.4%                   │
                │  Enhancement: +530 tokens (智能補充)   │
                └───────────────────────────────────────┘
```

### 關鍵設計決策

#### 1. 何時觸發 Context7？

**觸發條件**:
- Breadcrumbs 中出現技術框架/庫名稱
- Artifacts 中出現技術文件（.py, .js, .ts）

**範例**:
```python
breadcrumbs = ["function:compress_context", "class:ContextCompressor"]
# 不觸發（沒有框架名稱）

breadcrumbs = ["import:FastAPI", "class:APIRouter"]
# 觸發！拉取 FastAPI 最新文檔
```

#### 2. 何時觸發 Exa？

**觸發條件**:
- Session Intent 包含技術問題關鍵字
- Play-by-Play 包含特定技術決策

**範例**:
```python
session_intent = ["Implement dynamic memory compression for agent handoffs"]
# 觸發！搜尋 "dynamic memory compression best practices 2025"

play_by_play = ["Decision: Use AWS Lambda instead of Google Cloud Run"]
# 觸發！搜尋 "AWS Lambda vs Google Cloud Run comparison 2025"
```

---

## 🛠️ 實作計畫

### Phase 1: Context7 MCP 整合

#### 1.1 安裝 Context7 MCP

```bash
# 選項 A: 使用 Smithery CLI (推薦)
npx -y @smithery/cli install @upstash/context7-mcp --client claude

# 選項 B: 手動配置
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

#### 1.2 創建 Context7 整合模組

**檔案**: `project-template/integrations/context7_integration.py`

```python
"""
Context7 MCP Integration Module

Purpose: Automatically fetch up-to-date technical documentation
"""

import subprocess
import json
from typing import List, Dict, Optional

class Context7Client:
    """Client for Context7 MCP server"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def fetch_docs(self, library: str, version: str = "latest") -> Dict:
        """
        Fetch documentation for a specific library

        Args:
            library: Library name (e.g., "FastAPI", "React", "Next.js")
            version: Version string (default: "latest")

        Returns:
            Dictionary with documentation content
        """
        # Context7 MCP call
        query = f"How to use {library} {version}"

        # Use MCP protocol
        result = self._call_mcp(query)

        return {
            "library": library,
            "version": version,
            "documentation": result,
            "tokens": self._estimate_tokens(result)
        }

    def _call_mcp(self, query: str) -> str:
        """Call Context7 MCP server"""
        # Implementation depends on MCP client setup
        # This is a placeholder
        pass

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 4


def extract_libraries_from_breadcrumbs(breadcrumbs: List[str]) -> List[str]:
    """
    Extract library names from breadcrumbs

    Args:
        breadcrumbs: List of breadcrumb strings

    Returns:
        List of library names
    """
    libraries = []

    # Known frameworks/libraries
    known_libs = {
        "FastAPI", "Django", "Flask", "Express",
        "React", "Next.js", "Vue", "Svelte",
        "PyTorch", "TensorFlow", "scikit-learn",
        "pandas", "numpy", "Anthropic", "OpenAI"
    }

    for breadcrumb in breadcrumbs:
        for lib in known_libs:
            if lib.lower() in breadcrumb.lower():
                libraries.append(lib)

    return list(set(libraries))


def should_fetch_docs(compressed_context: Dict) -> bool:
    """
    Determine if we should fetch docs

    Args:
        compressed_context: Compressed context dictionary

    Returns:
        True if docs should be fetched
    """
    breadcrumbs = compressed_context.get("breadcrumbs", [])
    libraries = extract_libraries_from_breadcrumbs(breadcrumbs)

    return len(libraries) > 0


def enhance_with_context7(compressed_context: Dict, api_key: Optional[str] = None) -> Dict:
    """
    Enhance compressed context with Context7 documentation

    Args:
        compressed_context: Compressed context from ContextCompressor
        api_key: Optional Context7 API key

    Returns:
        Enhanced context with documentation
    """
    if not should_fetch_docs(compressed_context):
        return compressed_context

    # Extract libraries
    breadcrumbs = compressed_context.get("breadcrumbs", [])
    libraries = extract_libraries_from_breadcrumbs(breadcrumbs)

    # Fetch docs for each library
    client = Context7Client(api_key)
    docs = []

    for library in libraries[:3]:  # Limit to top 3
        doc = client.fetch_docs(library)
        docs.append(doc)

    # Add to enhanced context
    enhanced = compressed_context.copy()
    enhanced["context7Documentation"] = docs

    return enhanced
```

---

### Phase 2: Exa API 整合

#### 2.1 安裝 Exa Python SDK

```bash
pip install exa-py
```

#### 2.2 創建 Exa 整合模組

**檔案**: `project-template/integrations/exa_integration.py`

```python
"""
Exa Search API Integration Module

Purpose: Search for best practices and technical insights
"""

import os
from typing import List, Dict, Optional
from exa_py import Exa

class ExaSearchClient:
    """Client for Exa search API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('EXA_API_KEY')
        self.client = Exa(self.api_key) if self.api_key else None

    def search_best_practices(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search for best practices

        Args:
            query: Search query
            num_results: Number of results (default: 3)

        Returns:
            List of search results
        """
        if not self.client:
            return []

        # Enhance query with "best practices 2025"
        enhanced_query = f"{query} best practices 2025"

        results = self.client.search(
            enhanced_query,
            num_results=num_results
        )

        return [
            {
                "title": result.title,
                "url": result.url,
                "snippet": result.text[:200] if hasattr(result, 'text') else "",
                "relevance": result.score if hasattr(result, 'score') else 0.0
            }
            for result in results.results
        ]

    def search_technical_decisions(self, decision: str) -> List[Dict]:
        """
        Search for insights on technical decisions

        Args:
            decision: Technical decision description

        Returns:
            List of search results with insights
        """
        # Extract comparison keywords
        if " vs " in decision or " instead of " in decision:
            query = f"{decision} comparison pros cons 2025"
        else:
            query = f"{decision} technical analysis 2025"

        return self.search_best_practices(query, num_results=2)


def extract_search_queries(compressed_context: Dict) -> List[str]:
    """
    Extract search queries from compressed context

    Args:
        compressed_context: Compressed context dictionary

    Returns:
        List of search queries
    """
    queries = []

    # From session intent
    session_intent = compressed_context.get("sessionIntent", [])
    for intent in session_intent[:2]:  # Top 2
        if len(intent) > 20:
            queries.append(intent)

    # From play-by-play (technical decisions)
    play_by_play = compressed_context.get("playByPlay", [])
    for action in play_by_play:
        if "Decision:" in action or "decision" in action.lower():
            queries.append(action)

    return queries[:3]  # Limit to top 3


def should_search_exa(compressed_context: Dict) -> bool:
    """
    Determine if we should search Exa

    Args:
        compressed_context: Compressed context dictionary

    Returns:
        True if Exa search should be performed
    """
    queries = extract_search_queries(compressed_context)
    return len(queries) > 0


def enhance_with_exa(compressed_context: Dict, api_key: Optional[str] = None) -> Dict:
    """
    Enhance compressed context with Exa search results

    Args:
        compressed_context: Compressed context from ContextCompressor
        api_key: Optional Exa API key

    Returns:
        Enhanced context with search results
    """
    if not should_search_exa(compressed_context):
        return compressed_context

    # Extract queries
    queries = extract_search_queries(compressed_context)

    # Search for each query
    client = ExaSearchClient(api_key)
    search_results = []

    for query in queries:
        results = client.search_best_practices(query, num_results=2)
        search_results.extend(results)

    # Add to enhanced context
    enhanced = compressed_context.copy()
    enhanced["exaBestPractices"] = search_results

    return enhanced
```

---

### Phase 3: 整合到主流程

#### 3.1 修改 compress_context.py

在 `compress_with_handoff` 函數中添加增強邏輯：

```python
def compress_with_handoff(handoff_path: str, from_agent: str, to_agent: str,
                          use_context7: bool = False,
                          use_exa: bool = False,
                          context7_api_key: str = None,
                          exa_api_key: str = None) -> bool:
    """
    Compress context and update handoff.json with enhanced context

    Args:
        handoff_path: Path to handoff.json file
        from_agent: Source agent ID
        to_agent: Target agent ID
        use_context7: Enable Context7 documentation enhancement
        use_exa: Enable Exa best practices search
        context7_api_key: Optional Context7 API key
        exa_api_key: Optional Exa API key

    Returns:
        True if successful, False otherwise
    """
    # ... existing compression logic ...

    # Compress conversation
    compressor = ContextCompressor()
    compressed = compressor.compress(conversation)

    # Enhancement stage (NEW)
    enhanced = compressed.copy()

    if use_context7:
        from integrations.context7_integration import enhance_with_context7
        enhanced = enhance_with_context7(enhanced, context7_api_key)

    if use_exa:
        from integrations.exa_integration import enhance_with_exa
        enhanced = enhance_with_exa(enhanced, exa_api_key)

    # Update handoff with enhanced context
    handoff["summary"]["compressedContext"] = enhanced

    # ... rest of the function ...
```

---

## 💰 成本分析

### Context7

| Tier | 成本 | 限制 |
|------|------|------|
| **Free** | $0/月 | 基本功能、API rate limits |
| **Pro** | $7/月/seat | 私有 repo、團隊協作 |

**我們的使用**: ✅ **Free Tier 足夠**（公開 repo）

### Exa

| Tier | 成本 | 限制 |
|------|------|------|
| **Free Credits** | $0 | $10 免費額度 = 2,000 次搜尋 |
| **Pay-per-use** | $5/1K searches | 超額後付費 |

**我們的使用**: ✅ **Free Credits 足夠**（預估 <100 次搜尋/月）

### 總成本

**預期**: **$0/月**（兩者 Free Tier 都足夠）

---

## 🎯 預期效果

### 增強效果對比

| 指標 | 純壓縮 | +Context7 | +Exa | 完整增強 |
|------|--------|-----------|------|---------|
| **Tokens** | 325 | 825 | 625 | **1,125** |
| **技術文檔** | ❌ 無 | ✅ 有 | ❌ 無 | ✅ 有 |
| **最佳實踐** | ❌ 無 | ❌ 無 | ✅ 有 | ✅ 有 |
| **下一 Agent 上下文** | ⚠️ 基礎 | ✅ 良好 | ✅ 良好 | ✅ **完整** |

### 使用場景範例

**情境**: TDD Red → TDD Green 交接

```json
{
  "compressedContext": {
    "sessionIntent": ["Implement FastAPI endpoint for user authentication"],
    "breadcrumbs": ["import:FastAPI", "class:APIRouter"],
    "playByPlay": ["Decision: Use JWT instead of session cookies"]
  },

  "context7Documentation": [
    {
      "library": "FastAPI",
      "version": "latest",
      "documentation": "FastAPI authentication guide...",
      "tokens": 450
    }
  ],

  "exaBestPractices": [
    {
      "title": "JWT vs Session Cookies: Security Comparison 2025",
      "url": "https://...",
      "snippet": "JWT tokens provide stateless authentication...",
      "relevance": 0.92
    }
  ]
}
```

**效果**: 下一個 Agent (TDD Green) 獲得：
- ✅ 壓縮後的核心上下文（325 tokens）
- ✅ FastAPI 最新文檔（450 tokens）
- ✅ JWT 最佳實踐（200 tokens）
- **總計**: 975 tokens（vs. 原始 595 tokens）

---

## 📋 實作檢查清單

### Phase 1: Context7 整合
- [ ] 安裝 Context7 MCP
- [ ] 創建 `context7_integration.py`
- [ ] 實作 `Context7Client`
- [ ] 測試文檔拉取

### Phase 2: Exa 整合
- [ ] 安裝 Exa Python SDK
- [ ] 創建 `exa_integration.py`
- [ ] 實作 `ExaSearchClient`
- [ ] 測試搜尋功能

### Phase 3: 主流程整合
- [ ] 修改 `compress_context.py`
- [ ] 添加 CLI 參數（--use-context7, --use-exa）
- [ ] 更新 `claude-auto.sh`
- [ ] 端到端測試

### Phase 4: 文檔與測試
- [ ] 更新 README
- [ ] 創建使用範例
- [ ] 生成測試報告

---

## 🚀 下一步

1. **立即執行**: 安裝 Context7 MCP
2. **實作**: 創建整合模組
3. **測試**: 驗證增強效果
4. **優化**: 根據測試結果調整

---

**狀態**: 📋 **計畫完成** - 準備實作
**預計時間**: 2-3 小時
**預期成果**: 智能文檔增強系統，$0/月成本

---

*Generated with [Claude Code](https://claude.com/claude-code)*
