# Workspace Specification

**Version**: 4.0
**Type**: Meta-Specification
**Usage**: Read by LLM to generate project-specific CLAUDE.md

---

## 第 1 節 Core Protocols

### 1.1 Agent Handoff Protocol

**Rule**: All agent handoffs MUST use JSON Schema

```yaml
Schema: C:\Users\User\.claude\schemas\handoff-v1.json
Fields:
  - schemaVersion: "1.0.0"
  - from: {agentType, timestamp}
  - to: {agentType, requiredContext}
  - summary: {keyFindings, decisions}
  - artifacts: [{type, path, sections}]
  - metadata: {tokensUsed, fullOutputPath}

Constraint:
  - summary.keyFindings: MAX 5 items, each <50 tokens
  - Total handoff JSON: <500 tokens
  - Full output saved to: {project_root}\data\handoffs\{agent}_{timestamp}.json
```

### 1.2 Input Filter Protocol

**Rule**: Every agent switch MUST execute input filter

```yaml
Filter Process:
  1. Extract relevant decisions (MAX 5)
  2. List artifact paths only (no content)
  3. Extract warnings
  4. Remove: tool calls, intermediate discussion, duplicates

Target: <500 tokens after filtering
```

### 1.3 Memory Management Protocol

**Rule**: Two-tier memory system

```yaml
Short-Term Context:
  Storage: Current stage conversation + last 3 handoffs
  Limit: 5,000 tokens
  Action: Prune to 3,000 tokens after each handoff
  Archive: {project_root}\data\stage_archives\

Long-Term Memory (EvoMem):
  Storage: Facts, citations, success/failure patterns
  Retrieval: Temporal KG, Top 3 relevant only
  Query: memory.query_relevant(query, context, top_k=3)
  Effect: 2K -> 300 tokens (85% reduction)
```

### 1.4 Source Attribution Protocol

**Rule**: All factual claims MUST have source or mark [ASSUMPTION]

```yaml
Format:
  Correct: "市場規模 500 億 [來源: URL]"
  Wrong: "市場規模 500 億" (no source)
  Acceptable: "市場持續成長 [ASSUMPTION: 需驗證]"

Validator: 小查 (Agent #12) auto-checks
```

### 1.5 Checkpoint Protocol

**Rule**: Generate checkpoint at stage completion

```yaml
Trigger: Stage end (前商業/SBE/TDD/交付)
Format: CHECKPOINT_{stage}.md
Content:
  - Key decisions (with sources)
  - Assumptions to validate
  - Artifacts index
  - Token stats (before/after)
Effect: 40K -> 1.25K tokens (97% compression)
```

### 1.6 Review Protocol (NEW)

**Rule**: Multi-model review for plans and code。執行細節、腳本參考 `C:\Users\User\.claude\docs\v4.0\REVIEW_PROTOCOL.md`。

```yaml
Trigger Points:
  - Plan完成 -> 執行審查後才允許進入開發
  - Code完成 -> 在 merge / deploy 前完成審查
  - Checkpoint生成 -> 驗證交付完整性

Tooling:
  - Codex CLI: codex review --type={plan|code} --input={path} --output=data/reviews/
  - Gemini CLI: gemini code review --file={path} --format=json --output=data/reviews/
  - Windows / Linux wrapper: run_codex_review.*、run_gemini_review.* (見 `Mem0Evomem/`)

Review Flow:
  Step 1: Codex Review
    Output: data/reviews/codex_{type}_{timestamp}.json
    Threshold: overall_score >= 8/10

  Step 2: Gemini Review
    Output: data/reviews/gemini_{type}_{timestamp}.json
    Threshold: overall_score >= 8/10

  Step 3: Cross-Validation
    Compare: codex_review vs gemini_review
    If disagreement: Flag human review + log in CHECKPOINT
    If both pass: Continue
    If any fail: Fix -> 重新送審 (兩邊都要重跑)

Review Criteria:
  Plan:
    - Goal clarity
    - Feasibility
    - Risk identification
    - Resource estimation

  Code:
    - Complexity (C <= 1.25)
    - Coverage (>= 80%)
    - Type safety
    - Security vulnerabilities
    - Performance bottlenecks

Storage & Audit:
  - 資料夾: data/reviews/
  - Handoff: 附上 codex+gemini 跑完的檔案路徑
  - Checkpoint: 摘要評分、未解決問題、後續 TODO
```

