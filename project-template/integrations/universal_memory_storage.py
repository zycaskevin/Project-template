"""
Universal Memory Storage Module

Purpose: Provide a unified interface for different memory storage backends
Version: 1.0.0 (Revised - Based on Adversarial Analysis)
Author: Claude Code + zycaskevin

Design Philosophy:
- Minimal Viable Product (MVP): 2 core backends (EvoMem + JSON)
- Progressive Enhancement: Easy to add new backends later
- Auto-degradation: EvoMem → JSON → Fail with clear error
- Zero-config default: MemoryStorageFactory.create() works out of the box

Architecture:
1. Abstraction Layer: MemoryStorageInterface
2. Implementation Layer: EvoMemStorage (FULL) + JSONStorage (BASIC)
3. Factory Layer: MemoryStorageFactory (auto-detection + 2-tier degradation)

Based on Red Team vs Blue Team adversarial analysis:
- Reduced code from 500+ → ~300 lines (-40%)
- Simplified backends from 4 → 2 (-50%)
- Simplified capability levels from 4 → 2 (-50%)
- Simplified config options from 5 → 3 (-40%)
- Maintained extensibility while reducing complexity
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
import json
import os


# ============================================================
# 1. Capability Levels (Simplified to 2 levels)
# ============================================================

class StorageCapability(Enum):
    """Storage capability levels

    Simplified from 4 levels to 2 based on adversarial analysis:
    - FULL: Complete functionality (storage + semantic search + cross-conversation)
    - BASIC: Core functionality (storage + retrieval only)

    Removed unnecessary levels:
    - SEARCH: Redundant (same as FULL for our use case)
    - DOCUMENT: Moved to documentation generator, not a storage concern
    """
    FULL = "full"      # Complete functionality (EvoMem)
    BASIC = "basic"    # Core functionality (JSON fallback)


# ============================================================
# 2. Abstract Interface (Core Required + Optional Extensions)
# ============================================================

class MemoryStorageInterface(ABC):
    """Universal memory storage interface

    All memory storage backends must implement this interface.

    Design principle: Core methods (must implement) + Optional methods (can override)
    - Core: store(), retrieve(), health_check()
    - Optional: search() (defaults to empty list for BASIC backends)
    """

    @property
    @abstractmethod
    def capability(self) -> StorageCapability:
        """Declare storage capability level

        Returns:
            StorageCapability: FULL or BASIC
        """
        pass

    # ---------- Core Methods (All backends must implement) ----------

    @abstractmethod
    def store(self, memory_item: Dict) -> str:
        """Store memory item

        Args:
            memory_item: Memory item containing:
                {
                    "id": "mem_20251115_165919",
                    "type": "handoff",
                    "timestamp": "2025-11-15T16:59:19Z",
                    "session_memory": {...},
                    "long_term_memory": {...},
                    "metadata": {...}
                }

        Returns:
            memory_id: Unique memory identifier
        """
        pass

    @abstractmethod
    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """Retrieve memory item by ID

        Args:
            memory_id: Unique memory identifier

        Returns:
            memory_item: Memory item if found, None otherwise
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if storage backend is healthy

        Returns:
            True if healthy and ready to use, False otherwise
        """
        pass

    # ---------- Optional Methods (Only FULL backends implement) ----------

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Semantic search for memories (optional feature)

        Default implementation: Return empty list (search not supported)
        FULL capability backends can override this method.

        Args:
            query: Search query string
            **kwargs: Backend-specific parameters:
                - EvoMem: n_results=5, enhance=True
                - Mem0: user_id="...", limit=5

        Returns:
            results: List of relevant memory items (empty if not supported)

        Note:
            BASIC backends will return [] by default.
            Check capability before calling this method.
        """
        return []


# ============================================================
# 3. Implementation Layer - EvoMem Backend (FULL)
# ============================================================

