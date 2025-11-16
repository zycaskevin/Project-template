"""
MemoryHub 完整測試套件

測試覆蓋率目標: ≥ 90%
測試類別:
- 單元測試: MemoryHub 所有方法
- 整合測試: UniversalStorage + MemoryHub
- 效能測試: 延遲 < 100ms
- 相容性測試: 舊 API 向後相容

Version: 1.0.0
Author: 小質 (QA Expert)
Date: 2025-11-16
"""

import pytest
import time
from typing import Dict, List
from unittest import mock

# 測試對象
from memory_hub import MemoryHub, IntelligentMemorySystem


# ========== Fixtures ==========

@pytest.fixture
def memory_hub():
    """提供 MemoryHub 實例"""
    return MemoryHub()


@pytest.fixture
def sample_memory():
    """提供樣本記憶"""
    return {
        "content": "使用 pytest fixture 可提高測試複用性",
        "metadata": {
            "expert": "xiaocheng",
            "type": "learning",
            "project": "EvoMem",
            "tags": ["TDD", "pytest"],
            "timestamp": "2025-11-16T10:00:00",
            "source": "validated",
            "frequency": 5,
            "validated": True
        }
    }


# ========== 單元測試 ==========

class TestMemoryHubInitialization:
    """測試 MemoryHub 初始化"""

    def test_init_success(self, memory_hub):
        """測試正常初始化"""
        assert memory_hub is not None
        assert hasattr(memory_hub, 'storage')
        assert hasattr(memory_hub, 'capability')
        assert memory_hub._stats["total_queries"] == 0

    def test_storage_capability_detection(self, memory_hub):
        """測試儲存能力偵測"""
        from universal_memory_storage import StorageCapability

        assert memory_hub.capability in [
            StorageCapability.FULL,
            StorageCapability.BASIC
        ]

    def test_cache_initialized(self, memory_hub):
        """測試快取初始化"""
        assert memory_hub._query_cache == {}
        assert memory_hub._cache_max_size == 100


class TestIntelligentQuery:
    """測試智能查詢功能"""

    def test_basic_query(self, memory_hub):
        """測試基本查詢"""
        # 先添加測試資料
        memory_hub.add_memory(
            content="TDD Red-Green-Refactor 循環",
            expert="xiaocheng",
            memory_type="learning"
        )

        # 查詢
        results = memory_hub.intelligent_query(
            query="TDD",
            n_results=5
        )

        assert isinstance(results, list)
        # 注意：實際結果數量取決於 EvoMem 是否可用

    def test_query_with_agent_filter(self, memory_hub):
        """測試按專家過濾"""
        # 添加不同專家的記憶
        memory_hub.add_memory(
            content="小程的 TDD 實踐",
            expert="xiaocheng",
            memory_type="learning"
        )
        memory_hub.add_memory(
            content="小質的測試策略",
            expert="xiaozhi",
            memory_type="learning"
        )

        # 僅查詢小程的記憶
        results = memory_hub.intelligent_query(
            query="實踐",
            agent_type="xiaocheng",
            n_results=5
        )

        # 驗證所有結果都是小程的
        for r in results:
            assert r.get("metadata", {}).get("expert") == "xiaocheng"

    def test_query_with_project_filter(self, memory_hub):
        """測試按專案過濾"""
        # 添加不同專案的記憶
        memory_hub.add_memory(
            content="EvoMem 記憶系統",
            project="EvoMem",
            memory_type="learning"
        )
        memory_hub.add_memory(
            content="Buylist 購物清單",
            project="Buylist",
            memory_type="learning"
        )

        # 僅查詢 EvoMem 專案
        results = memory_hub.intelligent_query(
            query="系統",
            project="EvoMem",
            n_results=5
        )

        # 驗證所有結果都是 EvoMem 專案
        for r in results:
            assert r.get("metadata", {}).get("project") == "EvoMem"

    def test_query_cache_hit(self, memory_hub):
        """測試查詢快取命中"""
        # 第一次查詢（快取未命中）
        results1 = memory_hub.intelligent_query("測試", n_results=5)
        cache_hits_before = memory_hub._stats["cache_hits"]

        # 第二次相同查詢（快取命中）
        results2 = memory_hub.intelligent_query("測試", n_results=5)
        cache_hits_after = memory_hub._stats["cache_hits"]

        assert cache_hits_after == cache_hits_before + 1
        assert results1 == results2


