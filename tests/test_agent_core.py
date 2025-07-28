import pytest
from agent_core import UltronAgent

def test_ultron_agent_creation():
    agent = UltronAgent()
    assert agent is not None
