# 專案目錄結構

**版本**: 2.0.0
**最後更新**: 2025-11-16

---

## 📁 完整目錄結構

```
project-template/
├── integrations/                           # 整合模組目錄
│   │
│   ├── 📖 README.md                        # 快速入門指南（本文件）
│   ├── 📖 UNIVERSAL_STORAGE_USER_GUIDE.md # 詳細使用文檔
│   ├── 📖 DIRECTORY_STRUCTURE.md          # 目錄結構說明
│   ├── 📖 MEMORY_HANDOFF_USER_GUIDE.md    # 記憶交接使用指南（Phase 1）
│   ├── 📖 MEMORY_HANDOFF_COMPLETION_REPORT.md # Phase 1 完成報告
│   │
│   ├── 🔧 universal_memory_storage.py     # 通用記憶存儲核心（487 行）
│   ├── 🔧 memory_handoff_integration.py   # 記憶交接整合 v2.0.0
│   ├── 🔧 compress_context.py             # Factory.ai 2025 壓縮
│   ├── 🔧 context7_integration.py         # Context7 MCP 整合
│   ├── 🔧 exa_integration.py              # Exa API 整合
│   │
│   ├── 🧪 test_universal_storage.py       # 通用存儲測試（360 行）
│   ├── 📝 example_usage.py                # 實用範例代碼
│   │
│   ├── 📄 HANDOFF_*.md                    # 記憶交接文檔（自動生成）
│   └── 📄 TODO_NEXT.md                    # 下一步 TODO（自動生成）
│
├── scripts/                                # 腳本工具目錄
│   └── compress_context.py                # 壓縮腳本
│
└── data/                                   # 資料存儲目錄
    ├── memory/                             # JSON 記憶存儲（BASIC）
    │   ├── mem_20251116_100000.json
    │   ├── mem_20251116_100001.json
    │   └── ...
    │
    └── vectors/                            # 向量資料庫（FULL）
        └── memory/                         # EvoMem 持久化目錄
            ├── chroma.sqlite3
            └── ...
```

---

## 📖 核心文檔說明

### 1. README.md（本文件）

**用途**: 快速入門指南
**適用對象**: 所有使用者
**內容**:
- 系統概述
- 快速開始（零配置範例）
- 支援的存儲後端
- 測試指令
- 版本歷史

**閱讀時間**: 5 分鐘

---

### 2. UNIVERSAL_STORAGE_USER_GUIDE.md

**用途**: 完整使用文檔
**適用對象**: 深度使用者、開發者
**內容**:
- 詳細 API 參考
- 配置選項
- 進階用法
- 常見場景
- 故障排除
- 最佳實踐

**閱讀時間**: 30 分鐘

---

### 3. DIRECTORY_STRUCTURE.md（本文件）

**用途**: 目錄結構說明
**適用對象**: 新加入者、維護者
**內容**:
- 完整目錄樹
- 檔案用途說明
- 文檔索引
- 資料存儲位置

**閱讀時間**: 10 分鐘

---

### 4. MEMORY_HANDOFF_USER_GUIDE.md（Phase 1）

**用途**: 記憶交接系統使用指南
**適用對象**: 使用記憶交接功能的使用者
**內容**:
- 記憶交接觸發條件
- 5-Step 流程說明
- 生成的文檔格式
- 故障排除

**閱讀時間**: 15 分鐘

---

### 5. MEMORY_HANDOFF_COMPLETION_REPORT.md（Phase 1）

**用途**: Phase 1 完成報告
**適用對象**: 專案管理者、技術審查者
**內容**:
- Phase 1 實作摘要
- 技術指標
- 關鍵決策
- 下一步計劃

**閱讀時間**: 20 分鐘

---

## 🔧 核心代碼檔案

### 1. universal_memory_storage.py（487 行）

**用途**: 通用記憶存儲核心架構
**類別**:
- `StorageCapability` - 能力等級列舉
- `MemoryStorageInterface` - 抽象介面
- `EvoMemStorage` - EvoMem 後端（FULL）
- `JSONStorage` - JSON 後端（BASIC）
- `MemoryStorageFactory` - 工廠類（自動檢測）
- `create_storage()` - 便利函數

