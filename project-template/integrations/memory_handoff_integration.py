"""
Memory Handoff Integration Module

Purpose: Xiaoji's (小憶) automated memory handoff using compression mechanism
Version: 2.0.0 (Phase 1 - Universal Storage Integration)
Author: Claude Code + zycaskevin

Architecture: Hybrid Approach (Option D from XIAOJI_MEMORY_HANDOFF_DESIGN.md)
- Layer 1: Agent (xiaoji-memory-keeper.md) - Protocol definition
- Layer 2: Integration (this file) - Core orchestration
- Layer 3: Output Style - Minimal changes (triggers)
- Layer 4: Hook - Automatic triggers (optional)

Integration Strategy:
1. Detect trigger conditions (Token 70%, TODO completed, phase done)
2. Extract & compress context (using compress_context.py)
3. Enhance with Context7 + Exa (using existing integrations)
4. Store in Universal Memory (EvoMem or JSON fallback)
5. Generate handoff documents (HANDOFF_xxx.md, TODO_NEXT.md)

CHANGELOG v2.0.0:
- Integrated universal_memory_storage.py for flexible storage backends
- Support auto-degradation: EvoMem → JSON
- Removed hardcoded JSON storage, now uses MemoryStorageFactory

Design Reference:
- XIAOJI_MEMORY_HANDOFF_DESIGN.md
- universal_memory_storage.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Import existing compression and enhancement modules
try:
    # Add scripts and integrations to path
    scripts_dir = Path(__file__).parent.parent / "scripts"
    integrations_dir = Path(__file__).parent

    sys.path.insert(0, str(scripts_dir))
    sys.path.insert(0, str(integrations_dir))

    from compress_context import ContextCompressor, estimate_tokens
    from context7_integration import enhance_with_context7
    from exa_integration import enhance_with_exa

    # Import universal memory storage (v2.0.0)
    from universal_memory_storage import (
        MemoryStorageFactory,
        MemoryStorageInterface,
        StorageCapability
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


# ============================================================
# Trigger Detection (Step 1)
# ============================================================
class MemoryHandoffTrigger:
    """
    自動偵測記憶交接觸發條件

    觸發條件:
    - Token 使用達 70%
    - 完成 5 個 TODO
    - 階段完成 (如 TDD Red/Green/Refactor)
    - 經過 1 小時
    - 3 次 Git commit
    """

    # Default thresholds (可調整)
    TRIGGER_THRESHOLDS = {
        "token_usage": 0.70,        # 70% Token 使用
        "todo_completed": 5,        # 完成 5 個 TODO
        "time_elapsed": 3600,       # 1 小時經過 (秒)
        "phase_completed": True,    # 階段完成
        "git_commits": 3            # 3 次 commit
    }

    def __init__(self, thresholds: Optional[Dict] = None):
        """
        Initialize trigger detector

        Args:
            thresholds: Custom thresholds (optional)
        """
        if thresholds:
            self.thresholds = {**self.TRIGGER_THRESHOLDS, **thresholds}
        else:
            self.thresholds = self.TRIGGER_THRESHOLDS

    def should_trigger_handoff(self, context: Dict) -> Tuple[bool, List[str]]:
        """
        判斷是否應該觸發記憶交接

        Args:
            context: {
                'current_tokens': int,
                'max_tokens': int,
                'todos': List[Dict],  # [{"status": "completed", "task": "..."}]
                'phase_completed': bool,
                'time_elapsed': Optional[int],
                'git_commits': Optional[int]
            }

        Returns:
            Tuple[bool, List[str]]: (should_trigger, reasons)
        """
        triggers = []

        # Check 1: Token 使用率
        current_tokens = context.get('current_tokens', 0)
        max_tokens = context.get('max_tokens', 200000)

        if max_tokens > 0:
            token_ratio = current_tokens / max_tokens
            if token_ratio >= self.thresholds['token_usage']:
                triggers.append(f'token_usage ({token_ratio:.1%})')

        # Check 2: TODO 完成數
        todos = context.get('todos', [])
        if todos:
            completed_count = len([t for t in todos if t.get('status') == 'completed'])
            if completed_count >= self.thresholds['todo_completed']:
                triggers.append(f'todo_completed ({completed_count})')

        # Check 3: 階段完成
        if context.get('phase_completed'):
            triggers.append('phase_completed')

        # Check 4: 時間經過
        time_elapsed = context.get('time_elapsed')
        if time_elapsed and time_elapsed >= self.thresholds['time_elapsed']:
            triggers.append(f'time_elapsed ({time_elapsed}s)')

        # Check 5: Git commits
        git_commits = context.get('git_commits')
        if git_commits and git_commits >= self.thresholds['git_commits']:
            triggers.append(f'git_commits ({git_commits})')

        # 任一觸發條件滿足即觸發
        should_trigger = len(triggers) > 0

        return should_trigger, triggers


# ============================================================
# Information Extraction (Step 2)
# ============================================================
class InformationExtractor:
    """
    從對話中提取關鍵資訊

    提取內容:
    - Session intent, play-by-play, artifacts, breadcrumbs (via ContextCompressor)
    - TODOs (狀態追蹤)
    - Decisions (關鍵決策)
    - Code patterns (代碼模式)
    - Learnings (學習與洞察)
    """

    def __init__(self):
        self.compressor = ContextCompressor()

    def extract(self, conversation: str, todos: List[Dict]) -> Dict:
        """
        提取關鍵資訊並壓縮

        Args:
            conversation: 完整對話內容
            todos: TODO 列表

        Returns:
            提取的資訊 (包含壓縮的上下文)
        """
        # 使用現有的壓縮器
        compressed = self.compressor.compress(conversation)

        # 額外提取
        extracted = {
            **compressed,
            "todos": todos,
            "decisions": self._extract_decisions(conversation),
            "code_patterns": self._extract_code_patterns(compressed['breadcrumbs']),
            "learnings": self._extract_learnings(compressed['playByPlay'])
        }

        return extracted

    def _extract_decisions(self, conversation: str) -> List[Dict]:
        """
        提取關鍵決策

        尋找模式:
        - "Decision:", "Decided to", "選擇"
        - "Rationale:", "理由", "因為"
        """
        decisions = []

        # Simple extraction (可增強為 LLM-based)
        keywords = ['decision:', 'decided to', '選擇', 'rationale:', '理由']

        lines = conversation.split('\n')
        current_decision = None

        for line in lines:
            line_lower = line.lower()

            # Check for decision start
            if any(kw in line_lower for kw in ['decision:', 'decided to', '選擇']):
                if current_decision:
                    decisions.append(current_decision)

                current_decision = {
                    "decision": line.strip(),
                    "rationale": "",
                    "source": "conversation"
                }

            # Check for rationale
            elif current_decision and any(kw in line_lower for kw in ['rationale:', '理由', '因為']):
                current_decision["rationale"] = line.strip()

        # Add last decision
        if current_decision:
            decisions.append(current_decision)

        return decisions[:10]  # Limit to top 10

    def _extract_code_patterns(self, breadcrumbs: List[str]) -> List[Dict]:
        """
        從 breadcrumbs 提取代碼模式

        例如:
        - function:sort_by_priority → 優先級排序模式
        - class:MemoryHandoff → 記憶交接模式
        """
        patterns = []

        # Group by pattern type
        functions = [b for b in breadcrumbs if b.startswith('function:')]
        classes = [b for b in breadcrumbs if b.startswith('class:')]

        # Extract patterns (top 5)
        for func in functions[:5]:
            identifier = func.split(':', 1)[1]
            patterns.append({
                "pattern": identifier,
                "type": "function",
                "use_case": f"Function pattern: {identifier}"
            })

        for cls in classes[:5]:
            identifier = cls.split(':', 1)[1]
            patterns.append({
                "pattern": identifier,
                "type": "class",
                "use_case": f"Class pattern: {identifier}"
            })

        return patterns

    def _extract_learnings(self, play_by_play: List[str]) -> List[Dict]:
        """
        從 play-by-play 提取學習與洞察

        尋找模式:
        - "Fixed", "Optimized" → 解決方案
        - "Implemented", "Created" → 新功能
        """
        learnings = []

        # Keywords indicating learnings
        solution_keywords = ['fixed', 'resolved', 'solved', '修復']
        optimization_keywords = ['optimized', 'improved', '優化']
        implementation_keywords = ['implemented', 'created', '實作', '創建']

        for action in play_by_play:
            action_lower = action.lower()

            # Solution learning
            if any(kw in action_lower for kw in solution_keywords):
                learnings.append({
                    "pattern": action,
                    "type": "solution",
                    "context": "Problem resolution"
                })

            # Optimization learning
            elif any(kw in action_lower for kw in optimization_keywords):
                learnings.append({
                    "pattern": action,
                    "type": "optimization",
                    "context": "Performance improvement"
                })

            # Implementation learning
            elif any(kw in action_lower for kw in implementation_keywords):
                learnings.append({
                    "pattern": action,
                    "type": "implementation",
                    "context": "New feature creation"
                })

        return learnings[:10]  # Limit to top 10


# ============================================================
# Enhancement (Step 3)
# ============================================================
class ContextEnhancer:
    """
    使用 Context7 + Exa 增強壓縮內容
    """

    def enhance(self, compressed: Dict,
                use_context7: bool = True,
                use_exa: bool = True,
                context7_tokens: int = 500,
                exa_tokens: int = 300) -> Dict:
        """
        增強壓縮內容

        Args:
            compressed: 壓縮的上下文
            use_context7: 啟用 Context7
            use_exa: 啟用 Exa
            context7_tokens: Context7 Token 預算
            exa_tokens: Exa Token 預算

        Returns:
            增強的上下文
        """
        enhanced = compressed.copy()

        if not DEPENDENCIES_AVAILABLE:
            print("[WARNING] Enhancement dependencies not available")
            return enhanced

        # Step 3.1: Context7 文檔增強
        if use_context7:
            try:
                enhanced = enhance_with_context7(
                    enhanced,
                    use_mcp=False,  # 使用 mock (暫不需要真實 MCP)
                    max_tokens=context7_tokens
                )
                print(f"  [OK] Context7: +{enhanced.get('enhancement', {}).get('total_tokens_added', 0)} tokens")
            except Exception as e:
                print(f"  [WARNING] Context7 enhancement failed: {e}")

        # Step 3.2: Exa 最佳實踐增強
        if use_exa:
            try:
                enhanced = enhance_with_exa(
                    enhanced,
                    use_api=False,  # 使用 mock
                    max_tokens=exa_tokens
                )
                exa_added = enhanced.get('enhancement', {}).get('exa_tokens_added', 0)
                print(f"  [OK] Exa: +{exa_added} tokens")
            except Exception as e:
                print(f"  [WARNING] Exa enhancement failed: {e}")

        return enhanced


# ============================================================
# Storage (Step 4) - v2.0.0 Universal Storage Wrapper
# ============================================================
class MemoryStorage:
    """
    記憶存儲包裝器（v2.0.0 - Universal Storage Integration）

    功能變更:
    - v1.0.0: 硬編碼 JSON 存儲
    - v2.0.0: 使用 MemoryStorageFactory 自動檢測後端
      - 優先: EvoMem (FULL capability - 語義搜尋)
      - 降級: JSON (BASIC capability - 基礎存儲)

    這個包裝器保持向後兼容，同時提供新的通用存儲能力。
    """

    def __init__(self, storage_config: Optional[Dict] = None):
        """
        Initialize storage with universal backend

        Args:
            storage_config: 存儲配置（可選）
                {
                    "type": "auto" | "evomem" | "json",
                    "evomem": {...},
                    "json": {"storage_dir": "data/memory"}
                }

                若未提供，使用零配置自動檢測
        """
        if storage_config is None:
            # Zero-config: Auto-detect with default JSON fallback dir
            storage_config = {
                "type": "auto",
                "json": {"storage_dir": "data/memory"}
            }

        # Create storage backend using factory
        self.backend: MemoryStorageInterface = MemoryStorageFactory.create(storage_config)

        # Log capability
        print(f"  [INFO] Memory storage initialized: {type(self.backend).__name__} "
              f"({self.backend.capability.value})")

    def store(self, memory_item: Dict) -> str:
        """
        存儲記憶項目（使用通用後端）

        Args:
            memory_item: 記憶項目

        Returns:
            記憶 ID

        Note:
            v2.0.0: 自動檢測 memory_item['id']，若不存在則生成
        """
        # Generate memory ID if not present
        if 'id' not in memory_item:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            memory_item['id'] = f"mem_{timestamp}"

        # Store using backend
        memory_id = self.backend.store(memory_item)

        return memory_id

    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """
        取回記憶項目（使用通用後端）

        Args:
            memory_id: 記憶 ID

        Returns:
            記憶項目 or None
        """
        return self.backend.retrieve(memory_id)

    def search(self, query: str, **kwargs) -> List[Dict]:
        """
        語義搜尋記憶（v2.0.0 新功能）

        Args:
            query: 搜尋查詢
            **kwargs: 後端特定參數

        Returns:
            相關記憶列表（若後端不支援，返回空列表）

        Note:
            僅 FULL capability 後端（如 EvoMem）支援此功能
            BASIC capability 後端（如 JSON）返回空列表
        """
        return self.backend.search(query, **kwargs)

    @property
    def capability(self) -> StorageCapability:
        """
        取得當前存儲後端的能力等級

        Returns:
            StorageCapability: FULL or BASIC
        """
        return self.backend.capability


# ============================================================
# Documentation (Step 5)
# ============================================================
class HandoffDocumenter:
    """
    生成人類可讀的交接文檔
    """

    def generate_handoff(self, memory_item: Dict,
                        output_dir: str = ".") -> str:
        """
        生成交接文檔

        Args:
            memory_item: 記憶項目
            output_dir: 輸出目錄

        Returns:
            文檔檔名
        """
        # Generate filename
        phase = memory_item.get('metadata', {}).get('phase', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"HANDOFF_{phase}_{timestamp}.md"

        # Generate content
        doc_content = self._format_handoff_document(memory_item)

        # Write file
        filepath = Path(output_dir) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        print(f"  [OK] Handoff doc: {filepath}")

        return filename

    def generate_todo_next(self, memory_item: Dict,
                          output_dir: str = ".") -> str:
        """
        生成下一步 TODO 文檔

        Args:
            memory_item: 記憶項目
            output_dir: 輸出目錄

        Returns:
            文檔檔名
        """
        filename = "TODO_NEXT.md"

        # Extract pending TODOs
        todos = memory_item.get('session_memory', {}).get('todos', [])
        pending_todos = [t for t in todos if t.get('status') == 'pending']

        # Generate content
        doc_content = f"""# 下一步 TODO