---

## 第 2 節 Rules

### 2.1 Prohibitions (MUST NOT)

```yaml
- Create root directory files -> Use project-specific src/
- Create .md files unless explicitly requested
- Skip TDD Red-Green-Refactor cycle
- Create duplicate files -> Extend existing
- Use free-text handoffs -> Use JSON Schema
- Skip source attribution -> All facts need source or [ASSUMPTION]
- Accumulate full history -> Prune at each handoff
- Skip review -> MUST review plan and code
```

### 2.2 Requirements (MUST)

```yaml
- TDD First: Red -> Green -> Refactor
- Atomic Commits: Each phase separate commit
- Structured Handoffs: JSON Schema handoff protocol
- Source Attribution: Facts have source or [ASSUMPTION]
- Context Pruning: Execute input filter at handoff
- Checkpoint: Generate at stage milestones
- Multi-Model Review: Codex + Gemini review for plans/code
- Code Quality: Average CC ≤ 5, Coverage ≥ 80%
```

---

## 第 3 節 Agent Definitions

**命名規則**: 代理以「小 + 職能」命名（例: 小秘=Orchestrator）。每位代理的完整說明與提示詞都在 `.claude/agents/<name>.md`，以下僅列重點與主要產出路徑：

### 3.1 Core Team (Daily Development)

```yaml
小秘 (Orchestrator):
  Version: v2.0 (upgraded from v1.0) [NEW]
  Token: 2000
  Trigger: 複雜多步驟任務、多 Agent 協作、全階段協調、衝突解決、錯誤恢復
  File: .claude/agents/xiaomi-orchestrator.md
  Core Functions:
    - Task decomposition (MECE principle)
    - Dynamic agent routing (5-level decision) [ENHANCED from 3-level]
    - Workflow orchestration (TDD, Project-Launch)
    - Output integration & conflict resolution
    - Progress tracking & state management
    - Agent authority levels (4-tier system) [NEW]
    - Conflict resolution protocols (3 types: cross-level, peer-level, resource) [NEW]
    - Error recovery mechanisms (3 strategies: execution failure, quality, deadlock) [NEW]
  Performance Metrics [NEW]:
    - Conflict resolution rate: 93% (target: ≥90%)
    - Error recovery rate: 89% (target: ≥85%)
    - Routing accuracy: 92% (5-level decision tree, target: ≥90%)

小憶 (Memory Keeper):
  Version: v3.0-hub (upgraded from v2.0-tiny)
  Token: 2200 (increased from 1800, +22%)
  Trigger: Historical queries, memory management, context compression, proactive recommendations
  File: .claude/agents/xiaoji-memory-keeper.md
  Core Functions:
    - Intelligent Query Routing (根據 Agent 類型優化查詢)
    - Proactive Recommendations (主動推薦相關經驗與洞察)
    - Cross-Project Memory Reuse (跨專案記憶複用)
    - Memory Quality Scoring (4 維度品質評分)
  Performance Metrics:
    - Query accuracy: 90% (v2.0: 75%, +20%)
    - Cross-project reuse: 40% (v2.0: 0%)
    - Value multiplier: 3x (v2.0: 1x, +200%)
    - Average quality filter: ≥70 (B+)

小程 (Developer):
  Token: 2200
  Trigger: Green/Refactor phases, TDD workflow
  File: .claude/agents/xiaocheng-developer.md

小質 (QA Expert):
  Token: 1500
  Trigger: SBE workshop, Red phase, quality assessment
  File: .claude/agents/xiaozhi-quality.md

小查 (Validator):
  Token: 1500
  Trigger: 全階段（每次 agent 輸出後自動觸發）
  File: .claude/agents/xiaocha-validator.md
  Core Functions:
    - Source attribution validation (標記 [ASSUMPTION])
    - Logic consistency check (矛盾檢測)
    - Confidence scoring (0-100 scale)
    - Hallucination prevention (target: <2%)
  Quality Gates:
    - Hallucination rate < 2%
    - Source coverage > 90%
    - Logic consistency > 95%
    - Avg confidence > 75
```

