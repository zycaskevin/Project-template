# 小憶的記憶交接功能設計

**設計日期**: 2025-11-16
**分析方法**: Exa + Context7 + 多專家協作思維樹
**核心問題**: 如何讓小憶利用壓縮機制實現 TODO 與文檔化的記憶交接？

---

## 🌳 多專家協作思維樹分析

### 問題分解：三個層級需要調整

```
小憶的記憶交接功能
├─ 層級 1: Agent 層 (xiaoji-memory-keeper.md)
│  └─ 問題: 小憶如何「知道」何時壓縮與交接？
│
├─ 層級 2: Output Style 層 (tdd-multi-expert-zh.md)
│  └─ 問題: 輸出風格如何觸發小憶的記憶功能？
│
└─ 層級 3: Plugin/Integration 層
   └─ 問題: 壓縮腳本如何與 EvoMem/Context7/Exa 整合？
```

---

## 🔍 專家 1: 架構師視角 - 系統層級分析

### 當前系統架構（As-Is）

```
┌─────────────────────────────────────────────────┐
│  對話進行中 (Token 累積)                         │
└───────────────┬─────────────────────────────────┘
                │
                ▼
        Token 達 70-80%？
                │
                ├─ No → 繼續對話
                │
                └─ Yes → 手動觸發壓縮
                         │
                         ▼
                ┌────────────────────────┐
                │  compress_context.py   │
                │  (Factory.ai 2025)     │
                └───────────┬────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │  compressed.json       │
                │  - sessionIntent       │
                │  - playByPlay          │
                │  - artifacts           │
                │  - breadcrumbs         │
                └────────────────────────┘
```

**問題**:
- ❌ 小憶沒有參與壓縮過程
- ❌ 沒有記憶存儲機制
- ❌ 沒有 TODO 追蹤
- ❌ 沒有文檔化流程

---

### 理想系統架構（To-Be）

```
┌─────────────────────────────────────────────────┐
│  對話進行中 (Token 累積)                         │
│  - 小憶持續監控 Token 使用                        │
│  - 小憶自動提取關鍵資訊                           │
└───────────────┬─────────────────────────────────┘
                │
                ▼
        Token 達 70%？
                │
                └─ Yes → 🧠 小憶自動觸發
                         │
                         ▼
                ┌────────────────────────────────┐
                │  小憶記憶交接流程 (5 Steps)     │
                │                                │
                │  Step 1: 提取關鍵資訊          │
                │  Step 2: 壓縮上下文            │
                │  Step 3: 增強搜尋 (Exa+C7)     │
                │  Step 4: 存入 EvoMem           │
                │  Step 5: 生成交接文檔          │
                └───────────┬────────────────────┘
                            │
                            ▼
                ┌────────────────────────────────┐
                │  Enhanced Handoff Package      │
                │                                │
                │  1. compressed.json (325 T)    │
                │  2. context7_docs.json (500 T) │
                │  3. exa_insights.json (300 T)  │
                │  4. evomem_memory.json (∞)     │
                │  5. TODO_NEXT.md              │
                │  6. HANDOFF_DOC.md            │
                └────────────────────────────────┘
```

---

## 🔍 專家 2: 系統設計師 - 層級調整分析

### 分析：哪個層級需要調整？

#### 選項 A: 只調整 Agent 層 (xiaoji-memory-keeper.md)

**優點**:
- ✅ 最小改動
- ✅ 其他層級不受影響

**缺點**:
- ❌ 小憶無法「自動」觸發（需要用戶召喚）
- ❌ 缺少系統級整合

**評分**: 🟡 **5/10** (不足)

---

#### 選項 B: 調整 Output Style 層

**優點**:
- ✅ 可在 Token 達閾值時自動觸發小憶
- ✅ 與現有 TDD 流程整合

**缺點**:
- ❌ Output Style 不應處理記憶邏輯（職責混淆）
- ❌ 違反單一職責原則

**評分**: 🟡 **6/10** (可行但不理想)

---

#### 選項 C: 新增 Plugin 層 (memory-handoff-plugin)

**優點**:
- ✅ 符合插件架構
- ✅ 可獨立開發與測試
- ✅ 可選擇性啟用

**缺點**:
- ❌ 需要新增 Plugin 基礎設施
- ❌ 較大改動

**評分**: 🟢 **8/10** (推薦)

---

#### 選項 D: 混合方案（推薦）⭐

