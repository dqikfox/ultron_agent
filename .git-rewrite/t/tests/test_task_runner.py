from ultron_agent.core.action_registry import ActionRegistry
from ultron_agent.core.task_runner import TaskRunner
import pytest

def test_runs_sequential_tasks_and_collects_results():
    reg = ActionRegistry()
    reg.register('echo', lambda message: message)
    runner = TaskRunner(reg)
    plan = [{'action': 'echo', 'params': {'message': 'hello-world'}}]
    results = runner.run(plan)
    assert results[0]['result'] == 'hello-world'

def test_unknown_action_raises_runner_error():
    reg = ActionRegistry()
    runner = TaskRunner(reg)
    plan = [{'action': 'notfound', 'params': {}}]
    with pytest.raises(SystemExit):
        runner.run(plan)