**生成時間**: {datetime.now(timezone.utc).isoformat()}
**專案**: {memory_item.get('metadata', {}).get('project', 'Unknown')}
**階段**: {memory_item.get('metadata', {}).get('phase', 'Unknown')}

---

## 🔄 待辦事項

"""

        for i, todo in enumerate(pending_todos, 1):
            doc_content += f"{i}. **{todo.get('task', 'Unknown task')}**\n"
            if 'activeForm' in todo:
                doc_content += f"   - 進行中: {todo['activeForm']}\n"
            doc_content += "\n"

        if not pending_todos:
            doc_content += "✅ 無待辦事項\n\n"

        doc_content += f"""---

*自動生成於 {datetime.now(timezone.utc).isoformat()} by 小憶 (Memory Keeper)*
"""

        # Write file
        filepath = Path(output_dir) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        print(f"  [OK] TODO doc: {filepath}")

        return filename

    def _format_handoff_document(self, memory_item: Dict) -> str:
        """格式化交接文檔"""

        session = memory_item.get('session_memory', {})
        longterm = memory_item.get('long_term_memory', {})
        metadata = memory_item.get('metadata', {})

        doc = f"""# 記憶交接文檔

**時間**: {memory_item.get('timestamp', 'Unknown')}
**記憶 ID**: {memory_item.get('id', 'Unknown')}
**專案**: {metadata.get('project', 'Unknown')}
**階段**: {metadata.get('phase', 'Unknown')}