**設計**:
```
1. Agent 層 (小憶)
   - 定義記憶交接協議
   - 實作 5-Step 流程

2. Integration 層 (新增 memory_handoff_integration.py)
   - 整合壓縮、Exa、Context7、EvoMem
   - 自動化流程編排

3. Output Style 層 (最小改動)
   - 只在 Token 監控章節新增小憶觸發提示
   - 不改變核心邏輯

4. Hook 層 (新增)
   - 在 Token 達 70% 時自動觸發小憶
   - 完全自動化
```

**優點**:
- ✅ 清晰的職責分離
- ✅ 可完全自動化
- ✅ 可獨立測試
- ✅ 最佳架構

**評分**: 🟢 **9/10** (最推薦)

---

## 🔍 專家 3: 資料工程師 - 記憶存儲設計

### 小憶的記憶存儲架構

#### 兩層記憶系統

```
┌─────────────────────────────────────────────────┐
│  Layer 1: 短期記憶 (Session Memory)             │
│  - 當前對話上下文                                │
│  - TODO 列表                                    │
│  - 臨時決策                                     │
│  - 壽命: 單次對話                                │
│  - 存儲: compressed.json                        │
└─────────────────────────────────────────────────┘
                    │ 壓縮 & 提取
                    ▼
┌─────────────────────────────────────────────────┐
│  Layer 2: 長期記憶 (EvoMem)                     │
│  - 跨對話知識                                   │
│  - 歷史決策模式                                  │
│  - Bug 修復記錄                                 │
│  - 最佳實踐                                     │
│  - 壽命: 永久 (向量資料庫)                       │
│  - 存儲: ChromaDB + Metadata                   │
└─────────────────────────────────────────────────┘
```

---

### 記憶項目結構 (Memory Item Schema)

```json
{
  "id": "mem_20251116_001",
  "type": "handoff",
  "timestamp": "2025-11-16T17:30:00Z",
  "from_agent": "general",
  "to_agent": "xiaoji",

  "session_memory": {
    "sessionIntent": ["實作 P1-4.2 三大功能"],
    "playByPlay": [
      "實作框架優先級權重系統",
      "實作版本號偵測",
      "實作依賴關係圖"
    ],
    "artifacts": [
      "project-template/integrations/context7_integration.py",
      "test_p1_4_2_features.py",
      "P1-4.2_PRIORITY_VERSION_DEPENDENCIES_REPORT.md"
    ],
    "breadcrumbs": [
      "function:sort_libraries_by_priority",
      "function:extract_version_from_breadcrumbs",
      "function:enrich_libraries_with_dependencies"
    ],
    "todos": [
      {"status": "completed", "task": "實作優先級系統"},
      {"status": "completed", "task": "實作版本偵測"},
      {"status": "completed", "task": "實作依賴關係"}
    ],
    "decisions": [
      {
        "decision": "使用 5 層權重系統 (10/7-8/5-6/3/1)",
        "rationale": "平衡重要性與靈活性",
        "alternatives_considered": ["3 層", "動態權重"],
        "source": "P1-4.2 設計"
      }
    ]
  },

  "long_term_memory": {
    "learnings": [
      {
        "pattern": "框架優先級分配 Token",
        "context": "當 Token 預算有限時",
        "solution": "按權重分配，低優先級跳過",
        "effectiveness": "Token 效率 +10%"
      }
    ],
    "best_practices": [
      "版本感知查詢提升文檔準確性 +15%",
      "依賴關係補充提升連貫性 +20%"
    ],
    "bugs_fixed": [],
    "code_patterns": [
      {
        "pattern": "sort_by_priority_then_allocate",
        "use_case": "資源有限時的優先級分配",
        "code_ref": "context7_integration.py:361-393"
      }
    ]
  },

  "enhancements": {
    "context7_docs": {
      "libraries": ["react", "fastapi", "redux"],
      "tokens_added": 500,
      "relevance_score": 0.92
    },
    "exa_insights": {
      "queries": [
        "React 18 best practices 2025",
        "FastAPI 0.109.0 authentication"
      ],
      "tokens_added": 300,
      "relevance_score": 0.88
    }
  },

  "metadata": {
    "project": "專案啟動文檔專案",
    "phase": "P1-4.2",
    "token_before": 82234,
    "token_after": 4521,
    "compression_ratio": 0.945,
    "quality_score": 9.5
  }
}
```

---

## 🔍 專家 4: 流程設計師 - 小憶的 5-Step 流程

### Step 1: 自動觸發檢測

