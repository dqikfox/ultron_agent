"""
Integration test: verify Supabase is wired into the ULTRON agent.
Run with: pytest tests/test_supabase_integration.py
      or: python tests/test_supabase_integration.py
"""

import asyncio
import sys
import os

# Ensure project root is in path and is the cwd for config lookup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "ultron_config.json")


# ---------------------------------------------------------------------------
# Async helpers (called via asyncio.run inside sync pytest functions)
# ---------------------------------------------------------------------------

async def _client_factory():
    from ultron.supabase_client import create_client_from_config
    client = create_client_from_config(CONFIG_PATH)
    assert client is not None, "create_client_from_config returned None"
    ok = await client.connect()
    assert ok, "Could not connect to local Supabase"
    await client.close()


async def _conversation_lifecycle():
    from ultron.supabase_client import create_client_from_config
    client = create_client_from_config(CONFIG_PATH)
    await client.connect()

    cid = await client.start_conversation("Integration Test Session")
    assert cid, "No conversation id returned"

    mid = await client.persist_message("user", "Integration test message")
    assert mid, "Message not persisted"

    mid2 = await client.persist_message("assistant", "Integration test reply",
                                         processing_time_ms=100)
    assert mid2

    convs = await client.get_conversation_history(limit=5)
    assert any(c["id"] == cid for c in convs), "Conversation not in history"

    msgs = await client.get_recent_messages(conversation_id=cid)
    assert len(msgs) == 2, f"Expected 2 messages, got {len(msgs)}"

    await client.close()


async def _memory_sync():
    from ultron.supabase_client import create_client_from_config
    client = create_client_from_config(CONFIG_PATH)
    await client.connect()

    await client.save_memory_entry("test_key_integration", "hello_world")
    entries = await client.load_memory_entries()
    assert "test_key_integration" in entries, "Memory entry not loaded back"
    assert entries["test_key_integration"] == "hello_world"

    await client.close()


async def _tool_execution_logging():
    from ultron.supabase_client import create_client_from_config
    client = create_client_from_config(CONFIG_PATH)
    await client.connect()
    await client.start_conversation("Tool Log Test")

    await client.log_tool_execution(
        "test_tool", "test input", "test output",
        status="success", duration_ms=42
    )

    rows = await client.select("tool_executions",
                                "select=tool_name,status&order=created_at.desc&limit=1")
    assert rows and rows[0]["tool_name"] == "test_tool"

    await client.close()


# ---------------------------------------------------------------------------
# Sync pytest test functions
# ---------------------------------------------------------------------------

def test_client_factory():
    asyncio.run(_client_factory())


def test_conversation_lifecycle():
    asyncio.run(_conversation_lifecycle())


def test_memory_sync():
    asyncio.run(_memory_sync())


def test_tool_execution_logging():
    asyncio.run(_tool_execution_logging())


def test_tool_interface_supabase_property():
    from tools.tool_interface import ToolInterface
    from ultron.supabase_client import create_client_from_config

    client = create_client_from_config(CONFIG_PATH)
    ToolInterface.shared_supabase = client

    class DummyTool(ToolInterface):
        name = "dummy"
        description = "test"
        def match(self, cmd): return False
        async def execute(self, cmd): return {}
        def schema(self): return {}

    tool = DummyTool()
    assert tool.supabase is client, "Tool.supabase property not returning shared client"
    ToolInterface.shared_supabase = None  # cleanup


def test_memory_class_supabase_methods():
    """Verify Memory has sync_to_supabase and load_from_supabase methods."""
    from memory import Memory
    mem = Memory()
    assert callable(getattr(mem, "sync_to_supabase", None)), \
        "Memory missing sync_to_supabase"
    assert callable(getattr(mem, "load_from_supabase", None)), \
        "Memory missing load_from_supabase"


def test_agent_core_has_supabase_init():
    """Verify agent_core declares _initialize_supabase and self.supabase."""
    import inspect
    import agent_core
    src = inspect.getsource(agent_core.UltronAgent)
    assert "_initialize_supabase" in src
    assert "self.supabase" in src


if __name__ == "__main__":
    async def main():
        print("Running Supabase integration tests...\n")
        await _client_factory();          print("✅ client factory OK")
        await _conversation_lifecycle();  print("✅ conversation lifecycle OK")
        await _memory_sync();             print("✅ memory sync OK")
        await _tool_execution_logging();  print("✅ tool execution logging OK")
        test_tool_interface_supabase_property(); print("✅ tool interface OK")
        test_memory_class_supabase_methods();    print("✅ memory methods OK")
        test_agent_core_has_supabase_init();     print("✅ agent_core wiring OK")
        print("\n✅ All Supabase integration tests passed!")

    asyncio.run(main())