---

## 📋 任務摘要

**任務目標**:
"""

        for intent in session.get('sessionIntent', []):
            doc += f"- {intent}\n"

        doc += "\n**完成事項**:\n"
        for action in session.get('playByPlay', []):
            doc += f"- ✅ {action}\n"

        doc += "\n---\n\n## 📁 產出物\n\n**檔案**:\n"
        for artifact in session.get('artifacts', []):
            doc += f"- [{artifact}]({artifact})\n"

        doc += "\n---\n\n## 🔑 關鍵決策\n\n"
        for decision in session.get('decisions', []):
            doc += f"**決策**: {decision.get('decision', 'Unknown')}\n"
            doc += f"- **理由**: {decision.get('rationale', 'N/A')}\n"
            doc += f"- **來源**: {decision.get('source', 'N/A')}\n\n"

        doc += "---\n\n## 💡 學習與洞察\n\n"
        for learning in longterm.get('learnings', []):
            doc += f"**模式**: {learning.get('pattern', 'Unknown')}\n"
            doc += f"- **類型**: {learning.get('type', 'N/A')}\n"
            doc += f"- **情境**: {learning.get('context', 'N/A')}\n\n"

        doc += f"""---

## 📊 效能指標

- **Token 壓縮**: {metadata.get('token_before', 0):,} → {metadata.get('token_after', 0):,} ({metadata.get('compression_ratio', 0) * 100:.1f}% 壓縮)
- **品質評分**: {metadata.get('quality_score', 0)}/10

