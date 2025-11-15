# 快速開始指南 (Quick Start Guide)

**Version**: 4.0
**Audience**: 新專案開發者
**Time**: 10-15 分鐘

---

## 🎯 目標

完成本指南後,您將:
- ✅ 了解完整工作流程 (前商業 → SBE → TDD → 交付)
- ✅ 知道如何召喚 Agent
- ✅ 能夠開始第一個功能開發

---

## 📋 前置條件

```bash
# 1. Python 3.8+
python --version  # 應該 >= 3.8

# 2. Git
git --version

# 3. 基本 CLI 工具
pip --version
pytest --version  # 如果沒有會在 Step 1 安裝
```

---

## 🚀 三種啟動模式

根據您的需求選擇:

### 模式 A: 完整專案 (前商業 → 開發 → 交付)

**適用於**: 全新專案,需要完整的商業分析與產品規劃

**時間**: 3-5 天 (含商業分析)

**流程**:
```
1. 初始化專案 (init-project.sh)
2. 前商業階段 (小研 → 小市 → 小品 → 小界)
3. SBE Workshop (小質)
4. TDD Cycle (小程 + 小質)
5. 交付 (小數 + 小策)
```

[詳細步驟](#mode-a-complete)

---

### 模式 B: 快速開發 (已有需求 → 直接開發)

**適用於**: 已有 PRD 或需求文檔,直接開始開發

**時間**: 1-2 天

**流程**:
```
1. 初始化專案 (init-project.sh)
2. SBE Workshop (小質) - 轉換需求為 .feature
3. TDD Cycle (小程 + 小質)
4. 交付 (小數 + 小策)
```

[詳細步驟](#mode-b-fast-dev)

---

### 模式 C: 極簡模式 (僅用 Agent 協助)

**適用於**: 簡單任務,只需要特定 Agent 協助

**時間**: 數小時

**流程**:
```
1. 手動創建目錄結構
2. 按需召喚 Agent (例: @.claude/agents/xiaocheng-developer.md)
```

[詳細步驟](#mode-c-minimal)

---

## 📖 模式 A: 完整專案 {#mode-a-complete}

### Step 1: 初始化專案

```bash
# 1. 複製模板到新專案目錄
cp -r project-template ~/my-saas-app/.claude

# 2. 進入專案目錄
cd ~/my-saas-app

# 3. 執行初始化腳本
./.claude/scripts/init-project.sh

# Windows 用戶使用:
# .\.claude\scripts\init-project.bat
```

**輸出**:
```
✅ 專案初始化完成!
📁 目錄結構已創建
📄 基礎文件已生成
🔧 Git 已初始化
```

---

### Step 2: 前商業階段 (產業研究)

**召喚 Agent**: 小研 (產業研究分析師)

在 Claude Code 中輸入:
```
請讀取 .claude/agents/xiaoyan-research.md

我需要進行產業研究,目標產業是 [填入您的產業],
請執行完整的產業分析包括:
- 市場規模
- 競爭格局
- 趨勢分析
- 垂直產業機會
```

**小研會產出**:
- `docs/research/industry.md` - 產業分析報告
- Handoff JSON - 交接給小市

**時間**: 30-60 分鐘

---

### Step 3: 前商業階段 (市場策略)

**召喚 Agent**: 小市 (市場策略專家)

小研完成後,小市會自動被召喚 (如果有 Orchestrator),或手動召喚:

```
請讀取 .claude/agents/xiaoshi-market.md

基於小研的產業分析,請制定 GTM 策略包括:
- 目標客群
- 定價策略
- 銷售通路
- 市場定位
```

**小市會產出**:
- `docs/research/gtm.md` - 市場策略
- Handoff JSON - 交接給小品

**時間**: 30-60 分鐘

---

### Step 4: 前商業階段 (產品規劃)

**召喚 Agent**: 小品 (產品經理)

```
請讀取 .claude/agents/xiaopin-product.md

基於市場策略,請撰寫 PRD 包括:
- 功能需求 (P0, P1, P2)
- 非功能需求 (效能、擴展性、安全)
- 技術約束
- Acceptance Criteria
```

**小品會產出**:
- `docs/product/prd.md` - 產品需求文檔
- Handoff JSON - 交接給小界

**時間**: 1-2 小時

---

### Step 5: 前商業階段 (UX/UI 設計)

**召喚 Agent**: 小界 (UX/UI 設計師)

```
請讀取 .claude/agents/xiaojie-ux.md

基於 PRD,請進行 UX/UI 設計包括:
- User flow
- Wireframes
- Interaction specs
- Design system
```

**小界會產出**:
- `docs/design/user-flow.md`
- `docs/design/wireframes/`
- `docs/design/design-system.md`
- Handoff JSON - 交接給小架

**時間**: 2-3 小時

---

### Step 6: Checkpoint 1 - 前商業階段完成

```bash
# 小秘 (Orchestrator) 自動生成 Checkpoint
# 或手動請求:

請讀取 .claude/agents/xiaomi-orchestrator.md

前商業階段已完成,請生成 CHECKPOINT_PRE_BUSINESS.md
```

**Checkpoint 包含**:
- 關鍵決策摘要
- 所有 artifacts 索引
- Token 使用統計
- 下一步建議

**壓縮效果**: 40K tokens → 1.25K tokens (97%)

---

### Step 7: SBE Workshop (需求工作坊)

**召喚 Agent**: 小質 (QA 專家)

```
請讀取 .claude/agents/xiaozhi-quality.md

請主持 SBE Workshop,基於 PRD 生成 .feature 文件。

範例領域: [例如: 用戶認證、計算機、購物車]
```

**小質會產出**:
- `features/authentication.feature` (Gherkin 格式)
- 包含場景、範例、邊界條件

**時間**: 1-2 小時

---

### Step 8-10: TDD Cycle (核心開發)

詳見 [模式 B: TDD 流程](#tdd-flow)

---

### Step 11: 交付階段

**召喚 Agent**: 小數 (資料分析) + 小策 (文檔撰寫)

```
# 小數: 執行 CI/CD 檢查
請執行 scripts/ci/full_check.sh 並產出品質報告

# 小策: 撰寫交付文檔
請撰寫 RELEASE_NOTES.md、API 文檔、使用指南
```

**時間**: 2-3 小時

---

## 📖 模式 B: 快速開發 {#mode-b-fast-dev}

### Step 1: 初始化

同 [模式 A Step 1](#mode-a-complete)

---

### Step 2: 將現有需求轉為 .feature

**假設**: 您已有 PRD 或需求文檔

**召喚 Agent**: 小質

```
請讀取 .claude/agents/xiaozhi-quality.md

我有以下需求文檔: [貼上您的需求]

請將其轉換為 Gherkin .feature 文件,包括:
- 功能描述
- 場景
- 範例表格
- 邊界條件
```

**產出**: `features/*.feature`

---

### Step 3: TDD Cycle {#tdd-flow}

#### 🔴 Phase 1: Red (寫失敗測試)

**召喚 Agent**: 小質 (主導) + 小程 (協助)

```
請讀取 .claude/agents/xiaozhi-quality.md

基於 features/authentication.feature,請撰寫 AAA 格式的失敗測試。

測試文件: tests/unit/test_authentication.py
```

**小質會**:
1. 查詢 EvoMem 歷史 Bug 案例
2. 撰寫 AAA (Arrange-Act-Assert) 測試
3. 確保測試失敗 (Red)
4. 生成 Handoff JSON 交給小程

**產出**:
```python
# tests/unit/test_authentication.py

def test_user_login_with_valid_credentials():
    # Arrange
    user = create_test_user(email="test@example.com", password="Password123!")

    # Act
    result = authenticate(email="test@example.com", password="Password123!")

    # Assert
    assert result.success is True
    assert result.user_id == user.id
    assert result.token is not None
```

**Git Commit**:
```bash
git add tests/
git commit -m "test(TDD-Red): 新增用戶認證測試

🔴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

#### 🟢 Phase 2: Green (最小實作)

**召喚 Agent**: 小程 (主導)

```
請讀取 .claude/agents/xiaocheng-developer.md

基於失敗測試,請實作最小可行代碼讓測試通過。

要求:
- Coverage >= 80%
- 所有測試通過
- 代碼簡潔
```

**小程會**:
1. 實作最小功能
2. 執行 `pytest tests/ -v`
3. 確保 Coverage >= 80%
4. 生成 Handoff JSON

**產出**:
```python
# src/auth/authentication.py

def authenticate(email: str, password: str) -> AuthResult:
    """用戶認證"""
    user = get_user_by_email(email)

    if not user:
        return AuthResult(success=False, error="User not found")

    if not verify_password(password, user.password_hash):
        return AuthResult(success=False, error="Invalid password")

    token = generate_jwt_token(user.id)
    return AuthResult(success=True, user_id=user.id, token=token)
```

**Git Commit**:
```bash
git add src/
git commit -m "feat(TDD-Green): 實現用戶認證功能

✅ Coverage: 85%
✅ All tests pass

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

#### 🔵 Phase 3: Refactor (優化代碼)

**召喚 Agent**: 小程

```
請測量代碼複雜度並進行 Refactoring:
- 目標: Cyclomatic Complexity <= 5
- Type hints 100%
- 提升可讀性
```

**小程會**:
1. 執行 `radon cc src/ -a` (測量複雜度)
2. 執行 `mypy src/` (型別檢查)
3. Refactor 代碼
4. 再次執行測試確保功能不變

**產出**:
```python
# src/auth/authentication.py (Refactored)

from typing import Optional
from dataclasses import dataclass

@dataclass
class AuthResult:
    success: bool
    user_id: Optional[int] = None
    token: Optional[str] = None
    error: Optional[str] = None

def authenticate(email: str, password: str) -> AuthResult:
    """
    用戶認證

    Args:
        email: 用戶 email
        password: 明文密碼

    Returns:
        AuthResult: 認證結果,包含 success, user_id, token

    Raises:
        ValueError: 如果 email 或 password 為空
    """
    if not email or not password:
        raise ValueError("Email and password are required")

    user = get_user_by_email(email)
    if user is None:
        return AuthResult(success=False, error="User not found")

    if not verify_password(password, user.password_hash):
        return AuthResult(success=False, error="Invalid password")

    token = generate_jwt_token(user.id)
    return AuthResult(success=True, user_id=user.id, token=token)
```

**Git Commit**:
```bash
git add src/
git commit -m "refactor(TDD-Refactor): 優化認證代碼

- 新增型別提示
- 改善錯誤處理
- 降低複雜度: 8 → 4

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

#### 🔍 Phase 4: Review (雙模型審查)

**執行 Codex + Gemini Review**:

```bash
# Codex Review
./.claude/scripts/run-codex-review.sh src/auth/authentication.py

# Gemini Review
./.claude/scripts/run-gemini-review.sh src/auth/authentication.py

# 檢查結果
cat data/reviews/codex_code_*.json
cat data/reviews/gemini_code_*.json
```

**如果兩個模型都 >= 8/10**: 繼續下一個功能

**如果任一模型 < 8/10**: 修復問題,重新送審

---

### Step 4: 重複 TDD Cycle

針對每個功能重複 Red → Green → Refactor → Review

---

### Step 5: 生成 Checkpoint

每完成一個 Stage (例: 完成所有認證功能),生成 Checkpoint:

```
請讀取 .claude/agents/xiaomi-orchestrator.md

認證功能已完成,請生成 CHECKPOINT_AUTH.md
```

---

## 📖 模式 C: 極簡模式 {#mode-c-minimal}

### 使用場景

- 簡單腳本或工具
- 只需要特定 Agent 協助
- 不需要完整工作流程

### 步驟

```bash
# 1. 手動創建目錄
mkdir -p my-tool/{src,tests}
cd my-tool

# 2. 僅複製需要的 Agent
cp -r project-template/agents .claude/

# 3. 按需召喚 Agent
# 例如: 需要代碼審查
請讀取 .claude/agents/xiaocheng-developer.md
請審查以下代碼: [貼上代碼]
```

---

## 🎯 常見任務速查

### 任務 1: 查詢歷史 Bug

```
請讀取 .claude/agents/xiaoji-memory-keeper.md

查詢歷史 Bug 案例,關鍵字: [認證失敗、SQL 注入、XSS]
```

### 任務 2: 架構設計

```
請讀取 .claude/agents/xiaojia-architect.md

設計系統架構,需求:
- 支援 10K 並發用戶
- 99.9% 可用性
- 全球多地區部署
```

### 任務 3: 效能優化

```
請讀取 .claude/agents/xiaokuai-performance.md

分析效能瓶頸:
- 目前響應時間: 500ms
- 目標: <100ms
- Profiling 數據: [貼上]
```

---

## 🐛 疑難排解

### 問題 1: Agent 沒有被自動召喚

**解決方案**:
```bash
# 確認 CLAUDE.md 存在
ls .claude/CLAUDE.md

# 手動請求 Claude Code 讀取
"請讀取 .claude/CLAUDE.md 並開始工作"
```

### 問題 2: 測試執行失敗

**解決方案**:
```bash
# 檢查依賴
pip install -r requirements/base.txt

# 檢查 pytest 配置
cat pytest.ini

# 手動執行測試
pytest tests/ -v --tb=short
```

### 問題 3: Git Commit 被 Hook 阻止

**解決方案**:
```bash
# 檢查 pre-commit hook
cat .git/hooks/pre-commit

# 臨時跳過 hook
git commit --no-verify -m "..."

# 修復問題後重新 commit
```

---

## 📊 預期時間表

| 模式 | 初始化 | 開發 | 總時間 |
|------|--------|------|--------|
| A: 完整專案 | 10 分鐘 | 3-5 天 | 3-5 天 |
| B: 快速開發 | 10 分鐘 | 1-2 天 | 1-2 天 |
| C: 極簡模式 | 5 分鐘 | 數小時 | 數小時 |

---

## 🎓 下一步學習

- [Agent 使用指南](AGENT_GUIDE.md) - 所有 Agent 詳細說明
- [工作流程指南](WORKFLOW_GUIDE.md) - 完整開發流程
- [CLAUDE.md](../CLAUDE.md) - 完整規範參考

---

**🚀 準備好了嗎? 開始您的第一個功能開發!**
