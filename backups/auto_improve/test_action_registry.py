from ultron_agent.core.action_registry import ActionRegistry
import pytest

def test_register_and_get_returns_callable():
    reg = ActionRegistry()
    reg.register('echo', lambda x: x)
    assert callable(reg.get('echo'))

def test_list_actions_contains_registered_names():
    reg = ActionRegistry()
    reg.register('echo', lambda x: x)
    assert 'echo' in reg.list_actions()

def test_get_unknown_action_raises_keyerror():
    reg = ActionRegistry()
    with pytest.raises(KeyError):
        reg.get('notfound')
