# 關鍵修訂需求 (Critical Revisions Required)

**Date**: 2025-11-15
**Reviewer**: 對抗性思維 + 思維樹審查
**Status**: 🔴 需要立即修訂

---

## 🚨 高優先級 (P0 - 必須修訂)

### 1. 階段偵測循環依賴 ❌

**問題**: 被動偵測導致首次壓縮無法判斷階段

**修訂方案**: 主動宣告協議
```yaml
User/Agent declares: "## 🎯 Stage: tdd.red"
System uses: tdd.red compression settings
```

**影響文件**:
- [x] `CLAUDE.md` - Protocol 2: Stage-Aware Compression
- [x] `WORKSPACE_SPEC.md` - Section 1.2

**預計工時**: 2 小時

---

### 2. Memory Chain 無修剪機制 ❌

**問題**: 多功能專案會突破 1,500 tokens 限制

**修訂方案**: 滑動視窗 + 增量歸檔
```yaml
max_chain_length: 5 stages
Pruning: Merge oldest → "Early Dev Summary"
Archive: data/memory_archive/{feature}.md
```

**影響文件**:
- [x] `CLAUDE.md` - Protocol 1: Enhanced Handoff
- [x] `schemas/handoff-v2.json` - memoryChain constraints

**預計工時**: 3 小時

---

### 3. Handoff JSON 實作缺失 ❌

**問題**: 無自動化工具,手動生成不可靠

**修訂方案**: 半自動化 (template + validation script)
```python
validate_handoff.py:
  - Schema validation
  - Auto-complete timestamp, hash
  - Token count check
```

**影響文件**:
- [x] 新增 `scripts/validate_handoff.py`
- [x] 新增 `scripts/generate_handoff_template.py`
- [x] 更新 `README.md` - 使用說明

**預計工時**: 4 小時

---

### 4. 效能指標過度承諾 ❌

**問題**: Token -40%, Hallucination <2% 可能無法達成

**修訂方案**: 調整為保守估計
```yaml
Token Efficiency: -13% (更現實)
Hallucination Rate: 3-4% (仍顯著改善)
Source Coverage: 75-80% (可達成)
```

**影響文件**:
- [x] `CLAUDE.md` - Performance Metrics
- [x] `USAGE_SUMMARY.md` - 預期效果
- [x] `README.md` - 效能數據

**預計工時**: 1 小時

---

## ⚠️ 中優先級 (P1 - 應該修訂)

### 5. 小查全時驗證成本高 ⚠️

**問題**: +37.5% Token overhead 抵消節省

**修訂方案**: Risk-based validation
```yaml
Light mode: All outputs (~200 tokens)
Standard mode: High-risk outputs (~800 tokens)
Deep mode: User-requested (~1,500 tokens)
Saving: -70% validation cost
```

**影響文件**:
- [x] `agents/xiaocha-validator.md` - 新增驗證模式
- [x] `CLAUDE.md` - Protocol 3: Hallucination Prevention

**預計工時**: 2 小時

---

### 6. 多模型審查可行性低 ⚠️

**問題**: 雙 API 配置困難,成本高

**修訂方案**: Single-LLM multi-perspective review
```yaml
Self-Review: radon, pytest, mypy, bandit
Peer Review: 不同 Agent 審查
Optional: External API (僅當配置時)
```

**影響文件**:
- [x] `CLAUDE.md` - Protocol 4: Multi-Model Review → Review Protocol v2.0
- [x] `scripts/run-codex-review.sh` → `scripts/self-review.sh`
- [x] 刪除或標記為 optional: `run-gemini-review.sh`

**預計工時**: 3 小時

---

### 7. 壓縮不可逆性問題 ⚠️

**問題**: 無法支援迭代開發

**修訂方案**: 三層存儲
```yaml
Tier 1: Active Context (當前)
Tier 2: Stage Archive (Checkpoint)
Tier 3: Full Backup (30 days, JSONL)
```

**影響文件**:
- [x] `CLAUDE.md` - Protocol 5: Memory Management
- [x] 新增 `scripts/restore_full_context.py`

**預計工時**: 4 小時

---

## 📝 低優先級 (P2 - 可選修訂)

### 8. 缺失的範例與腳本 📝

**問題**: 部分承諾的文件未實作

**修訂方案**: 補充或標記為 TODO

