"""
Tests for elite enhancements:
  1. IntelligentCache — bug fix + TTL + batch ops
  2. EventSystem — wildcards, dead-letter queue, subscribe_once, middleware, replay
  3. CircuitBreaker — trip / recover / decorator / fallback
  4. Memory — TTL short-term + fuzzy search
  5. ToolInterface — execute_safe / circuit stats (via hello_tool)
"""

import asyncio
import time
import pytest


# ---------------------------------------------------------------------------
# 1. IntelligentCache
# ---------------------------------------------------------------------------

class TestIntelligentCache:
    def _make(self, size=5, ttl=None):
        from utils.intelligent_cache import IntelligentCache
        return IntelligentCache(cache_size=size, ttl_seconds=ttl)

    def test_basic_hit_miss(self):
        c = self._make()
        c.set("a", 1)
        val, hit = c.get("a")
        assert hit is True
        assert val == 1

    def test_miss_returns_none(self):
        c = self._make()
        val, hit = c.get("missing")
        assert hit is False
        assert val is None

    def test_get_stats_no_crash(self):
        c = self._make()
        c.set("x", 10)
        c.get("x")
        c.get("y")  # miss
        stats = c.get_stats()
        assert stats["hit_count"] == 1
        assert stats["miss_count"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["miss_rate"] == 0.5

    def test_eviction_by_importance(self):
        c = self._make(size=2)
        c.set("a", 1)
        c.set("b", 2)
        c.get("b")  # b importance decays but stays high
        c.set("c", 3)  # should evict lowest-importance key (a)
        _, hit_a = c.get("a")
        _, hit_c = c.get("c")
        assert hit_c is True

    def test_ttl_expiry(self):
        c = self._make(ttl=0.05)
        c.set("k", "v")
        time.sleep(0.1)
        val, hit = c.get("k")
        assert hit is False

    def test_batch_get_set(self):
        c = self._make()
        c.batch_set({"x": 1, "y": 2, "z": 3})
        result = c.batch_get(["x", "y", "missing"])
        assert result == {"x": 1, "y": 2}

    def test_delete(self):
        c = self._make()
        c.set("d", 99)
        assert c.delete("d") is True
        _, hit = c.get("d")
        assert hit is False
        assert c.delete("d") is False  # already gone

    def test_invalidate(self):
        c = self._make()
        c.set("keep", "yes")
        # Decay importance of "keep" far below 0.5
        c.importances["keep"] = 0.1
        c.invalidate()
        _, hit = c.get("keep")
        assert hit is False


# ---------------------------------------------------------------------------
# 2. EventSystem
# ---------------------------------------------------------------------------

class TestEventSystem:
    def _make(self):
        from utils.event_system import EventSystem
        return EventSystem()

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_exact_subscription(self):
        es = self._make()
        received = []

        async def cb(data):
            received.append(data["v"])

        async def _go():
            await es.subscribe("my_event", cb)
            await es.emit("my_event", {"v": 42})

        self._run(_go())
        assert received == [42]

    def test_wildcard_subscription(self):
        es = self._make()
        received = []

        async def wc(data):
            received.append(data.get("v"))

        async def _go():
            await es.subscribe("tool.*", wc)
            await es.emit("tool.run", {"v": 1})
            await es.emit("tool.loaded", {"v": 2})
            await es.emit("other.event", {"v": 3})  # should NOT match

        self._run(_go())
        assert 1 in received
        assert 2 in received
        assert 3 not in received

    def test_subscribe_once(self):
        es = self._make()
        count = []

        async def once_cb(data):
            count.append(1)

        async def _go():
            await es.subscribe_once("ping", once_cb)
            await es.emit("ping", {})
            await es.emit("ping", {})

        self._run(_go())
        assert len(count) == 1, f"expected 1, got {len(count)}"

    def test_middleware_transforms(self):
        es = self._make()
        received = []

        async def tag_mw(event):
            event.data["tagged"] = True
            return event

        async def cb(data):
            received.append(data.get("tagged"))

        async def _go():
            es.add_middleware(tag_mw)
            await es.subscribe("ev", cb)
            await es.emit("ev", {"x": 1})

        self._run(_go())
        assert True in received

    def test_middleware_drop(self):
        es = self._make()
        received = []

        async def drop_mw(event):
            return None  # drop everything

        async def cb(data):
            received.append(1)

        async def _go():
            es.add_middleware(drop_mw)
            await es.subscribe("ev", cb)
            await es.emit("ev", {"x": 1})

        self._run(_go())
        assert received == []

    def test_dead_letter_queue(self):
        es = self._make()

        def bad_cb(data):
            raise RuntimeError("intentional failure")

        async def _go():
            await es.subscribe("bad", bad_cb)
            await es.emit("bad", {"msg": "boom"})

        self._run(_go())
        dl = es.get_dead_letters()
        assert len(dl) == 1
        assert "intentional failure" in dl[0].error

    def test_replay_history(self):
        es = self._make()
        replayed = []

        async def _go():
            await es.subscribe("tool.x", lambda d: None)
            await es.emit("tool.x", {"v": 1})
            await es.emit("tool.x", {"v": 2})
            await es.emit("other", {"v": 99})
            count = await es.replay_history(
                lambda d: replayed.append(d.get("v")),
                event_name="tool.*",
            )
            return count

        count = self._run(_go())
        assert count == 2
        assert replayed == [1, 2]

    def test_get_stats_includes_wildcard(self):
        es = self._make()

        async def _go():
            await es.subscribe("tool.*", lambda d: None)
            stats = es.get_stats()
            return stats

        stats = self._run(_go())
        assert "tool.*" in stats["wildcard_patterns"]
        assert stats["wildcard_subscriptions"] == 1


# ---------------------------------------------------------------------------
# 3. CircuitBreaker
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    def _make(self, **kw):
        from utils.circuit_breaker import CircuitBreaker
        return CircuitBreaker(name="test_cb", failure_threshold=2,
                              recovery_timeout=0.05, **kw)

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_trips_after_threshold(self):
        from utils.circuit_breaker import CircuitOpenError
        cb = self._make()

        async def bad():
            raise ValueError("fail")

        async def _go():
            for _ in range(2):
                try:
                    await cb.call(bad)
                except ValueError:
                    pass
            return cb.state.value

        state = self._run(_go())
        assert state == "open"

    def test_rejects_when_open(self):
        from utils.circuit_breaker import CircuitOpenError
        cb = self._make()

        async def bad():
            raise ValueError("fail")

        async def good():
            return "ok"

        async def _go():
            for _ in range(2):
                try:
                    await cb.call(bad)
                except ValueError:
                    pass
            await cb.call(good)

        with pytest.raises(CircuitOpenError):
            self._run(_go())

    def test_recovers_after_timeout(self):
        from utils.circuit_breaker import CircuitOpenError
        cb = self._make()

        async def bad():
            raise ValueError("fail")

        async def good():
            return "ok"

        async def _go():
            for _ in range(2):
                try:
                    await cb.call(bad)
                except ValueError:
                    pass
            await asyncio.sleep(0.1)  # past recovery_timeout=0.05
            return await cb.call(good)

        result = self._run(_go())
        assert result == "ok"
        assert cb.state.value == "closed"

    def test_sync_call(self):
        from utils.circuit_breaker import CircuitBreaker
        cb = CircuitBreaker("sync_test", failure_threshold=2, recovery_timeout=60)

        def good():
            return "sync_ok"

        assert cb.call_sync(good) == "sync_ok"

    def test_decorator_with_fallback(self):
        from utils.circuit_breaker import circuit_breaker, get_circuit_breaker

        cb = get_circuit_breaker("dec_fb_test", failure_threshold=2,
                                  recovery_timeout=60)

        @circuit_breaker("dec_fb_test", failure_threshold=2,
                          recovery_timeout=60, fallback=lambda: "fb")
        def risky():
            raise RuntimeError("fail")

        try:
            risky()
        except RuntimeError:
            pass
        try:
            risky()
        except RuntimeError:
            pass
        result = risky()
        assert result == "fb"


# ---------------------------------------------------------------------------
# 4. Memory TTL + fuzzy search
# ---------------------------------------------------------------------------

class TestMemory:
    def _make(self):
        from memory import Memory
        return Memory(short_term_limit=20, long_term_file="/tmp/test_mem_elite.json")

    def test_add_and_retrieve(self):
        m = self._make()
        m.add_to_short_term("hello")
        items = m.retrieve_short_term()
        assert "hello" in items

    def test_ttl_expiry(self):
        m = self._make()
        m.add_to_short_term("expires_soon", ttl_seconds=0.05)
        time.sleep(0.1)
        items = m.retrieve_short_term()
        assert "expires_soon" not in items

    def test_ttl_permanent_coexist(self):
        m = self._make()
        m.add_to_short_term("permanent")
        m.add_to_short_term("temporary", ttl_seconds=0.05)
        time.sleep(0.1)
        items = m.retrieve_short_term()
        assert "permanent" in items
        assert "temporary" not in items

    def test_search_exact(self):
        m = self._make()
        m.add_to_short_term("the quick brown fox")
        results = m.search_memory("fox")
        assert any("fox" in str(r) for r in results)

    def test_search_fuzzy(self):
        m = self._make()
        m.add_to_short_term("the quick brown fox jumps")
        results = m.search_memory("quick fox", fuzzy=True)
        assert len(results) > 0

    def test_fuzzy_no_partial_match(self):
        m = self._make()
        m.add_to_short_term("only quick here")
        # Both tokens must match; "fox" is absent
        results = m.search_memory("quick fox", fuzzy=True)
        assert len(results) == 0

    def test_get_recent_respects_ttl(self):
        m = self._make()
        m.add_to_short_term("old_item", ttl_seconds=0.05)
        m.add_to_short_term("new_item")
        time.sleep(0.1)
        recent = m.get_recent_memory(limit=5)
        assert "new_item" in recent
        assert "old_item" not in recent