```python
# memory_handoff_integration.py

class MemoryHandoffTrigger:
    """自動偵測並觸發小憶的記憶交接"""

    TRIGGER_THRESHOLDS = {
        "token_usage": 0.70,        # 70% Token 使用
        "todo_completed": 5,        # 完成 5 個 TODO
        "time_elapsed": 3600,       # 1 小時經過
        "phase_completed": True,    # 階段完成 (如 TDD Red)
        "git_commits": 3            # 3 次 commit
    }

    def should_trigger_handoff(self, context: Dict) -> bool:
        """判斷是否應該觸發記憶交接"""
        triggers = []

        # Check 1: Token 使用率
        token_ratio = context['current_tokens'] / context['max_tokens']
        if token_ratio >= self.TRIGGER_THRESHOLDS['token_usage']:
            triggers.append('token_usage')

        # Check 2: TODO 完成數
        completed_todos = len([t for t in context['todos']
                              if t['status'] == 'completed'])
        if completed_todos >= self.TRIGGER_THRESHOLDS['todo_completed']:
            triggers.append('todo_completed')

        # Check 3: 階段完成
        if context.get('phase_completed'):
            triggers.append('phase_completed')

        # 任一觸發條件滿足即觸發
        return len(triggers) > 0, triggers
```

---

### Step 2: 提取關鍵資訊

```python
def extract_key_information(self, conversation: str) -> Dict:
    """從對話中提取關鍵資訊"""

    # 使用現有的 compress_context.py
    from compress_context import ContextCompressor

    compressor = ContextCompressor()
    compressed = compressor.compress(conversation)

    # 額外提取
    extracted = {
        **compressed,
        "todos": self._extract_todos(conversation),
        "decisions": self._extract_decisions(conversation),
        "code_patterns": self._extract_code_patterns(compressed['breadcrumbs']),
        "learnings": self._extract_learnings(compressed['playByPlay'])
    }

    return extracted
```

---

### Step 3: 增強搜尋 (Context7 + Exa)

```python
def enhance_with_search(self, compressed: Dict) -> Dict:
    """使用 Context7 和 Exa 增強壓縮內容"""

    from context7_integration import enhance_with_context7
    from exa_integration import enhance_with_exa

    # Step 3.1: Context7 文檔增強
    enhanced = enhance_with_context7(
        compressed,
        use_mcp=True,
        max_tokens=500
    )

    # Step 3.2: Exa 最佳實踐增強
    enhanced = enhance_with_exa(
        enhanced,
        use_api=False,  # 使用 Mock
        max_tokens=300
    )

    return enhanced
```

---

### Step 4: 存入 EvoMem (長期記憶)

```python
def store_in_evomem(self, memory_item: Dict) -> str:
    """存入 EvoMem 長期記憶"""

    # TODO: 整合 EvoMem
    # from evomem import IntelligentMemorySystem

    # memory = IntelligentMemorySystem()
    # memory_id = memory.add_memory(
    #     content=self._format_for_storage(memory_item),
    #     metadata={
    #         "type": "handoff",
    #         "project": memory_item['metadata']['project'],
    #         "phase": memory_item['metadata']['phase'],
    #         "tags": self._extract_tags(memory_item)
    #     }
    # )

    # 暫時存成 JSON
    import json
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"memory_handoff_{timestamp}.json"

    with open(f"data/memory/{filename}", 'w', encoding='utf-8') as f:
        json.dump(memory_item, f, indent=2, ensure_ascii=False)

    return filename
```

---

### Step 5: 生成交接文檔

```python
def generate_handoff_doc(self, memory_item: Dict) -> str:
    """生成人類可讀的交接文檔"""

    doc = f"""# 記憶交接文檔

**時間**: {memory_item['timestamp']}
**從**: {memory_item['from_agent']}
**到**: {memory_item['to_agent']}
**專案**: {memory_item['metadata']['project']}
**階段**: {memory_item['metadata']['phase']}

---

## 📋 任務摘要

**任務目標**:
{chr(10).join([f"- {intent}" for intent in memory_item['session_memory']['sessionIntent']])}

**完成事項**:
{chr(10).join([f"- ✅ {action}" for action in memory_item['session_memory']['playByPlay']])}

---

## 📁 產出物

**檔案**:
{chr(10).join([f"- [{artifact}]({artifact})" for artifact in memory_item['session_memory']['artifacts']])}

---

## 🔑 關鍵決策

{self._format_decisions(memory_item['session_memory']['decisions'])}

---

## 💡 學習與洞察

{self._format_learnings(memory_item['long_term_memory']['learnings'])}

---

## 📊 效能指標

- **Token 壓縮**: {memory_item['metadata']['token_before']} → {memory_item['metadata']['token_after']} ({memory_item['metadata']['compression_ratio'] * 100:.1f}% 壓縮)
- **品質評分**: {memory_item['metadata']['quality_score']}/10

---

## 🎯 下一步建議

{self._generate_next_steps(memory_item)}

---

*自動生成於 {memory_item['timestamp']} by 小憶 (Memory Keeper)*
"""

    # 存檔
    filename = f"HANDOFF_{memory_item['metadata']['phase']}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(doc)

    return filename
```

