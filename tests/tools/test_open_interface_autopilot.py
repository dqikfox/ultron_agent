from tools.open_interface_autopilot import OpenInterfaceConfig, LLMPlanner


def build_planner(max_actions: int = 3) -> LLMPlanner:
    config = OpenInterfaceConfig(max_actions_per_step=max_actions)
    return LLMPlanner(config)


def test_parse_response_handles_code_fences() -> None:
    planner = build_planner(max_actions=2)
    response = """```json
    {
        "reasoning": "Testing parser",
        "confidence": 0.85,
        "actions": [
            {"type": "click", "x": 100, "y": 200},
            {"type": "type", "text": "hello world"},
            {"type": "wait", "seconds": 1.5}
        ]
    }
    ```"""

    parsed = planner._parse_response(response)

    assert parsed["reasoning"] == "Testing parser"
    assert parsed["confidence"] == 0.85
    # Limited to configured max_actions_per_step
    assert len(parsed["actions"]) == 2
    assert parsed["actions"][0]["type"] == "click"


def test_normalize_action_accepts_strings() -> None:
    planner = build_planner()
    normalized = planner._normalize_action("type hello")
    assert normalized["type"] == "type"
    assert normalized["text"] == "type hello"
