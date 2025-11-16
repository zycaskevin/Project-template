"""
MemoryHub - 小憶記憶中樞 Universal Storage 包裝器

這個模組提供向後相容的記憶中樞介面，保留小憶 v3.0-hub 的智能路由功能，
同時使用 Universal Memory Storage v2.0.0 作為底層儲存。

Version: 1.0.0
Author: Multi-Expert Team (小米 + 小架 + 小憶)
Date: 2025-11-16
"""

from typing import List, Dict, Optional, Any
from enum import Enum
import time
import json
from datetime import datetime

try:
    from universal_memory_storage import (
        create_storage,
        StorageCapability,
        MemoryStorageInterface
    )
except ImportError:
    # 降級處理：若 universal_memory_storage 不可用
    print("⚠️ 警告: universal_memory_storage 模組不可用，MemoryHub 功能受限")
    create_storage = None
    StorageCapability = None
    MemoryStorageInterface = None


class MemoryHub:
    """
    小憶記憶中樞 - Universal Storage 包裝器

    保留小憶 v3.0-hub 的所有核心功能：
    - 智能查詢路由（按專家類型）
    - 主動推薦（帶洞察生成）
    - 跨專案記憶搜尋
    - 記憶品質評分（0-100）

    同時使用 Universal Storage v2.0.0 提供：
    - 自動降級機制（EvoMem → JSON）
    - 統一儲存介面
    - 可插拔後端
    """

    def __init__(self, persist_directory: Optional[str] = None):
        """
        初始化 MemoryHub

        Args:
            persist_directory: 持久化目錄（向後相容參數，實際由 UniversalStorage 管理）
        """
        if create_storage is None:
            raise ImportError(
                "universal_memory_storage 模組不可用。"
                "請確保已安裝 Universal Memory Storage v2.0.0"
            )

        # 初始化 Universal Storage
        self.storage = create_storage()
        self.capability = self.storage.capability

        # 統計資訊
        self._stats = {
            "total_queries": 0,
            "filtered_queries": 0,
            "cache_hits": 0,
            "avg_latency_ms": 0.0
        }

        # 簡易快取（記憶最近 100 次查詢）
        self._query_cache: Dict[str, List[Dict]] = {}
        self._cache_max_size = 100

        print(f"✅ MemoryHub 初始化完成")
        print(f"   儲存能力: {self.capability.value}")
        print(f"   後端類型: {type(self.storage).__name__}")

    def intelligent_query(
        self,
        query: str,
        agent_type: Optional[str] = None,
        n_results: int = 5,
        project: Optional[str] = None
    ) -> List[Dict]:
        """
        智能查詢路由（保留 v3.0-hub 功能）

        這是 MemoryHub 的核心方法，提供：
        1. 按專家類型過濾
        2. 跨專案搜尋
        3. 自動快取
        4. 效能統計

        Args:
            query: 查詢字串
            agent_type: 專家類型（如 "xiaocheng", "xiaozhi"）
            n_results: 返回結果數量
            project: 專案名稱（如 "EvoMem", "Buylist"）

        Returns:
            記憶列表，每個記憶包含 content 和 metadata

        Example:
            >>> hub = MemoryHub()
            >>> results = hub.intelligent_query(
            ...     "TDD 最佳實踐",
            ...     agent_type="xiaocheng",
            ...     n_results=5
            ... )
            >>> print(f"找到 {len(results)} 條記憶")
        """
        start_time = time.time()
        self._stats["total_queries"] += 1

        # 檢查快取
        cache_key = f"{query}:{agent_type}:{project}:{n_results}"
        if cache_key in self._query_cache:
            self._stats["cache_hits"] += 1
            print(f"⚡ 快取命中: {cache_key[:50]}...")
            return self._query_cache[cache_key]

        # 檢查儲存能力
        if self.capability != StorageCapability.FULL:
            print("⚠️ EvoMem 不可用，語義搜尋降級")
            return []

        # 語義搜尋（查詢 2x 結果以便過濾）
        try:
            results = self.storage.search(query, n_results=n_results * 2)
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
            return []

        # 手動過濾 metadata（替代舊 where 參數）
        filtered_results = results

        if agent_type:
            self._stats["filtered_queries"] += 1
            filtered_results = [
                r for r in filtered_results
                if r.get("metadata", {}).get("expert") == agent_type
            ]

        if project:
            filtered_results = [
                r for r in filtered_results
                if r.get("metadata", {}).get("project") == project
            ]

        # 限制結果數量
        filtered_results = filtered_results[:n_results]

        # 更新快取
        self._update_cache(cache_key, filtered_results)

        # 記錄效能
        elapsed_ms = (time.time() - start_time) * 1000
        self._update_stats(elapsed_ms)

        print(f"✅ 查詢完成: {len(filtered_results)} 條結果 ({elapsed_ms:.1f}ms)")

        return filtered_results

    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        expert: Optional[str] = None,
        memory_type: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        添加記憶（向後相容 IntelligentMemorySystem.add_memory）

        Args:
            content: 記憶內容
            metadata: 完整 metadata 字典（優先使用）
            expert: 專家名稱（如 "xiaocheng"）
            memory_type: 記憶類型（如 "learning", "bug", "decision"）
            project: 專案名稱（如 "EvoMem"）
            tags: 標籤列表（如 ["TDD", "pytest"]）

        Returns:
            是否成功添加

        Example:
            >>> hub.add_memory(
            ...     content="使用 pytest fixture 可提高測試複用性",
            ...     expert="xiaocheng",
            ...     memory_type="learning",
            ...     tags=["TDD", "pytest"]
            ... )
        """
        # 構建 metadata
        if metadata is None:
            metadata = {}

        # 添加額外欄位
        if expert:
            metadata["expert"] = expert
        if memory_type:
            metadata["type"] = memory_type
        if project:
            metadata["project"] = project
        if tags:
            metadata["tags"] = tags

        # 自動添加時間戳
        metadata["timestamp"] = datetime.now().isoformat()

        # 添加到 Universal Storage
        try:
            self.storage.add({
                "content": content,
                "metadata": metadata
            })
            print(f"✅ 記憶已添加: {content[:50]}...")

            # 清除快取（新記憶可能影響查詢結果）
            self._query_cache.clear()

            return True
        except Exception as e:
            print(f"❌ 添加記憶失敗: {e}")
            return False

    def query(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        向後相容的 query 方法（IntelligentMemorySystem.query）

        這個方法保留舊 API 介面，內部轉發到 intelligent_query

        Args:
            query: 查詢字串
            n_results: 返回結果數量
            where: 過濾條件（如 {"expert": "xiaocheng"}）

        Returns:
            記憶列表

        Example:
            >>> # 舊代碼可直接使用
            >>> results = memory.query(
            ...     "TDD 最佳實踐",
            ...     n_results=5,
            ...     where={"expert": "xiaocheng"}
            ... )
        """
        agent_type = None
        project = None

        if where:
            agent_type = where.get("expert")
            project = where.get("project")

        return self.intelligent_query(
            query=query,
            agent_type=agent_type,
            project=project,
            n_results=n_results
        )

    def calculate_quality_score(
        self,
        memory: Dict[str, Any],
        source_weight: float = 0.4,
        frequency_weight: float = 0.2,
        timeliness_weight: float = 0.2,
        validation_weight: float = 0.2
    ) -> int:
        """
        計算記憶品質評分（0-100）

        評分維度：
        - 來源可信度（40%）: validated > documented > inferred > assumed
        - 使用頻率（20%）: 被查詢/引用次數
        - 時效性（20%）: 最近記憶得分更高
        - 驗證狀態（20%）: 是否經過小查驗證

        Args:
            memory: 記憶字典（包含 metadata）
            source_weight: 來源權重
            frequency_weight: 頻率權重
            timeliness_weight: 時效性權重
            validation_weight: 驗證權重

        Returns:
            品質評分（0-100）
        """
        metadata = memory.get("metadata", {})
        score = 0.0

        # 1. 來源可信度評分
        source = metadata.get("source", "assumed")
        source_scores = {
            "validated": 100,
            "documented": 80,
            "inferred": 60,
            "assumed": 40
        }
        score += source_scores.get(source, 40) * source_weight

        # 2. 使用頻率評分
        frequency = metadata.get("frequency", 1)
        frequency_score = min(100, frequency * 10)  # 10次使用 = 滿分
        score += frequency_score * frequency_weight

        # 3. 時效性評分
        timestamp = metadata.get("timestamp")
        if timestamp:
            try:
                mem_time = datetime.fromisoformat(timestamp)
                days_old = (datetime.now() - mem_time).days
                timeliness_score = max(0, 100 - days_old)  # 每天減 1 分
            except:
                timeliness_score = 50  # 無法解析時間，給中等分數
        else:
            timeliness_score = 50
        score += timeliness_score * timeliness_weight

        # 4. 驗證狀態評分
        validated = metadata.get("validated", False)
        validation_score = 100 if validated else 0
        score += validation_score * validation_weight

        return int(score)

    def get_recommendations(
        self,
        context: str,
        n_results: int = 10,
        min_quality_score: int = 60
    ) -> List[Dict]:
        """
        主動推薦（帶洞察生成）

        基於當前上下文推薦相關記憶，並生成洞察

        Args:
            context: 當前上下文（如 "正在開發計算機模組"）
            n_results: 推薦數量
            min_quality_score: 最低品質分數

        Returns:
            推薦列表，每個包含 memory + quality_score + insight
        """
        # 查詢相關記憶
        results = self.intelligent_query(context, n_results=n_results)

        # 計算品質分數並過濾
        recommendations = []
        for memory in results:
            quality_score = self.calculate_quality_score(memory)

            if quality_score >= min_quality_score:
                recommendations.append({
                    "memory": memory,
                    "quality_score": quality_score,
                    "insight": self._generate_insight(memory)
                })

        # 按品質分數排序
        recommendations.sort(key=lambda x: x["quality_score"], reverse=True)

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取使用統計

        Returns:
            統計資訊字典
        """
        return {
            "total_queries": self._stats["total_queries"],
            "filtered_queries": self._stats["filtered_queries"],
            "cache_hits": self._stats["cache_hits"],
            "cache_hit_rate": (
                self._stats["cache_hits"] / self._stats["total_queries"]
                if self._stats["total_queries"] > 0 else 0.0
            ),
            "avg_latency_ms": self._stats["avg_latency_ms"],
            "cache_size": len(self._query_cache),
            "storage_capability": self.capability.value
        }

    def clear_cache(self):
        """清除查詢快取"""
        self._query_cache.clear()
        print("✅ 快取已清除")

    # ========== 私有方法 ==========

    def _update_cache(self, key: str, value: List[Dict]):
        """更新快取（LRU 策略）"""
        if len(self._query_cache) >= self._cache_max_size:
            # 移除最舊的項目
            oldest_key = next(iter(self._query_cache))
            del self._query_cache[oldest_key]

        self._query_cache[key] = value

    def _update_stats(self, latency_ms: float):
        """更新效能統計"""
        n = self._stats["total_queries"]
        current_avg = self._stats["avg_latency_ms"]

        # 移動平均
        self._stats["avg_latency_ms"] = (
            (current_avg * (n - 1) + latency_ms) / n
        )

    def _generate_insight(self, memory: Dict[str, Any]) -> str:
        """
        生成洞察（簡化版）

        實際應用中可使用 LLM 生成更智能的洞察
        """
        metadata = memory.get("metadata", {})
        memory_type = metadata.get("type", "unknown")
        expert = metadata.get("expert", "unknown")

        insights = {
            "bug": f"💡 歷史 Bug 提醒：注意邊界條件測試",
            "learning": f"💡 最佳實踐：建議採用此模式",
            "decision": f"💡 架構決策參考：{expert} 的經驗",
            "test_case": f"💡 測試案例：可複用到當前場景"
        }

        return insights.get(memory_type, f"💡 相關記憶來自 {expert}")


# ========== 向後相容別名 ==========

class IntelligentMemorySystem(MemoryHub):
    """
    向後相容別名

    舊代碼可繼續使用 IntelligentMemorySystem，內部實際使用 MemoryHub

    Example:
        >>> from integrations.memory_hub import IntelligentMemorySystem
        >>> memory = IntelligentMemorySystem()
        >>> # 完全相容舊 API
    """
    def __init__(self, persist_directory: Optional[str] = None):
        print("⚠️ IntelligentMemorySystem 已棄用，請改用 MemoryHub")
        print("   當前呼叫將轉發到 MemoryHub（向後相容）")
        super().__init__(persist_directory)


# ========== 模組導出 ==========

__all__ = [
    "MemoryHub",
    "IntelligentMemorySystem",  # 向後相容
]


if __name__ == "__main__":
    # 快速測試
    print("=" * 60)
    print("MemoryHub 快速測試")
    print("=" * 60)

    try:
        # 初始化
        hub = MemoryHub()

        # 測試添加記憶
        hub.add_memory(
            content="pytest fixture 可提高測試複用性",
            expert="xiaocheng",
            memory_type="learning",
            tags=["TDD", "pytest"]
        )

        # 測試查詢
        results = hub.intelligent_query(
            query="pytest 測試",
            agent_type="xiaocheng",
            n_results=5
        )

        print(f"\n查詢結果: {len(results)} 條")

        # 測試統計
        stats = hub.get_statistics()
        print(f"\n統計資訊:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))

        print("\n✅ MemoryHub 測試通過！")

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