---

## 🔍 專家 5: 整合工程師 - 實際整合方案

### 完整整合架構

```python
# memory_handoff_integration.py (新檔案)

class MemoryHandoffOrchestrator:
    """小憶的記憶交接編排器"""

    def __init__(self):
        self.trigger = MemoryHandoffTrigger()
        self.compressor = ContextCompressor()
        self.enhancer = SearchEnhancer()
        self.storage = MemoryStorage()
        self.documenter = HandoffDocumenter()

    def execute_handoff(self,
                       conversation: str,
                       current_tokens: int,
                       max_tokens: int,
                       todos: List[Dict],
                       metadata: Dict) -> Dict:
        """
        執行完整的記憶交接流程

        Returns:
            {
                "compressed": {...},
                "enhanced": {...},
                "memory_id": "mem_xxx",
                "handoff_doc": "HANDOFF_xxx.md",
                "todo_next": "TODO_NEXT.md",
                "success": True
            }
        """

        # Step 1: 檢查觸發條件
        should_trigger, reasons = self.trigger.should_trigger_handoff({
            'current_tokens': current_tokens,
            'max_tokens': max_tokens,
            'todos': todos,
            'phase_completed': metadata.get('phase_completed', False)
        })

        if not should_trigger:
            return {"success": False, "reason": "No trigger conditions met"}

        print(f"🧠 小憶: 觸發記憶交接 (原因: {', '.join(reasons)})")

        # Step 2: 提取 & 壓縮
        print("📦 Step 2/5: 提取關鍵資訊並壓縮...")
        compressed = self.compressor.compress(conversation)

        # 額外提取
        compressed['todos'] = todos
        compressed['decisions'] = self._extract_decisions(conversation)

        # Step 3: 增強搜尋
        print("🔍 Step 3/5: 使用 Context7 + Exa 增強...")
        enhanced = self.enhancer.enhance(compressed)

        # Step 4: 存入 EvoMem
        print("💾 Step 4/5: 存入 EvoMem 長期記憶...")
        memory_item = self._build_memory_item(
            compressed, enhanced, metadata
        )
        memory_id = self.storage.store(memory_item)

        # Step 5: 生成文檔
        print("📝 Step 5/5: 生成交接文檔...")
        handoff_doc = self.documenter.generate_handoff(memory_item)
        todo_next = self.documenter.generate_todo_next(memory_item)

        print("✅ 記憶交接完成!")
        print(f"   - 壓縮率: {memory_item['metadata']['compression_ratio'] * 100:.1f}%")
        print(f"   - 記憶 ID: {memory_id}")
        print(f"   - 交接文檔: {handoff_doc}")

        return {
            "success": True,
            "compressed": compressed,
            "enhanced": enhanced,
            "memory_id": memory_id,
            "handoff_doc": handoff_doc,
            "todo_next": todo_next,
            "compression_ratio": memory_item['metadata']['compression_ratio']
        }
```

---

## 🔍 專家 6: 使用者體驗設計師 - 觸發方式設計

### 三種觸發方式

#### 方式 1: 自動觸發（推薦）⭐

```python
# 在 output-style 中新增 Token 監控
## 📊 Token 使用監控

**目前使用**: 145,680 / 200,000 tokens (72.8%)
**狀態**: 🟡 建議執行記憶交接

🧠 **小憶建議**: Token 使用已達 72.8%，建議執行記憶交接以：
   - 壓縮當前對話上下文
   - 存入長期記憶 (EvoMem)
   - 生成交接文檔供下次對話參考

**執行方式**:
1. 自動: 我可以立即執行（推薦）
2. 手動: 回覆「執行記憶交接」
```

**優點**:
- ✅ 使用者無感知
- ✅ 完全自動化
- ✅ 不中斷工作流程

---

#### 方式 2: 半自動（建議確認）

```python
# 觸發提示
🧠 **小憶**: 偵測到以下觸發條件:
   - ✓ Token 使用 72.8% (> 70%)
   - ✓ 完成 6 個 TODO (> 5)
   - ✓ 階段完成 (P1-4.2)

**建議執行記憶交接**，是否繼續？
   - 預期壓縮: 145,680 → ~7,000 tokens (95% 壓縮)
   - 生成文檔: HANDOFF_P1-4.2.md, TODO_NEXT.md
   - 存入 EvoMem: 可供未來查詢

[立即執行] [稍後] [不需要]
```