**缺失文件**:
- [ ] `templates/checkpoint-example.md`
- [ ] `templates/prd-template.md`
- [ ] `scripts/pre-commit`
- [ ] `docs/AGENT_GUIDE.md`
- [ ] `docs/WORKFLOW_GUIDE.md`
- [ ] `docs/TROUBLESHOOTING.md`

**預計工時**: 6 小時 (分散執行)

---

## 📊 修訂工時總計

```yaml
P0 (必須): 10 小時
P1 (應該): 9 小時
P2 (可選): 6 小時

Total: 25 小時 (約 3-4 個工作天)
```

---

## 🎯 建議執行順序

### Week 1: 修復致命缺陷 (P0)

**Day 1-2**:
1. ✅ 階段偵測循環依賴 (2h)
2. ✅ Memory Chain 修剪機制 (3h)
3. ✅ Handoff JSON 半自動化 (4h)

**Day 3**:
4. ✅ 效能指標調整 (1h)

### Week 2: 優化系統 (P1)

**Day 4-5**:
5. ✅ 小查驗證模式 (2h)
6. ✅ Review Protocol v2.0 (3h)
7. ✅ 三層存儲系統 (4h)

### Week 3+: 補充文檔 (P2)

**按需執行**:
8. 補充缺失的範例與腳本 (6h)

---

## 🔄 修訂後的專案狀態

### 修訂前 (v4.0 Original)

```yaml
優點:
  ✅ 思維方向正確 (基於 2025 研究)
  ✅ 文檔非常詳盡
  ✅ Domain-specific extensions 有價值

致命缺陷:
  ❌ 階段偵測循環依賴 (無法執行)
  ❌ Memory Chain 會爆炸 (多功能專案)
  ❌ Handoff JSON 無實作 (理論設計)
  ❌ 小查全時驗證成本抵消節省
  ❌ 雙 API 審查門檻高,可行性低
  ❌ 壓縮不可逆,違反敏捷原則
  ❌ 效能承諾過度樂觀

評級: C (有潛力,但需大幅修訂)
```

### 修訂後 (v4.1 Realistic)

```yaml
優點:
  ✅ 思維方向正確 (基於 2025 研究)
  ✅ 階段宣告協議 (解決循環依賴)
  ✅ 滑動視窗 Memory Chain (可擴展)
  ✅ 半自動化 Handoff (可執行)
  ✅ Risk-based 驗證 (成本可控)
  ✅ Single-LLM 審查 (降低門檻)
  ✅ 三層存儲 (支援迭代)
  ✅ 保守效能估計 (可達成)

評級: A- (生產就緒,實際可用)
```

---

## 🎓 關鍵學習

### 對抗性思維的價值

**發現的問題類型**:
1. **循環依賴**: 階段偵測 chicken-and-egg
2. **規模問題**: Memory Chain 爆炸性增長
3. **實作 Gap**: 理論協議 vs 實際工具
4. **成本矛盾**: 優化目標 vs 驗證成本
5. **可行性**: 雙 API vs 單一用戶設置
6. **原則衝突**: 不可逆壓縮 vs 敏捷開發

### 改進原則

1. **Under-promise, Over-deliver**: 保守承諾,超額交付
2. **Fail-safe defaults**: 系統應在無配置時仍可用
3. **Graceful degradation**: 外部依賴失敗時有備案
4. **Cost-conscious**: 優化不應引入更高成本
5. **Reversibility**: 重要決策應可撤銷
6. **Progressive enhancement**: 核心功能 + 可選增強

---

## ✅ 下一步行動

### 立即執行 (今天)

1. **更新 CLAUDE.md v4.1**
   - 修正 Protocol 2 (階段宣告)
   - 修正 Protocol 5 (Memory Chain 修剪)
   - 修正 Performance Metrics (保守估計)

2. **更新 USAGE_SUMMARY.md**
   - 調整效能數據
   - 標註"現實估計"

### 本週執行

3. **實作驗證工具**
   - `scripts/validate_handoff.py`
   - `scripts/generate_handoff_template.py`

4. **更新 Agent 文件**
   - `agents/xiaocha-validator.md` (三種驗證模式)

### 下週執行

5. **實作三層存儲**
   - `scripts/restore_full_context.py`
   - 更新 Protocol 5

6. **Review Protocol v2.0**
   - `scripts/self-review.sh`
   - 更新 Protocol 4

---

**🎯 目標: 將 v4.0 "理想設計" 轉化為 v4.1 "實際可用系統"**