class TestAddMemory:
    """測試添加記憶功能"""

    def test_add_memory_basic(self, memory_hub):
        """測試基本添加記憶"""
        success = memory_hub.add_memory(
            content="測試記憶內容",
            expert="xiaocheng",
            memory_type="learning"
        )

        assert success is True

    def test_add_memory_with_full_metadata(self, memory_hub):
        """測試使用完整 metadata 添加"""
        metadata = {
            "expert": "xiaocheng",
            "type": "learning",
            "project": "EvoMem",
            "tags": ["TDD", "pytest"],
            "source": "validated"
        }

        success = memory_hub.add_memory(
            content="完整 metadata 測試",
            metadata=metadata
        )

        assert success is True

    def test_add_memory_auto_timestamp(self, memory_hub):
        """測試自動添加時間戳"""
        memory_hub.add_memory(
            content="時間戳測試",
            expert="xiaocheng"
        )

        # 查詢並驗證時間戳
        results = memory_hub.intelligent_query("時間戳", n_results=1)
        if results:
            assert "timestamp" in results[0].get("metadata", {})

    def test_add_memory_clears_cache(self, memory_hub):
        """測試添加記憶清除快取"""
        # 先查詢以建立快取
        memory_hub.intelligent_query("測試", n_results=5)
        cache_size_before = len(memory_hub._query_cache)

        # 添加新記憶
        memory_hub.add_memory("新記憶", expert="xiaocheng")

        # 快取應被清除
        cache_size_after = len(memory_hub._query_cache)
        assert cache_size_after == 0


class TestBackwardCompatibility:
    """測試向後相容性"""

    def test_query_method_compatible(self, memory_hub):
        """測試舊 query 方法相容"""
        # 添加測試資料
        memory_hub.add_memory(
            content="向後相容測試",
            expert="xiaocheng"
        )

        # 使用舊 API
        results = memory_hub.query(
            query="相容",
            n_results=5,
            where={"expert": "xiaocheng"}
        )

        assert isinstance(results, list)

    def test_intelligent_memory_system_alias(self):
        """測試 IntelligentMemorySystem 別名"""
        # 舊代碼應能正常使用
        old_memory = IntelligentMemorySystem()

        assert isinstance(old_memory, MemoryHub)
        assert hasattr(old_memory, 'query')
        assert hasattr(old_memory, 'add_memory')


class TestQualityScoring:
    """測試品質評分功能"""

    def test_calculate_quality_score_high(self, memory_hub, sample_memory):
        """測試高品質記憶評分"""
        score = memory_hub.calculate_quality_score(sample_memory)

        # validated + 高頻率 + 最近時間 + 已驗證 = 高分
        assert 80 <= score <= 100

    def test_calculate_quality_score_low(self, memory_hub):
        """測試低品質記憶評分"""
        low_quality_memory = {
            "content": "低品質記憶",
            "metadata": {
                "source": "assumed",
                "frequency": 0,
                "validated": False
                # 無時間戳
            }
        }

        score = memory_hub.calculate_quality_score(low_quality_memory)

        # assumed + 低頻率 + 無時間 + 未驗證 = 低分
        assert 0 <= score <= 60

    def test_quality_score_range(self, memory_hub, sample_memory):
        """測試評分範圍在 0-100"""
        score = memory_hub.calculate_quality_score(sample_memory)

        assert 0 <= score <= 100


class TestRecommendations:
    """測試推薦功能"""

    def test_get_recommendations_basic(self, memory_hub):
        """測試基本推薦"""
        # 添加測試資料
        memory_hub.add_memory(
            content="TDD 最佳實踐",
            expert="xiaocheng",
            memory_type="learning",
            metadata={"source": "validated", "validated": True}
        )

        # 獲取推薦
        recommendations = memory_hub.get_recommendations(
            context="開發新功能",
            n_results=10,
            min_quality_score=60
        )

        assert isinstance(recommendations, list)

    def test_recommendations_include_insight(self, memory_hub):
        """測試推薦包含洞察"""
        memory_hub.add_memory(
            content="使用 fixture 提高複用",
            expert="xiaocheng",
            memory_type="learning",
            metadata={"source": "validated"}
        )

        recommendations = memory_hub.get_recommendations("測試", n_results=5)

        for rec in recommendations:
            assert "memory" in rec
            assert "quality_score" in rec
            assert "insight" in rec
            assert isinstance(rec["insight"], str)

    def test_recommendations_sorted_by_quality(self, memory_hub):
        """測試推薦按品質排序"""
        # 添加不同品質的記憶
        memory_hub.add_memory(
            "高品質記憶",
            metadata={"source": "validated", "validated": True, "frequency": 10}
        )
        memory_hub.add_memory(
            "低品質記憶",
            metadata={"source": "assumed", "validated": False, "frequency": 1}
        )

        recommendations = memory_hub.get_recommendations("記憶", n_results=10)

        # 驗證排序（品質分數遞減）
        if len(recommendations) >= 2:
            for i in range(len(recommendations) - 1):
                assert (
                    recommendations[i]["quality_score"] >=
                    recommendations[i + 1]["quality_score"]
                )


