import subprocess
import sys
import os

def test_cli_runs_plan_and_prints_summary():
    plan_path = os.path.join(os.path.dirname(__file__), 'data', 'plan_echo.yml')
    result = subprocess.run([sys.executable, '-m', 'ultron_agent.cli', 'run', '--plan', plan_path], capture_output=True)
    assert result.returncode == 0
    assert 'Ran 1 tasks successfully.' in result.stdout.decode()
    assert 'echo: hello-world' in result.stdout.decode()

def test_cli_unknown_action_exits_with_code_2_and_message():
    plan_path = os.path.join(os.path.dirname(__file__), 'data', 'plan_echo.yml')
    # Modify plan to use unknown action
    import yaml
    with open(plan_path, 'r') as f:
        plan = yaml.safe_load(f)
    plan['tasks'][0]['action'] = 'notfound'
    tmp_path = plan_path + '.tmp'
    with open(tmp_path, 'w') as f:
        yaml.safe_dump(plan, f)
    result = subprocess.run([sys.executable, '-m', 'ultron_agent.cli', 'run', '--plan', tmp_path], capture_output=True)
    assert result.returncode == 2
    assert 'Unknown action: notfound' in result.stdout.decode()
    os.remove(tmp_path)
