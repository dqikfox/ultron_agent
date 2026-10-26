from .action_registry import ActionRegistry

class TaskRunner:
    def __init__(self, registry: ActionRegistry):
        self.registry = registry

    def run(self, plan: list):
        results = []
        for task in plan:
            action = task.get('action')
            params = task.get('params', {})
            try:
                handler = self.registry.get(action)
                result = handler(**params)
                results.append({'action': action, 'result': result})
            except KeyError:
                raise SystemExit(f"Unknown action: {action}")
        return results