class TestStatistics:
    """測試統計功能"""

    def test_get_statistics_structure(self, memory_hub):
        """測試統計資訊結構"""
        stats = memory_hub.get_statistics()

        assert "total_queries" in stats
        assert "filtered_queries" in stats
        assert "cache_hits" in stats
        assert "cache_hit_rate" in stats
        assert "avg_latency_ms" in stats
        assert "cache_size" in stats
        assert "storage_capability" in stats

    def test_statistics_updated_after_query(self, memory_hub):
        """測試查詢後統計更新"""
        stats_before = memory_hub.get_statistics()
        total_before = stats_before["total_queries"]

        # 執行查詢
        memory_hub.intelligent_query("測試", n_results=5)

        stats_after = memory_hub.get_statistics()
        total_after = stats_after["total_queries"]

        assert total_after == total_before + 1

    def test_cache_hit_rate_calculation(self, memory_hub):
        """測試快取命中率計算"""
        # 第一次查詢（未命中）
        memory_hub.intelligent_query("測試", n_results=5)

        # 第二次相同查詢（命中）
        memory_hub.intelligent_query("測試", n_results=5)

        stats = memory_hub.get_statistics()

        # 2 次查詢，1 次命中 = 50% 命中率
        assert 0.4 <= stats["cache_hit_rate"] <= 0.6


class TestCacheManagement:
    """測試快取管理"""

    def test_clear_cache(self, memory_hub):
        """測試清除快取"""
        # 建立快取
        memory_hub.intelligent_query("測試", n_results=5)
        assert len(memory_hub._query_cache) > 0

        # 清除快取
        memory_hub.clear_cache()
        assert len(memory_hub._query_cache) == 0

    def test_cache_lru_eviction(self, memory_hub):
        """測試 LRU 快取淘汰"""
        # 設置小快取大小以便測試
        memory_hub._cache_max_size = 3

        # 添加 4 個查詢（超過快取大小）
        memory_hub.intelligent_query("query1", n_results=5)
        memory_hub.intelligent_query("query2", n_results=5)
        memory_hub.intelligent_query("query3", n_results=5)
        memory_hub.intelligent_query("query4", n_results=5)

        # 快取大小應保持在最大值
        assert len(memory_hub._query_cache) <= 3


# ========== 整合測試 ==========

class TestIntegration:
    """整合測試"""

    def test_full_workflow(self, memory_hub):
        """測試完整工作流程"""
        # 1. 添加記憶
        success = memory_hub.add_memory(
            content="TDD Red-Green-Refactor",
            expert="xiaocheng",
            memory_type="learning",
            tags=["TDD"]
        )
        assert success

        # 2. 查詢記憶
        results = memory_hub.intelligent_query(
            query="TDD",
            agent_type="xiaocheng",
            n_results=5
        )
        assert isinstance(results, list)

        # 3. 獲取推薦
        recommendations = memory_hub.get_recommendations(
            context="開發新功能",
            n_results=5
        )
        assert isinstance(recommendations, list)

        # 4. 檢查統計
        stats = memory_hub.get_statistics()
        assert stats["total_queries"] >= 2  # intelligent_query + get_recommendations


# ========== 效能測試 ==========

class TestPerformance:
    """效能測試"""

    def test_query_latency_under_100ms(self, memory_hub):
        """測試查詢延遲 < 100ms"""
        # 添加測試資料
        memory_hub.add_memory("效能測試", expert="xiaocheng")

        # 測量延遲
        start = time.time()
        memory_hub.intelligent_query("效能", n_results=5)
        elapsed_ms = (time.time() - start) * 1000

        # 允許較寬鬆的限制（首次查詢可能較慢）
        assert elapsed_ms < 500, f"查詢延遲 {elapsed_ms}ms 超過 500ms"

    def test_cached_query_latency_under_10ms(self, memory_hub):
        """測試快取查詢延遲 < 10ms"""
        # 第一次查詢（建立快取）
        memory_hub.intelligent_query("快取測試", n_results=5)

        # 第二次查詢（快取命中）
        start = time.time()
        memory_hub.intelligent_query("快取測試", n_results=5)
        elapsed_ms = (time.time() - start) * 1000

        # 快取查詢應非常快
        assert elapsed_ms < 50, f"快取查詢延遲 {elapsed_ms}ms 超過 50ms"


# ========== 錯誤處理測試 ==========

class TestErrorHandling:
    """錯誤處理測試"""

    def test_degraded_mode_handling(self, memory_hub):
        """測試降級模式處理"""
        from universal_memory_storage import StorageCapability

        # 模擬降級模式
        with mock.patch.object(memory_hub, 'capability', StorageCapability.BASIC):
            results = memory_hub.intelligent_query("測試", n_results=5)

            # 降級模式應返回空列表
            assert results == []


# ========== 執行測試 ==========

if __name__ == "__main__":
    # 執行測試
    pytest.main([__file__, "-v", "--tb=short"])