**功能**:
- ✅ 統一存儲介面
- ✅ 自動降級（EvoMem → JSON）
- ✅ 零配置支援
- ✅ 能力分級

**依賴**:
- 標準函式庫（json, os, pathlib）
- 可選: EvoMem（FULL 功能）

---

### 2. memory_handoff_integration.py（v2.0.0）

**用途**: 記憶交接系統整合
**版本變更**:
- v1.0.0: 硬編碼 JSON 存儲
- v2.0.0: 整合 `universal_memory_storage`

**類別**:
- `MemoryHandoffTrigger` - 觸發條件檢測
- `MemoryExtractor` - 資訊提取與壓縮
- `MemoryEnhancer` - Context7 + Exa 增強
- `MemoryStorage` - 通用存儲包裝器（v2.0.0）
- `HandoffDocumenter` - 文檔生成
- `MemoryHandoffOrchestrator` - 流程編排器

**功能**:
- ✅ 5-Step 記憶交接流程
- ✅ 自動觸發檢測
- ✅ Factory.ai 2025 壓縮
- ✅ Context7 + Exa 增強
- ✅ 通用存儲整合（v2.0.0 新增）

---

### 3. compress_context.py

**用途**: Factory.ai 2025 壓縮標準實作
**功能**:
- Session Intent 提取
- Play-by-Play 壓縮
- Artifacts 保留
- Breadcrumbs 提取
- Token 估算

**壓縮率**: 95%+

---

### 4. context7_integration.py

**用途**: Context7 MCP 整合（P1-4.2）
**功能**:
- 框架優先級權重（10/7-8/5-6/3/1）
- 版本檢測
- 依賴關係圖
- 文檔自動獲取

**支援框架**: 100+

---

### 5. exa_integration.py

**用途**: Exa AI 搜尋 API 整合（P1-3）
**功能**:
- 最佳實踐搜尋
- 結果快取
- Mock 模式（無 API key 時）

**免費額度**: $10 (2,000 次搜尋)

---

## 🧪 測試與範例

### 1. test_universal_storage.py（360 行）

**用途**: 完整測試套件
**測試分層**:
- Layer 1: 核心合約測試（所有後端）
- Layer 2: 能力合約測試（根據能力）
- Layer 3: 後端特定測試（獨特功能）
- Layer 4: 工廠與降級測試（自動降級）

**執行**:
```bash
python test_universal_storage.py
```

**預期結果**:
- 總測試數: 10
- 通過: 8
- 失敗/跳過: 2（EvoMem 不可用 - 預期）
- 通過率: 80%

---

### 2. example_usage.py

**用途**: 實用範例代碼
**包含範例**:
1. 基礎使用 - 零配置快速開始
2. 完整記憶交接流程
3. 語義搜尋（EvoMem）
4. 條件性功能使用
5. 批次處理
6. 環境感知配置
7. 健康監控
8. 備份與恢復

**執行**:
```bash
python example_usage.py
```

---

## 📄 自動生成文檔

### 1. HANDOFF_*.md

**生成時機**: 執行 `execute_handoff()` 後
**命名格式**: `HANDOFF_{phase}_{timestamp}.md`
**範例**: `HANDOFF_P1-5_20251116.md`

**內容結構**:
```markdown
# 記憶交接文檔

**時間**: 2025-11-16T10:00:00Z
**記憶 ID**: mem_20251116_100000
**專案**: 專案名稱
**階段**: P1-5

## 📋 任務摘要
## 📁 產出物
## 🔑 關鍵決策
## 💡 學習與洞察
## 📊 效能指標
```

---

### 2. TODO_NEXT.md

**生成時機**: 執行 `execute_handoff()` 後
**內容**: 下一步待辦事項

**內容結構**:
```markdown
# 下一步 TODO

**生成時間**: 2025-11-16T10:00:00Z
**專案**: 專案名稱
**階段**: P1-5

## 🔄 待辦事項

1. **任務 1**
   - 進行中: 描述

2. **任務 2**
   - 待辦: 描述
```

