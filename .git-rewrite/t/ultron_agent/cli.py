import argparse
import yaml
from core.action_registry import ActionRegistry
from core.task_runner import TaskRunner
import sys

def echo_action(message):
    return message

def main():
    parser = argparse.ArgumentParser(description="Ultron Task Runner CLI")
    parser.add_argument("run", help="Run a plan YAML file", nargs="?")
    parser.add_argument("--plan", help="Path to plan YAML file")
    args = parser.parse_args()

    if args.run != "run" or not args.plan:
        print("Usage: ultron run --plan path/to/plan.yml")
        sys.exit(2)

    try:
        with open(args.plan, "r") as f:
            plan_data = yaml.safe_load(f)
    except Exception:
        print(f"Could not read plan file: {args.plan}")
        sys.exit(2)

    tasks = plan_data.get("tasks", [])
    registry = ActionRegistry()
    registry.register("echo", echo_action)
    runner = TaskRunner(registry)
    try:
        results = runner.run(tasks)
    except SystemExit as e:
        print(str(e))
        sys.exit(2)
    print(f"Ran {len(results)} tasks successfully.")
    for r in results:
        print(f"{r['action']}: {r['result']}")
    sys.exit(0)

if __name__ == "__main__":
    main()