---

#### 方式 3: 手動召喚

```bash
# 使用者主動召喚小憶
User: "小憶，執行記憶交接"

小憶: 收到！開始執行記憶交接流程...
      [執行 5-Step 流程]
      ✅ 完成！已生成 HANDOFF_xxx.md
```

---

## 🔍 專家 7: 品質保證 - 測試策略

### 測試案例設計

```python
# test_memory_handoff.py

def test_trigger_detection():
    """測試觸發條件偵測"""
    trigger = MemoryHandoffTrigger()

    # Case 1: Token 超過 70%
    should, reasons = trigger.should_trigger_handoff({
        'current_tokens': 145000,
        'max_tokens': 200000
    })
    assert should == True
    assert 'token_usage' in reasons

def test_compression_ratio():
    """測試壓縮率"""
    orchestrator = MemoryHandoffOrchestrator()

    conversation = "..." # 長對話
    result = orchestrator.execute_handoff(
        conversation=conversation,
        current_tokens=150000,
        max_tokens=200000,
        todos=[],
        metadata={}
    )

    assert result['compression_ratio'] > 0.90  # 至少 90% 壓縮

def test_evomem_storage():
    """測試 EvoMem 存儲"""
    storage = MemoryStorage()

    memory_item = {...}
    memory_id = storage.store(memory_item)

    # 驗證可以取回
    retrieved = storage.retrieve(memory_id)
    assert retrieved == memory_item
```

---

## 🎯 最終設計建議

### 推薦架構（混合方案 D）

```
層級調整:
├─ 1. Agent 層 (xiaoji-memory-keeper.md)
│  └─ 新增: 5-Step 記憶交接協議定義
│
├─ 2. Integration 層 (新增 memory_handoff_integration.py)
│  └─ 實作: MemoryHandoffOrchestrator 完整流程
│
├─ 3. Output Style 層 (最小改動)
│  └─ 新增: Token 監控章節的小憶觸發提示
│
└─ 4. Hook 層 (可選)
   └─ 新增: 自動觸發 Hook (Token 70% 自動執行)
```

---

### 整合現有系統

```python
# 與現有壓縮機制整合
from compress_context import ContextCompressor          # 已有
from context7_integration import enhance_with_context7  # P1-4.2
from exa_integration import enhance_with_exa           # P1-3

# 新增
from memory_handoff_integration import MemoryHandoffOrchestrator
from evomem_integration import EvoMemStorage  # 待實作

# 完整流程
orchestrator = MemoryHandoffOrchestrator()
result = orchestrator.execute_handoff(...)
```

---

## 📊 實作優先級

### Phase 1: 核心功能 (6-8 小時)

1. **實作 MemoryHandoffOrchestrator** (3 小時)
   - 5-Step 流程
   - 觸發檢測
   - 文檔生成

2. **整合現有系統** (2 小時)
   - compress_context.py
   - context7_integration.py
   - exa_integration.py

3. **測試驗證** (2 小時)
   - 單元測試
   - 整合測試

### Phase 2: EvoMem 整合 (4-6 小時)

4. **實作 EvoMemStorage** (3 小時)
   - 長期記憶存儲
   - 向量檢索

5. **小憶 Agent 串接** (2 小時)
   - Agent 定義更新
   - API 實作

### Phase 3: 自動化與優化 (2-3 小時)

6. **自動觸發 Hook** (1 小時)
7. **Output Style 整合** (1 小時)
8. **效能優化** (1 小時)

---

## ✅ 結論

### 核心設計決策

1. **層級調整**: 混合方案 D（最佳架構）
   - Agent 層: 協議定義
   - Integration 層: 核心實作
   - Output Style: 最小改動
   - Hook 層: 自動觸發

2. **觸發方式**: 半自動（建議確認）
   - Token 70% 自動提示
   - 使用者確認後執行
   - 可選完全自動

3. **整合方式**: 充分複用現有系統
   - compress_context.py ✓
   - context7_integration.py (P1-4.2) ✓
   - exa_integration.py (P1-3) ✓
   - EvoMem (待整合)

---

### 下一步行動

**建議**: 立即實作 Phase 1 (核心功能)

**理由**:
- 可獨立於 EvoMem 運作
- 立即提供價值（壓縮 + 文檔）
- 為 EvoMem 整合打好基礎

---

*Generated with [Claude Code](https://claude.com/claude-code)*
*Analysis Method: Exa + Context7 + Multi-Expert Collaboration Tree*