### 3.2 Full Team (Project Launch)

```yaml
# 前商業階段
小秘: Orchestrator (全階段)
小研: 產業分析 -> docs/research/industry.md
小市: 市場策略 -> docs/research/gtm.md
小品: PRD -> docs/product/prd.md
小界: UX/UI 設計 -> docs/design/ (wireframes, design-system, interaction-specs)
小前: 視覺 -> docs/design/ui-style.md

# 開發階段
小架: 架構 -> ARCHITECTURE.md
小後: 後端 -> src/backend/
小界: 前端 -> src/frontend/
小數: 指標定義 -> docs/analytics/metrics-definition.md

# 交付階段
小數: A/B Testing & Analytics -> docs/analytics/ (ab-tests, weekly-reports, dashboards)
小策: 文檔撰寫 -> docs/ (api, guides, technical, releases)

# 註記：
# - 小秘 (Orchestrator) 與 小查 (Validator) 為 Core Team 成員（見 3.1 節）
# - 小秘在全階段協調多 Agent 工作流
# - 小查在每次 agent 輸出後自動驗證（目標: <2% hallucination rate）
# - 小數在開發階段定義指標，在交付階段執行數據分析與實驗驗證
```

### 3.3 Thinking Frameworks

```yaml
思維樹 (Tree): 小秘、小研、小架、小界 (Design Thinking 5-Stage)
思維鍊 (Chain): 小質、小程、小憶、小後、小查
DDDM (Data-Driven): 小數 (Hypothesis → Experiment → Collect → Analyze → Insight)
Docs-as-Code: 小策 (Source Control → Markdown → Automation → Quality → Deploy)
PREP: 小市、小品、小前
```

---

## 第 4 節 Workflow Stages

### 4.1 Stage 0: Project Init

```yaml
Interview (7 questions):
  1. Project name
  2. Description (<50 chars)
  3. Type: simple/standard/ai-ml
  4. Language
  5. GitHub: new/existing/local
  6. EvoMem: enable/query-only/disable
  7. Test strategy

Auto-script:
  1. Create folder structure
  2. Generate files: README, CLAUDE.md, pytest.ini, requirements/*.txt
  3. Install dependencies
  4. Setup Git + post-commit hook
  5. Setup EvoMem
```

### 4.2 Stage 1: Pre-Business (Iterative)

```yaml
Flow (NOT linear, iterative):
  小研 -> 小市 -> 小品 -> 小設 -> 小前
  ↑__________________________|
  (可回頭確認)

Handoff: JSON Schema
Completion:
  - All artifacts generated
  - 小查 verified (no hallucination)
  - 小秘 generated checkpoint (<2K tokens)
  - Total tokens <50K
```

### 4.3 Stage 2: SBE Workshop

```yaml
Host: 小質
Participants: User + 小憶 + 小架
Output: features/<domain>.feature (Gherkin + Examples)
Prep: 小憶 queries EvoMem (defects/success patterns)
```

### 4.4 Stage 3: TDD Cycle

```yaml
Red:
  - Write AAA format failing test
  - Query EvoMem for defect patterns
  - 小查 validates test
  - Handoff: JSON Schema

Green:
  - Minimal implementation
  - Coverage >= 80%
  - Pytest all pass
  - Handoff: JSON Schema
  - (NEW) Codex + Gemini review code

Refactor:
  - Measure complexity (C <= 1.25)
  - Type check
  - Refactor
  - Handoff: JSON Schema
  - (NEW) Codex + Gemini review changes
```

### 4.5 Stage 4: Delivery

```yaml
小數: Execute scripts/ci/full_check.sh
小策: Write REPORT.md
小秘: Generate final checkpoint, update EvoMem
```