---

*自動生成於 {memory_item.get('timestamp', 'Unknown')} by 小憶 (Memory Keeper)*
"""

        return doc


# ============================================================
# Main Orchestrator
# ============================================================
class MemoryHandoffOrchestrator:
    """
    小憶的記憶交接編排器

    執行完整的 5-Step 流程:
    1. 檢查觸發條件
    2. 提取關鍵資訊並壓縮
    3. 使用 Context7 + Exa 增強
    4. 存入記憶存儲
    5. 生成交接文檔
    """

    def __init__(self,
                 storage_dir: str = "data/memory",
                 output_dir: str = "."):
        """
        Initialize orchestrator

        Args:
            storage_dir: 記憶存儲目錄
            output_dir: 文檔輸出目錄
        """
        self.trigger = MemoryHandoffTrigger()
        self.extractor = InformationExtractor()
        self.enhancer = ContextEnhancer()
        self.storage = MemoryStorage(storage_dir)
        self.documenter = HandoffDocumenter()
        self.output_dir = output_dir

    def execute_handoff(self,
                       conversation: str,
                       current_tokens: int,
                       max_tokens: int,
                       todos: List[Dict],
                       metadata: Optional[Dict] = None) -> Dict:
        """
        執行完整的記憶交接流程

        Args:
            conversation: 完整對話內容
            current_tokens: 當前 Token 使用
            max_tokens: 最大 Token 限制
            todos: TODO 列表 [{"status": "completed", "task": "..."}]
            metadata: 額外 metadata (project, phase, etc.)

        Returns:
            {
                "success": bool,
                "compressed": Dict,
                "enhanced": Dict,
                "memory_id": str,
                "handoff_doc": str,
                "todo_next": str,
                "compression_ratio": float
            }
        """
        if metadata is None:
            metadata = {}

        print("\n[Xiaoji] 小憶: 開始記憶交接流程...")
        print("=" * 60)

        # Step 1: 檢查觸發條件
        print("\n[Step 1/5] 檢查觸發條件...")

        should_trigger, reasons = self.trigger.should_trigger_handoff({
            'current_tokens': current_tokens,
            'max_tokens': max_tokens,
            'todos': todos,
            'phase_completed': metadata.get('phase_completed', False)
        })

        if not should_trigger:
            print("  [INFO] 未達觸發條件")
            return {
                "success": False,
                "reason": "No trigger conditions met"
            }

        print(f"  [OK] 觸發原因: {', '.join(reasons)}")

        # Step 2: 提取 & 壓縮
        print("\n[Step 2/5] 提取關鍵資訊並壓縮...")
        compressed = self.extractor.extract(conversation, todos)

        token_before = current_tokens
        token_after = compressed['compressionMetadata']['compressedTokens']
        compression_ratio = compressed['compressionMetadata']['compressionRate']

        print(f"  [OK] 壓縮: {token_before:,} -> {token_after:,} tokens ({compression_ratio * 100:.1f}%)")

        # Step 3: 增強搜尋
        print("\n[Step 3/5] 使用 Context7 + Exa 增強...")
        enhanced = self.enhancer.enhance(compressed)

        # Step 4: 存入記憶
        print("\n[Step 4/5] 存入記憶存儲...")

        memory_item = self._build_memory_item(
            compressed, enhanced, metadata,
            token_before, token_after, compression_ratio
        )

        memory_id = self.storage.store(memory_item)

        # Step 5: 生成文檔
        print("\n[Step 5/5] 生成交接文檔...")
        handoff_doc = self.documenter.generate_handoff(memory_item, self.output_dir)
        todo_next = self.documenter.generate_todo_next(memory_item, self.output_dir)

        # Summary
        print("\n" + "=" * 60)
        print("[SUCCESS] 記憶交接完成!")
        print(f"   - 壓縮率: {compression_ratio * 100:.1f}%")
        print(f"   - 記憶 ID: {memory_id}")
        print(f"   - 交接文檔: {handoff_doc}")
        print(f"   - TODO 文檔: {todo_next}")
        print("=" * 60)

        return {
            "success": True,
            "compressed": compressed,
            "enhanced": enhanced,
            "memory_id": memory_id,
            "handoff_doc": handoff_doc,
            "todo_next": todo_next,
            "compression_ratio": compression_ratio,
            "token_before": token_before,
            "token_after": token_after
        }

    def _build_memory_item(self, compressed: Dict, enhanced: Dict,
                          metadata: Dict,
                          token_before: int, token_after: int,
                          compression_ratio: float) -> Dict:
        """構建記憶項目"""

        return {
            "type": "handoff",
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "from_agent": "general",
            "to_agent": "xiaoji",

            "session_memory": {
                "sessionIntent": compressed.get('sessionIntent', []),
                "playByPlay": compressed.get('playByPlay', []),
                "artifacts": compressed.get('artifacts', []),
                "breadcrumbs": compressed.get('breadcrumbs', []),
                "todos": compressed.get('todos', []),
                "decisions": compressed.get('decisions', [])
            },

            "long_term_memory": {
                "learnings": compressed.get('learnings', []),
                "best_practices": [],
                "code_patterns": compressed.get('code_patterns', [])
            },

            "enhancements": {
                "context7_docs": enhanced.get('enhancement', {}).get('context7_docs', []),
                "exa_search": enhanced.get('enhancement', {}).get('exa_search', [])
            },

            "metadata": {
                "project": metadata.get('project', 'Unknown'),
                "phase": metadata.get('phase', 'Unknown'),
                "token_before": token_before,
                "token_after": token_after,
                "compression_ratio": compression_ratio,
                "quality_score": 9.0  # TODO: 實作品質評估
            }
        }


# ============================================================
# CLI Interface (for testing)
# ============================================================
def main():
    """Test the memory handoff system"""
    print("Memory Handoff Integration - Test")
    print("=" * 60)

    # Test conversation
    test_conversation = """
