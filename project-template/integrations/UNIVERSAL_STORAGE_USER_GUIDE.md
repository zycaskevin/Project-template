# 通用記憶存儲系統 - 完整使用指南

**版本**: 2.0.0
**最後更新**: 2025-11-16

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [快速開始](#快速開始)
3. [核心概念](#核心概念)
4. [API 參考](#api-參考)
5. [配置選項](#配置選項)
6. [進階用法](#進階用法)
7. [常見場景](#常見場景)
8. [故障排除](#故障排除)
9. [最佳實踐](#最佳實踐)

---

## 系統概述

### 什麼是通用記憶存儲系統？

通用記憶存儲系統提供統一的記憶存儲介面，支援多種存儲後端（EvoMem、JSON 等），並具備自動降級能力，確保系統在任何環境下都能正常運作。

### 為什麼需要它？

**問題**：
- 不同專案使用不同記憶系統（Mem0、EvoMem、自建等）
- 硬編碼存儲邏輯難以擴展
- 開發環境與生產環境配置不一致

**解決方案**：
- ✅ 統一介面 - 一套 API 支援所有後端
- ✅ 自動降級 - EvoMem 不可用時自動降至 JSON
- ✅ 零配置 - 開箱即用，自動檢測最佳後端
- ✅ 靈活擴展 - 輕鬆新增新存儲後端

### 設計原則

基於 **Red Team vs Blue Team** 對抗性分析：

1. **最小可行方案 (MVP)** - 優先實作 2 個核心後端（EvoMem + JSON）
2. **漸進增強** - 保留介面擴展性，延後非必要功能
3. **零配置預設** - `create_storage()` 自動檢測
4. **自動降級** - 確保系統在任何環境下可用

---

## 快速開始

### 安裝

無需額外安裝！系統已整合到 `project-template/integrations/`。

**可選依賴**（若需要 EvoMem 完整功能）：

```bash
# 安裝 EvoMem（語義搜尋功能）
pip install -e EvoMem/
```

### 5 分鐘快速體驗

#### 1. 使用記憶交接系統（整合方式）

```python
from memory_handoff_integration import MemoryHandoffOrchestrator

# 創建 Orchestrator（自動檢測存儲後端）
orchestrator = MemoryHandoffOrchestrator()

# 執行記憶交接
result = orchestrator.execute_handoff(
    conversation="對話內容...",
    current_tokens=145000,
    max_tokens=200000,
    todos=[
        {"content": "完成功能 A", "status": "completed"},
        {"content": "測試功能 B", "status": "in_progress"}
    ],
    metadata={
        "project": "我的專案",
        "phase": "P1-5",
        "phase_completed": True
    }
)

print(f"記憶 ID: {result['memory_id']}")
print(f"交接文檔: {result['handoff_doc']}")
```

#### 2. 直接使用存儲 API

```python
from universal_memory_storage import create_storage

# 創建存儲（零配置）
storage = create_storage()

# 存儲記憶
memory_item = {
    "id": "mem_20251116_100000",
    "type": "handoff",
    "timestamp": "2025-11-16T10:00:00Z",
    "content": "記憶內容...",
    "metadata": {"project": "測試專案"}
}

memory_id = storage.store(memory_item)
print(f"已存儲: {memory_id}")

# 檢索記憶
retrieved = storage.retrieve(memory_id)
print(f"檢索成功: {retrieved['id']}")
```

---

## 核心概念

### 1. 存儲能力等級 (StorageCapability)

系統定義兩種能力等級：

| 等級 | 功能 | 後端範例 |
|------|------|---------|
| **FULL** | 存儲 + 檢索 + 語義搜尋 + 跨對話記憶 | EvoMem |
| **BASIC** | 存儲 + 檢索 | JSON |

**檢查能力**：

```python
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    print("支援語義搜尋")
    results = storage.search("關鍵字", n_results=5)
else:
    print("僅支援基礎存儲")
```

### 2. 自動降級機制

系統按順序嘗試後端：

```
1. 嘗試 EvoMem (FULL)
   ↓ 失敗
2. 降級至 JSON (BASIC)
   ↓ 失敗
3. 拋出錯誤
```

**降級輸出範例**：

```
[Auto-Detection] Detecting available memory storage backend...
  [Trying] EvoMemStorage (FULL capability)...
  [FAILED] EvoMemStorage: EvoMem not available
  [Trying] JSONStorage (BASIC capability)...
  [FALLBACK] Degraded to JSONStorage (semantic search unavailable)
```

### 3. 記憶項目結構

所有記憶項目遵循統一結構：

```python
memory_item = {
    # 必須欄位
    "id": "mem_20251116_100000",
    "type": "handoff",
    "timestamp": "2025-11-16T10:00:00Z",

    # 短期記憶
    "session_memory": {
        "sessionIntent": ["任務 1", "任務 2"],
        "todos": [...],
        "decisions": [...]
    },

    # 長期記憶
    "long_term_memory": {
        "learnings": [...],
        "code_patterns": [...]
    },

    # 元數據
    "metadata": {
        "project": "專案名稱",
        "phase": "階段",
        "compression_ratio": 0.95,
        "quality_score": 9.0
    }
}
```

---

## API 參考

### MemoryStorageInterface（抽象介面）

所有存儲後端必須實作此介面。

#### 核心方法

```python
class MemoryStorageInterface(ABC):
    @property
    @abstractmethod
    def capability(self) -> StorageCapability:
        """宣告能力等級"""
        pass

    @abstractmethod
    def store(self, memory_item: Dict) -> str:
        """存儲記憶

        Args:
            memory_item: 記憶項目

        Returns:
            memory_id: 唯一識別碼
        """
        pass

    @abstractmethod
    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """檢索記憶

        Args:
            memory_id: 記憶 ID

        Returns:
            記憶項目或 None
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """健康檢查

        Returns:
            True if healthy, False otherwise
        """
        pass
```

#### 可選方法

```python
    def search(self, query: str, **kwargs) -> List[Dict]:
        """語義搜尋（可選功能）

        預設實作：返回空列表（不支援搜尋）
        FULL capability 後端可覆寫此方法

        Args:
            query: 搜尋查詢
            **kwargs: 後端特定參數

        Returns:
            相關記憶列表
        """
        return []
```

---

### EvoMemStorage（FULL 後端）

完整功能記憶存儲，支援語義搜尋。

#### 初始化

```python
from universal_memory_storage import EvoMemStorage

storage = EvoMemStorage(
    persist_directory="data/vectors/memory"
)
```

#### 使用範例

```python
# 存儲
memory_id = storage.store(memory_item)

# 檢索
retrieved = storage.retrieve(memory_id)

# 語義搜尋（EvoMem 特有）
results = storage.search(
    query="優化效能",
    n_results=5
)

for result in results:
    print(f"相關記憶: {result['metadata']['memory_id']}")
```

---

### JSONStorage（BASIC 後端）

基礎檔案存儲，零依賴，穩定可靠。

#### 初始化

```python
from universal_memory_storage import JSONStorage

storage = JSONStorage(
    storage_dir="data/memory"
)
```

#### 使用範例

```python
# 存儲
memory_id = storage.store(memory_item)
# 檔案位置: data/memory/mem_20251116_100000.json

# 檢索
retrieved = storage.retrieve(memory_id)

# 搜尋（返回空列表）
results = storage.search("any query")
# results == []
```

---

### MemoryStorageFactory（工廠）

自動檢測與創建存儲後端。

#### create() - 主要方法

```python
from universal_memory_storage import MemoryStorageFactory

# 零配置（推薦）
storage = MemoryStorageFactory.create()

# 指定後端
storage = MemoryStorageFactory.create({
    "type": "json"
})

# 完整配置
storage = MemoryStorageFactory.create({
    "type": "evomem",
    "evomem": {
        "persist_directory": "custom/path"
    }
})
```

---

## 配置選項

### 選項 1: 零配置（推薦）

```python
storage = create_storage()
```

**行為**：
- 自動嘗試 EvoMem → JSON
- 使用預設路徑
- 適用於 99% 場景

---

### 選項 2: 指定後端類型

```python
# 僅使用 JSON（開發環境）
storage = create_storage({"type": "json"})

# 僅使用 EvoMem（生產環境）
storage = create_storage({"type": "evomem"})
```

---

### 選項 3: 完整配置

```python
# JSON 自訂路徑
storage = create_storage({
    "type": "json",
    "json": {
        "storage_dir": "custom/memory/path"
    }
})

# EvoMem 自訂配置
storage = create_storage({
    "type": "evomem",
    "evomem": {
        "persist_directory": "data/vectors/custom_memory"
    }
})
```

---

## 進階用法

### 1. 檢查存儲能力

```python
storage = create_storage()

print(f"後端類型: {type(storage).__name__}")
print(f"能力等級: {storage.capability.value}")

if storage.capability == StorageCapability.FULL:
    print("✅ 支援語義搜尋")
else:
    print("❌ 僅支援基礎存儲")
```

### 2. 條件性使用語義搜尋

```python
def search_memories(query: str) -> List[Dict]:
    """智能搜尋：使用語義搜尋或降級至空結果"""
    storage = create_storage()

    if storage.capability == StorageCapability.FULL:
        # 使用語義搜尋
        return storage.search(query, n_results=10)
    else:
        # 降級：返回空結果或使用簡單篩選
        print("[WARNING] 語義搜尋不可用，返回空結果")
        return []
```

### 3. 批次處理

```python
def batch_store(memory_items: List[Dict]) -> List[str]:
    """批次存儲記憶"""
    storage = create_storage()
    memory_ids = []

    for item in memory_items:
        memory_id = storage.store(item)
        memory_ids.append(memory_id)

    print(f"已存儲 {len(memory_ids)} 個記憶")
    return memory_ids
```

### 4. 健康檢查與監控

```python
def monitor_storage_health():
    """監控存儲健康狀態"""
    storage = create_storage()

    if storage.health_check():
        print(f"✅ 存儲正常: {type(storage).__name__}")
        return True
    else:
        print(f"❌ 存儲異常: {type(storage).__name__}")
        return False
```

---

## 常見場景

### 場景 1: 記憶交接（整合使用）

```python
from memory_handoff_integration import MemoryHandoffOrchestrator

# 創建 Orchestrator
orchestrator = MemoryHandoffOrchestrator()

# 執行記憶交接
result = orchestrator.execute_handoff(
    conversation=long_conversation_text,
    current_tokens=145000,
    max_tokens=200000,
    todos=current_todos,
    metadata={
        "project": "我的專案",
        "phase": "P1-5",
        "phase_completed": True
    }
)

# 檢查結果
if result['success']:
    print(f"✅ 交接成功")
    print(f"   記憶 ID: {result['memory_id']}")
    print(f"   壓縮率: {result['compression_ratio']:.1%}")
    print(f"   交接文檔: {result['handoff_doc']}")
else:
    print(f"❌ 交接失敗: {result.get('reason')}")
```

---

### 場景 2: 跨對話記憶複用（EvoMem）

```python
from universal_memory_storage import create_storage, StorageCapability

storage = create_storage({"type": "evomem"})

if storage.capability == StorageCapability.FULL:
    # 搜尋歷史相關記憶
    results = storage.search(
        query="效能優化 PostgreSQL",
        n_results=3
    )

    print(f"找到 {len(results)} 個相關記憶：")
    for result in results:
        print(f"  - {result['metadata']['memory_id']}")
        print(f"    專案: {result['metadata'].get('project')}")
        print(f"    相關度: {result.get('score', 'N/A')}")
else:
    print("⚠️ EvoMem 不可用，無法使用語義搜尋")
```

---

### 場景 3: 開發環境 vs 生產環境

```python
import os

def create_env_aware_storage():
    """根據環境自動選擇存儲後端"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        # 生產環境：強制使用 EvoMem
        return create_storage({"type": "evomem"})
    else:
        # 開發環境：使用 JSON（快速、無依賴）
        return create_storage({"type": "json"})

storage = create_env_aware_storage()
```

---

### 場景 4: 備份與恢復

```python
def backup_all_memories(output_dir: str):
    """備份所有記憶到 JSON 檔案"""
    from pathlib import Path
    import json

    storage = create_storage()
    backup_dir = Path(output_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 假設有記憶 ID 列表
    memory_ids = ["mem_001", "mem_002", "mem_003"]

    for memory_id in memory_ids:
        memory = storage.retrieve(memory_id)
        if memory:
            backup_file = backup_dir / f"{memory_id}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
            print(f"✅ 已備份: {memory_id}")
```

---

## 故障排除

### 問題 1: EvoMem 初始化失敗

**錯誤訊息**:
```
[FAILED] EvoMemStorage: EvoMem not available: No module named 'core'
```

**解決方案**:
```bash
# 安裝 EvoMem
pip install -e EvoMem/

# 或使用 JSON 降級（自動）
# 系統會自動降級至 JSONStorage
```

---

### 問題 2: JSON 檔案權限錯誤

**錯誤訊息**:
```
PermissionError: [Errno 13] Permission denied: 'data/memory/mem_xxx.json'
```

**解決方案**:
```python
# 檢查目錄權限
import os
from pathlib import Path

storage_dir = Path("data/memory")
if not os.access(storage_dir, os.W_OK):
    print("❌ 目錄不可寫")
    # 修改權限或更換目錄
    storage = create_storage({
        "type": "json",
        "json": {"storage_dir": "/tmp/memory"}
    })
```

---

### 問題 3: 記憶 ID 不存在

**錯誤**:
```python
retrieved = storage.retrieve("non_existent_id")
# retrieved == None
```

**解決方案**:
```python
memory_id = "mem_xxx"
retrieved = storage.retrieve(memory_id)

if retrieved is None:
    print(f"❌ 記憶 {memory_id} 不存在")
else:
    print(f"✅ 找到記憶: {retrieved['id']}")
```

---

### 問題 4: 搜尋功能不可用

**問題**: JSON 後端不支援 `search()`

**解決方案**:
```python
storage = create_storage()

if storage.capability == StorageCapability.FULL:
    results = storage.search("query")
else:
    print("⚠️ 當前後端不支援語義搜尋")
    print("   安裝 EvoMem 以啟用此功能")
    # 使用替代方案（如遍歷檔案）
```

---

## 最佳實踐

### 1. 優先使用零配置

```python
# ✅ 推薦
storage = create_storage()

# ❌ 避免
storage = JSONStorage(storage_dir="data/memory")
```

**理由**: 零配置自動處理降級，確保系統在任何環境下可用。

---

### 2. 檢查能力再使用功能

```python
# ✅ 推薦
if storage.capability == StorageCapability.FULL:
    results = storage.search("query")
else:
    print("語義搜尋不可用")

# ❌ 避免
results = storage.search("query")  # JSON 後端會返回 []
```

**理由**: 明確檢查能力，避免誤解空結果原因。

---

### 3. 使用環境變數控制配置

```python
import os

storage_type = os.getenv("STORAGE_TYPE", "auto")
storage = create_storage({"type": storage_type})
```

**理由**: 易於在不同環境間切換，無需修改代碼。

---

### 4. 記憶 ID 使用時間戳

```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
memory_id = f"mem_{timestamp}"
```

**理由**: 確保 ID 唯一性，並帶有時間資訊便於排序。

---

### 5. 定期健康檢查

```python
import schedule

def health_check():
    storage = create_storage()
    if not storage.health_check():
        # 發送警報或切換後端
        print("❌ 存儲健康檢查失敗")

# 每小時檢查一次
schedule.every(1).hours.do(health_check)
```

---

## 附錄

### A. 完整配置範例

```python
# 生產環境配置
production_config = {
    "type": "evomem",
    "evomem": {
        "persist_directory": "data/vectors/production_memory"
    }
}

# 開發環境配置
development_config = {
    "type": "json",
    "json": {
        "storage_dir": "data/memory/dev"
    }
}

# 測試環境配置
test_config = {
    "type": "json",
    "json": {
        "storage_dir": "/tmp/test_memory"
    }
}
```

---

### B. 記憶項目完整範例

```python
complete_memory_item = {
    "id": "mem_20251116_100000",
    "type": "handoff",
    "timestamp": "2025-11-16T10:00:00.000000Z",

    "session_memory": {
        "sessionIntent": [
            "實作通用記憶存儲",
            "整合到現有系統"
        ],
        "playByPlay": [
            {"action": "設計架構", "timestamp": "10:00:00"},
            {"action": "實作代碼", "timestamp": "10:30:00"}
        ],
        "todos": [
            {
                "content": "創建 universal_memory_storage.py",
                "status": "completed"
            }
        ],
        "decisions": [
            {
                "decision": "使用 2 層降級",
                "rationale": "簡化複雜度",
                "source": "對抗性分析"
            }
        ]
    },

    "long_term_memory": {
        "learnings": [
            {
                "pattern": "MVP 優於過度設計",
                "context": "Red Team 分析",
                "impact": "high"
            }
        ],
        "code_patterns": [
            {
                "pattern": "Factory Pattern",
                "usage": "自動檢測存儲後端"
            }
        ]
    },

    "metadata": {
        "project": "專案啟動文檔專案",
        "phase": "P1-Universal-Storage",
        "compression_ratio": 0.95,
        "quality_score": 9.5,
        "tags": ["storage", "architecture", "mvp"]
    }
}
```

---

**文檔版本**: 2.0.0
**最後更新**: 2025-11-16
**維護者**: Claude Code + zycaskevin