---

## 第 5 節 File References

```yaml
Schemas:
  Handoff: .claude/schemas/handoff-v1.json
  Review: .claude/schemas/review-v1.json

Agents:
  Core Team (Daily Development):
    - .claude/agents/xiaomi-orchestrator.md (小秘, ~2000 tokens)
    - .claude/agents/xiaoji-memory-keeper.md (小憶, ~1800 tokens)
    - .claude/agents/xiaocheng-developer.md (小程, ~2200 tokens)
    - .claude/agents/xiaozhi-quality.md (小質, ~1500 tokens)
    - .claude/agents/xiaocha-validator.md (小查, ~1500 tokens)

  Extended Team (Available):
    - .claude/agents/xiaojia-architect.md (小架, Architecture)
    - .claude/agents/xiaoan-security.md (小安, Security)
    - .claude/agents/xiaokuai-performance.md (小快, Performance)
    - .claude/agents/xiaoyun-devops.md (小雲, DevOps)
    - .claude/agents/xiaoche-documentation-writer.md (小策, Documentation Writer, ~2000 tokens) [NEW - P1]
    - .claude/agents/xiaohou-backend-developer.md (小後, Backend Developer, ~2500 tokens) [NEW - P0]

  Business Analysis Team (Pre-Business Stage):
    - .claude/agents/xiaoyan-research.md (小研, Research Analyst, ~2000 tokens)
    - .claude/agents/xiaoshi-market.md (小市, Market Strategist, ~2000 tokens)
    - .claude/agents/xiaopin-product.md (小品, Product Manager, ~2000 tokens)
    - .claude/agents/xiaojie-ux-designer.md (小界, UX/UI Designer, ~2500 tokens) [NEW - P0]
    - .claude/agents/xiaoshu-data-analyst.md (小數, Data Analyst, ~2000 tokens) [NEW - P0]

  Full Team Reference:
    - CODEX啟動指南 第 5.2 節 (`.claude/docs/v4.0/CODEX啟動指南_v1.0.md`)

Protocols:
  Review: .claude/docs/v4.0/REVIEW_PROTOCOL.md
  Memory: EvoMem/docs/MEMORY_PROTOCOL.md

Templates:
  Project: .claude/docs/v4.0/PROJECT_TEMPLATE.md

Documentation:
  Index: .claude/docs/README.md
  v4.0 Guide: .claude/docs/v4.0/README_V4.md
  Usage Example: .claude/docs/v4.0/USAGE_EXAMPLE.md
  Implementation Status: .claude/docs/v4.0/IMPLEMENTATION_STATUS.md
```

---

## 第 6 節 Usage

```yaml
For LLM:
  1. Read this WORKSPACE_SPEC.md
  2. Read docs/v4.0/PROJECT_TEMPLATE.md
  3. Execute project interview (見第 4.1 節)
  4. Generate project-specific CLAUDE.md
  5. Follow protocols in generated CLAUDE.md

For Human:
  - This is meta-spec, NOT for direct use
  - Use generated project CLAUDE.md instead
  - Complete documentation in docs/ directory
  - Documentation index: docs/README.md
```

## 實測數據 (2025-11-14)

```yaml
文檔大小:
  - WORKSPACE_SPEC.md: 357 行, ~2,200 tokens (實測)
  - PROJECT_TEMPLATE.md: 220 行, ~800 tokens (實測)
  - REVIEW_PROTOCOL.md: 384 行, ~2,000 tokens (實測)

完整功能開發 Token 使用:
  - 初始讀取 (首次): 3,800 tokens
  - Agent 交接 (每次): ~400 tokens
  - Review 執行: 200 tokens
  - 完整功能總計: ~6,400 tokens

對比:
  - 傳統方式: ~15,000 tokens
  - 實際節省: ~57% (not 80%)

Review System 實作:
  - 狀態: ✅ 半自動化
  - 使用方式(命令列): Codex, Gemini
  - 類型: 結構化提示詞 + 手動執行
  - 產出: codex_reviews/, gemini_reviews/, cross_reviews/
```