---

## 💾 資料存儲目錄

### 1. data/memory/（JSON 存儲）

**用途**: JSON 後端存儲目錄
**檔案格式**: `{memory_id}.json`
**範例**: `mem_20251116_100000.json`

**檔案結構**:
```json
{
  "id": "mem_20251116_100000",
  "type": "handoff",
  "timestamp": "2025-11-16T10:00:00Z",
  "session_memory": {...},
  "long_term_memory": {...},
  "metadata": {...}
}
```

**預設路徑**: `data/memory/`
**可配置**: 是（`storage_dir` 參數）

---

### 2. data/vectors/memory/（EvoMem 存儲）

**用途**: EvoMem 向量資料庫持久化目錄
**技術**: ChromaDB
**功能**: 語義搜尋、跨對話記憶

**檔案**:
- `chroma.sqlite3` - SQLite 資料庫
- 向量索引檔案

**預設路徑**: `data/vectors/memory/`
**可配置**: 是（`persist_directory` 參數）

---

## 🗂️ 檔案類型索引

### 按功能分類

#### 📖 文檔類（.md）
- `README.md` - 快速入門
- `UNIVERSAL_STORAGE_USER_GUIDE.md` - 詳細指南
- `DIRECTORY_STRUCTURE.md` - 本文件
- `MEMORY_HANDOFF_USER_GUIDE.md` - 記憶交接指南
- `MEMORY_HANDOFF_COMPLETION_REPORT.md` - 完成報告
- `HANDOFF_*.md` - 自動生成交接文檔
- `TODO_NEXT.md` - 自動生成待辦事項

#### 🔧 核心代碼（.py）
- `universal_memory_storage.py` - 通用存儲核心
- `memory_handoff_integration.py` - 記憶交接整合
- `compress_context.py` - 壓縮模組
- `context7_integration.py` - Context7 整合
- `exa_integration.py` - Exa 整合

#### 🧪 測試與範例（.py）
- `test_universal_storage.py` - 測試套件
- `example_usage.py` - 範例代碼

#### 💾 資料檔案（.json, .sqlite3）
- `mem_*.json` - JSON 記憶檔案
- `chroma.sqlite3` - ChromaDB 資料庫

---

## 📈 檔案大小與行數

| 檔案 | 類型 | 行數 | 大小 | 用途 |
|------|------|------|------|------|
| `universal_memory_storage.py` | 核心 | 487 | ~25KB | 通用存儲架構 |
| `memory_handoff_integration.py` | 核心 | 750+ | ~35KB | 記憶交接系統 |
| `test_universal_storage.py` | 測試 | 360 | ~15KB | 測試套件 |
| `example_usage.py` | 範例 | 400+ | ~18KB | 範例代碼 |
| `README.md` | 文檔 | 200+ | ~10KB | 快速入門 |
| `UNIVERSAL_STORAGE_USER_GUIDE.md` | 文檔 | 800+ | ~45KB | 詳細指南 |

---

## 🔄 版本管理

### 版本號規則

採用語義化版本 (Semantic Versioning):

```
主版本.次版本.修訂版本
  ↓      ↓      ↓
 2  .   0  .   0
```

- **主版本**: 不相容的 API 變更
- **次版本**: 向後兼容的功能新增
- **修訂版本**: 向後兼容的問題修正

### 當前版本

- **universal_memory_storage.py**: v2.0.0
- **memory_handoff_integration.py**: v2.0.0
- **整體專案**: v2.0.0

---

## 📞 支援與維護

### 文檔更新

- **頻率**: 每次主要版本更新
- **維護者**: Claude Code + zycaskevin
- **最後更新**: 2025-11-16

### 問題回報

如遇到問題，請檢查：
1. [故障排除](UNIVERSAL_STORAGE_USER_GUIDE.md#故障排除)
2. [常見場景](UNIVERSAL_STORAGE_USER_GUIDE.md#常見場景)
3. [測試結果](test_universal_storage.py)

---

**文檔版本**: 2.0.0
**最後更新**: 2025-11-16
**維護者**: Claude Code + zycaskevin