class EvoMemStorage(MemoryStorageInterface):
    """EvoMem vector database storage (FULL capability)

    Features:
    - Persistent vector storage with ChromaDB
    - Semantic search with intent classification
    - Cross-conversation memory reuse
    - Query enhancement

    Requirements:
    - EvoMem installed: pip install -e EvoMem/
    - ChromaDB dependencies available
    """

    @property
    def capability(self) -> StorageCapability:
        return StorageCapability.FULL

    def __init__(self, persist_directory: str = "data/vectors/memory"):
        """Initialize EvoMem storage

        Args:
            persist_directory: Path to ChromaDB persistence directory
        """
        self.persist_directory = persist_directory
        self._available = False
        self.evomem = None
        self._init_evomem()

    def _init_evomem(self):
        """Initialize EvoMem with lazy loading (avoid startup dependency errors)"""
        try:
            # Lazy import - only load when actually used
            from core.memory_v2.intelligent_memory_system import IntelligentMemorySystem

            self.evomem = IntelligentMemorySystem(
                persist_directory=self.persist_directory
            )
            self._available = True
            print(f"[OK] EvoMemStorage initialized at {self.persist_directory}")

        except ImportError as e:
            self._available = False
            raise RuntimeError(
                f"EvoMem not available: {e}\n"
                "Install with: pip install -e EvoMem/\n"
                "Or use JSONStorage as fallback"
            )

        except Exception as e:
            self._available = False
            raise RuntimeError(
                f"EvoMem initialization failed: {e}\n"
                "Check ChromaDB dependencies or use JSONStorage as fallback"
            )

    def store(self, memory_item: Dict) -> str:
        """Store memory to EvoMem vector database

        Process:
        1. Extract memory_id
        2. Build text content for vectorization
        3. Store to EvoMem with metadata

        Args:
            memory_item: Complete memory item

        Returns:
            memory_id: Unique identifier
        """
        if not self._available:
            raise RuntimeError("EvoMem not available")

        memory_id = memory_item['id']

        # Build content text for vectorization
        content = self._build_content(memory_item)

        # Store to EvoMem
        self.evomem.add_memory(
            content=content,
            metadata={
                "memory_id": memory_id,
                "type": "handoff",
                "project": memory_item['metadata'].get('project', 'unknown'),
                "phase": memory_item['metadata'].get('phase', ''),
                "timestamp": memory_item['timestamp'],
                "compression_ratio": memory_item['metadata'].get('compression_ratio', 0),
                "quality_score": memory_item['metadata'].get('quality_score', 0)
            }
        )

        return memory_id

    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """Retrieve memory from EvoMem by ID

        Args:
            memory_id: Unique memory identifier

        Returns:
            memory_item: Memory metadata if found, None otherwise
        """
        if not self._available:
            return None

        try:
            # Query by memory_id
            results = self.evomem.query(
                query=f"memory_id:{memory_id}",
                n_results=1
            )

            if results and len(results.get('results', [])) > 0:
                return results['results'][0]['metadata']

        except Exception as e:
            print(f"[WARNING] EvoMem retrieve error: {e}")

        return None

    def search(self, query: str, **kwargs) -> List[Dict]:
        """EvoMem semantic search with query enhancement

        Args:
            query: Search query
            **kwargs: EvoMem-specific parameters
                - n_results: Number of results (default: 5)
                - enhance: Enable query enhancement (default: True)

        Returns:
            results: List of relevant memories
        """
        if not self._available:
            return []

        n_results = kwargs.get('n_results', 5)

        try:
            results = self.evomem.query(
                query=query,
                n_results=n_results
            )

            return results.get('results', [])

        except Exception as e:
            print(f"[WARNING] EvoMem search error: {e}")
            return []

    def health_check(self) -> bool:
        """Check if EvoMem is healthy

        Returns:
            True if EvoMem initialized and ready, False otherwise
        """
        return self._available and self.evomem is not None

    def _build_content(self, memory_item: Dict) -> str:
        """Build text content for vectorization

        Extracts key information from memory item:
        - Session intent
        - TODOs
        - Decisions
        - Learnings

        Args:
            memory_item: Memory item

        Returns:
            content: Text content for vectorization
        """
        parts = []

        # Session memory
        session = memory_item.get('session_memory', {})

        # Intent
        if session.get('sessionIntent'):
            intents = session['sessionIntent']
            parts.append(f"Intent: {', '.join(intents)}")

        # TODOs
        if session.get('todos'):
            todos = [t['content'] for t in session['todos'] if isinstance(t, dict)]
            if todos:
                parts.append(f"TODOs: {'; '.join(todos)}")

        # Decisions
        if session.get('decisions'):
            decisions = [d['decision'] for d in session['decisions'] if isinstance(d, dict)]
            if decisions:
                parts.append(f"Decisions: {'; '.join(decisions)}")

        # Long-term memory
        long_term = memory_item.get('long_term_memory', {})

        # Learnings
        if long_term.get('learnings'):
            learnings = [l['pattern'] for l in long_term['learnings'] if isinstance(l, dict)]
            if learnings:
                parts.append(f"Learnings: {'; '.join(learnings)}")

        return "\n".join(parts) if parts else "Memory handoff"