User: 實作 P1-4.2 三大功能
Assistant: 開始實作框架優先級權重系統...
Created: context7_integration.py
Implemented: sort_libraries_by_priority function
Implemented: extract_version_from_breadcrumbs function
Implemented: enrich_libraries_with_dependencies function

Decision: 使用 5 層權重系統 (10/7-8/5-6/3/1)
Rationale: 平衡重要性與靈活性

Fixed: Version detection regex pattern
Optimized: Token allocation by priority

Created: test_p1_4_2_features.py
All tests passed (3/3)
"""

    # Test TODOs
    test_todos = [
        {"status": "completed", "task": "實作優先級系統", "activeForm": "實作優先級系統"},
        {"status": "completed", "task": "實作版本偵測", "activeForm": "實作版本偵測"},
        {"status": "completed", "task": "實作依賴關係", "activeForm": "實作依賴關係"},
        {"status": "completed", "task": "撰寫測試", "activeForm": "撰寫測試"},
        {"status": "completed", "task": "執行測試", "activeForm": "執行測試"},
        {"status": "pending", "task": "實作 P1-5 優化", "activeForm": "實作 P1-5 優化"}
    ]

    # Test metadata
    test_metadata = {
        "project": "專案啟動文檔專案",
        "phase": "P1-4.2",
        "phase_completed": True
    }

    # Execute handoff
    orchestrator = MemoryHandoffOrchestrator(
        storage_dir="data/memory",
        output_dir="."
    )

    result = orchestrator.execute_handoff(
        conversation=test_conversation,
        current_tokens=145000,
        max_tokens=200000,
        todos=test_todos,
        metadata=test_metadata
    )

    if result['success']:
        print("\n[SUCCESS] Memory handoff completed successfully!")
    else:
        print(f"\n[FAIL] Memory handoff failed: {result.get('reason', 'Unknown')}")


if __name__ == "__main__":
    if not DEPENDENCIES_AVAILABLE:
        print("[ERROR] Dependencies not available. Cannot run test.")
        print("  Required: compress_context.py, context7_integration.py, exa_integration.py")
        sys.exit(1)

    main()
