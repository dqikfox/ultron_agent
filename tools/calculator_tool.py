from .base import Tool
import math
import re

class CalculatorTool(Tool):
    name = "calculator"
    description = "Perform mathematical calculations and operations."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "The mathematical expression to evaluate."}
        },
        "required": ["expression"]
    }

    def __init__(self):
        super().__init__()

    def match(self, command: str) -> bool:
        cmd = command.lower()
        return any(x in cmd for x in ["calculate", "compute", "math", "solve", "+", "-", "*", "/", "sqrt", "sin", "cos", "tan"])

    def execute(self, command: str = "", expression: str = "") -> str:
        if not expression:
            # Extract expression from command
            expression = self._extract_expression(command)

        if not expression:
            return "No mathematical expression provided."

        try:
            # Safe evaluation with limited functions
            result = self._safe_eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating expression: {e}"

    def _extract_expression(self, command: str) -> str:
        """Extract mathematical expression from command text."""
        # Remove common words and keep only the mathematical part
        cmd = command.lower()
        cmd = re.sub(r'\b(calculate|compute|what is|what\'s|find|solve)\b', '', cmd)
        cmd = re.sub(r'[^\d\w\s\+\-\*\/\(\)\.\^\!\%]', '', cmd)  # Keep only math chars
        return cmd.strip()

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expression with limited functions."""
        # Define allowed functions and constants
        allowed_names = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "pow": pow,
            "factorial": math.factorial
        }

        # Replace ^ with ** for exponentiation
        expression = expression.replace("^", "**")

        # Use eval with restricted globals
        return eval(expression, {"__builtins__": {}}, allowed_names)