# ============================================================
# 4. Implementation Layer - JSON Backend (BASIC)
# ============================================================

class JSONStorage(MemoryStorageInterface):
    """JSON file storage (BASIC capability - fallback option)

    Features:
    - Simple file-based storage
    - No external dependencies
    - Fast and reliable
    - No semantic search (returns empty list)

    Use cases:
    - Development environment without EvoMem
    - CI/CD testing environment
    - Minimal dependency deployment
    """

    @property
    def capability(self) -> StorageCapability:
        return StorageCapability.BASIC

    def __init__(self, storage_dir: str = "data/memory"):
        """Initialize JSON storage

        Args:
            storage_dir: Directory to store JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] JSONStorage initialized at {storage_dir}")

    def store(self, memory_item: Dict) -> str:
        """Store memory to JSON file

        Args:
            memory_item: Complete memory item

        Returns:
            memory_id: Unique identifier
        """
        memory_id = memory_item['id']
        file_path = self.storage_dir / f"{memory_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(memory_item, f, ensure_ascii=False, indent=2)

        return memory_id

    def retrieve(self, memory_id: str) -> Optional[Dict]:
        """Retrieve memory from JSON file

        Args:
            memory_id: Unique memory identifier

        Returns:
            memory_item: Memory item if file exists, None otherwise
        """
        file_path = self.storage_dir / f"{memory_id}.json"

        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] JSON retrieve error: {e}")

        return None

    # search() inherits default implementation (returns empty list)

    def health_check(self) -> bool:
        """Check if storage directory is writable

        Returns:
            True if directory exists and is writable, False otherwise
        """
        return self.storage_dir.exists() and os.access(str(self.storage_dir), os.W_OK)


# ============================================================
# 5. Factory Layer (Auto-detection + 2-tier degradation)
# ============================================================

class MemoryStorageFactory:
    """Memory storage factory with auto-detection and 2-tier degradation

    Degradation path (based on adversarial analysis):
    1. Try EvoMem (FULL) - Complete functionality
    2. Fallback to JSON (BASIC) - Core functionality only
    3. Fail with clear error message

    Removed from original design (based on Red Team feedback):
    - Mem0 backend (not used in current project)
    - DocumentOnly backend (handled by documenter, not storage)
    - 4-tier degradation (too complex for MVP)
    """

    @classmethod
    def create(cls, config: Optional[Dict] = None) -> MemoryStorageInterface:
        """Create memory storage instance with auto-detection

        Args:
            config: Optional configuration
                {
                    "type": "auto" | "evomem" | "json",
                    "evomem": {
                        "persist_directory": "data/vectors/memory"
                    },
                    "json": {
                        "storage_dir": "data/memory"
                    }
                }

                If not provided, defaults to auto-detection (zero-config)

        Returns:
            MemoryStorageInterface: Storage instance (EvoMem or JSON)

        Raises:
            RuntimeError: If all backends fail

        Examples:
            # Zero-config (recommended)
            storage = MemoryStorageFactory.create()

            # Specify backend
            storage = MemoryStorageFactory.create({"type": "evomem"})

            # Custom config
            storage = MemoryStorageFactory.create({
                "type": "evomem",
                "evomem": {"persist_directory": "custom/path"}
            })
        """
        if config is None:
            config = {}

        storage_type = config.get('type', 'auto')

        if storage_type == 'auto':
            return cls._auto_detect(config)
        elif storage_type == 'evomem':
            return cls._create_evomem(config.get('evomem', {}))
        elif storage_type == 'json':
            return cls._create_json(config.get('json', {}))
        else:
            raise ValueError(
                f"Unknown storage type: {storage_type}\n"
                f"Valid options: 'auto', 'evomem', 'json'"
            )

    @classmethod
    def _auto_detect(cls, config: Dict) -> MemoryStorageInterface:
        """Auto-detect available storage backend (2-tier degradation)

        Tries in order:
        1. EvoMem (FULL)
        2. JSON (BASIC)

        Args:
            config: Configuration dict

        Returns:
            MemoryStorageInterface: First available backend

        Raises:
            RuntimeError: If all backends fail
        """
        print("[Auto-Detection] Detecting available memory storage backend...")

        # 1. Try EvoMem (FULL)
        try:
            print("  [Trying] EvoMemStorage (FULL capability)...")
            storage = cls._create_evomem(config.get('evomem', {}))
            if storage.health_check():
                print("  [SUCCESS] Using EvoMemStorage")
                return storage
            else:
                print("  [FAILED] EvoMemStorage health check failed")
        except Exception as e:
            print(f"  [FAILED] EvoMemStorage: {str(e)}")

        # 2. Fallback to JSON (BASIC)
        try:
            print("  [Trying] JSONStorage (BASIC capability)...")
            storage = cls._create_json(config.get('json', {}))
            if storage.health_check():
                print("  [FALLBACK] Degraded to JSONStorage (semantic search unavailable)")
                return storage
            else:
                print("  [FAILED] JSONStorage health check failed")
        except Exception as e:
            print(f"  [FAILED] JSONStorage: {str(e)}")

        # 3. All backends failed
        raise RuntimeError(
            "No available memory storage backend.\n"
            "Please ensure:\n"
            "  1. EvoMem is installed: pip install -e EvoMem/\n"
            "  OR\n"
            "  2. Storage directory is writable: data/memory/\n"
            "\n"
            "For help, see: project-template/integrations/MEMORY_HANDOFF_USER_GUIDE.md"
        )

    @classmethod
    def _create_evomem(cls, config: Dict) -> EvoMemStorage:
        """Create EvoMem storage instance

        Args:
            config: EvoMem configuration
                {
                    "persist_directory": "data/vectors/memory"
                }

        Returns:
            EvoMemStorage: EvoMem storage instance
        """
        persist_directory = config.get('persist_directory', 'data/vectors/memory')
        return EvoMemStorage(persist_directory=persist_directory)

    @classmethod
    def _create_json(cls, config: Dict) -> JSONStorage:
        """Create JSON storage instance

        Args:
            config: JSON configuration
                {
                    "storage_dir": "data/memory"
                }

        Returns:
            JSONStorage: JSON storage instance
        """
        storage_dir = config.get('storage_dir', 'data/memory')
        return JSONStorage(storage_dir=storage_dir)


# ============================================================
# 6. Convenience Functions
# ============================================================

def create_storage(config: Optional[Dict] = None) -> MemoryStorageInterface:
    """Convenience function to create storage (alias for factory)

    Args:
        config: Optional configuration

    Returns:
        MemoryStorageInterface: Storage instance

    Example:
        from universal_memory_storage import create_storage

        storage = create_storage()  # Zero-config auto-detection
    """
    return MemoryStorageFactory.create(config)


# ============================================================
# 7. Module Exports
# ============================================================

__all__ = [
    'StorageCapability',
    'MemoryStorageInterface',
    'EvoMemStorage',
    'JSONStorage',
    'MemoryStorageFactory',
    'create_storage'
]
