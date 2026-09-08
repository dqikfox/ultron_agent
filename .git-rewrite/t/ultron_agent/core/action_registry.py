class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register(self, name, handler):
        self._actions[name] = handler

    def get(self, name):
        if name not in self._actions:
            raise KeyError(f"Unknown action: {name}")
        return self._actions[name]

    def list_actions(self):
        return list(self._actions.keys())
