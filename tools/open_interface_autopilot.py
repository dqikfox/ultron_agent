"""
Open Interface Autopilot Core
Implements the core ideas from https://github.com/AmberSahdev/Open-Interface
so ULTRON can drive the desktop with LLM-generated plans.
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import mss  # type: ignore

    MSS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    mss = None
    MSS_AVAILABLE = False

try:
    import pyautogui  # type: ignore

    PYAUTOGUI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

from PIL import Image

import requests

from utils.ultron_logger import log_info, log_error, log_ai_decision


def _bool_from_env(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_from_env(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _float_from_env(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


@dataclass
class OpenInterfaceConfig:
    """Holds configurable knobs for Open Interface style automation."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-1.5-flash"
    custom_base_url: Optional[str] = None
    custom_model: Optional[str] = None
    max_iterations: int = 6
    max_actions_per_step: int = 6
    history_limit: int = 5
    temperature: float = 0.2
    max_output_tokens: int = 800
    action_delay_seconds: float = 0.35
    retry_delay_seconds: float = 1.0
    monitor_index: int = 1
    screenshot_dir: Path = Path("screenshots/open_interface")
    log_dir: Path = Path("logs/open_interface")
    allow_mouse_fail_safe: bool = True
    cursor_pause_seconds: float = 0.05
    course_correction: bool = True
    provider_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.screenshot_dir, str):
            self.screenshot_dir = Path(self.screenshot_dir)
        if isinstance(self.log_dir, str):
            self.log_dir = Path(self.log_dir)
        self.provider = (self.provider or "openai").lower()


def load_open_interface_config(overrides: Optional[Dict[str, Any]] = None) -> OpenInterfaceConfig:
    """Load configuration from ultron_config.json, env vars, and overrides."""

    config_data: Dict[str, Any] = {}
    config_path = Path("ultron_config.json")

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as src:
                raw_cfg = json.load(src)
            config_data = raw_cfg.get("open_interface") or raw_cfg.get("openai_computer_use", {})
        except Exception as exc:  # pragma: no cover - config parsing issues
            log_error("open_interface", f"Failed to read ultron_config.json: {exc}")

    env_overrides: Dict[str, Any] = {}
    env_map = {
        "provider": ("OPEN_INTERFACE_PROVIDER", str),
        "model": ("OPEN_INTERFACE_MODEL", str),
        "gemini_model": ("OPEN_INTERFACE_GEMINI_MODEL", str),
        "custom_base_url": ("OPEN_INTERFACE_BASE_URL", str),
        "custom_model": ("OPEN_INTERFACE_CUSTOM_MODEL", str),
        "screenshot_dir": ("OPEN_INTERFACE_SCREENSHOT_DIR", str),
        "log_dir": ("OPEN_INTERFACE_LOG_DIR", str),
    }
    for field_name, (env_key, _type) in env_map.items():
        env_val = os.getenv(env_key)
        if env_val:
            env_overrides[field_name] = env_val

    numeric_env = {
        "max_iterations": ("OPEN_INTERFACE_MAX_ITERATIONS", _int_from_env),
        "max_actions_per_step": ("OPEN_INTERFACE_MAX_ACTIONS", _int_from_env),
        "history_limit": ("OPEN_INTERFACE_HISTORY_LIMIT", _int_from_env),
        "temperature": ("OPEN_INTERFACE_TEMPERATURE", _float_from_env),
        "max_output_tokens": ("OPEN_INTERFACE_MAX_TOKENS", _int_from_env),
        "action_delay_seconds": ("OPEN_INTERFACE_ACTION_DELAY", _float_from_env),
        "retry_delay_seconds": ("OPEN_INTERFACE_RETRY_DELAY", _float_from_env),
        "monitor_index": ("OPEN_INTERFACE_MONITOR_INDEX", _int_from_env),
    }
    for field_name, (env_key, caster) in numeric_env.items():
        env_val = caster(os.getenv(env_key))
        if env_val is not None:
            env_overrides[field_name] = env_val

    bool_env = {
        "allow_mouse_fail_safe": "OPEN_INTERFACE_FAILSAFE",
        "course_correction": "OPEN_INTERFACE_COURSE_CORRECTION",
    }
    for field_name, env_key in bool_env.items():
        env_val = _bool_from_env(os.getenv(env_key))
        if env_val is not None:
            env_overrides[field_name] = env_val

    merged: Dict[str, Any] = {**config_data, **env_overrides}
    if overrides:
        merged.update(overrides)

    provider_options = merged.get("provider_options", {})
    merged["provider_options"] = provider_options

    return OpenInterfaceConfig(**merged)


class ScreenshotManager:
    """Captures screenshots and emits base64 payloads for the LLM."""

    def __init__(self, config: OpenInterfaceConfig) -> None:
        self.config = config
        self.config.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, *, include_base64: bool = True) -> Tuple[str, Optional[str]]:
        """Capture the current primary monitor."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = self.config.screenshot_dir / f"open_interface_{timestamp}.png"

        image = self._grab_frame()
        image.save(filename)

        if not include_base64:
            return str(filename), None

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return str(filename), encoded

    def _grab_frame(self) -> Image.Image:
        if MSS_AVAILABLE:
            with mss.mss() as sct:  # type: ignore[attr-defined]
                monitors = sct.monitors
                monitor_index = max(1, min(self.config.monitor_index, len(monitors) - 1))
                frame = sct.grab(monitors[monitor_index])
                return Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")

        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("Neither mss nor pyautogui is available for screenshots.")

        return pyautogui.screenshot()  # type: ignore[call-arg]


class LLMPlanner:
    """Produces action plans by prompting the selected LLM."""

    SYSTEM_PROMPT = (
        "You are Open Interface, an autonomous computer control specialist. "
        "Given a goal, the latest desktop screenshot, and a short history of what "
        "already happened, reply with a strict JSON object containing:\n"
        "reasoning: short thought process\n"
        "confidence: float 0-1 about finishing soon\n"
        "actions: array describing the next low-level actions required. "
        "Each action MUST include a 'type' field with one of "
        "[move, click, double_click, right_click, drag, scroll, type, key, hotkey, wait, screenshot, finish]. "
        "For pointing actions include pixel coordinates. For typing send the exact text."
    )

    def __init__(self, config: OpenInterfaceConfig) -> None:
        self.config = config
        self._openai_client = None
        self._gemini_model = None

    def plan(
        self,
        goal: str,
        screenshot_b64: str,
        history: str,
        step: int,
    ) -> Dict[str, Any]:
        """Return the parsed JSON plan from the LLM."""
        user_prompt = self._build_prompt(goal, history, step)
        raw_text = ""

        try:
            if self.config.provider == "gemini":
                raw_text = self._call_gemini(user_prompt, screenshot_b64)
            elif self.config.provider == "custom":
                raw_text = self._call_custom(user_prompt, screenshot_b64)
            else:
                raw_text = self._call_openai(user_prompt, screenshot_b64)
        except Exception as exc:
            log_error("open_interface", f"LLM call failed: {exc}")
            raise

        return self._parse_response(raw_text)

    def _build_prompt(self, goal: str, history: str, step: int) -> str:
        history_summary = history or "No previous steps executed."
        return (
            f"Goal: {goal}\n"
            f"Current step: {step}\n"
            f"Previous steps summary:\n{history_summary}\n\n"
            "Respond ONLY with JSON matching this schema:\n"
            "{\n"
            '  "reasoning": "string",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "actions": [\n'
            '    {"type": "move", "x": 100, "y": 200, "duration": 0.2},\n'
            '    {"type": "click", "x": 100, "y": 200, "button": "left"},\n'
            '    {"type": "type", "text": "hello world"},\n'
            '    {"type": "key", "key": "enter"},\n'
            '    {"type": "hotkey", "keys": ["ctrl", "l"]},\n'
            '    {"type": "wait", "seconds": 1.0},\n'
            '    {"type": "finish", "message": "Describe accomplishment"}\n'
            "  ]\n"
            "}\n"
            "Avoid duplicate or redundant actions. Never hallucinate data."
        )

    def _call_openai(self, prompt: str, screenshot_b64: str) -> str:
        if self._openai_client is None:
            from openai import OpenAI  # lazy import

            api_key = (
                self.config.provider_options.get("openai_api_key")
                or os.getenv("OPENAI_API_KEY")
            )
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is required for Open Interface.")

            base_url = self.config.custom_base_url or os.getenv("OPENAI_BASE_URL")
            self._openai_client = OpenAI(api_key=api_key, base_url=base_url)

        response = self._openai_client.chat.completions.create(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_b64}"
                            },
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content or ""

    def _call_gemini(self, prompt: str, screenshot_b64: str) -> str:
        import google.generativeai as genai  # type: ignore

        if self._gemini_model is None:
            api_key = (
                self.config.provider_options.get("gemini_api_key")
                or os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_GEMINI_API_KEY")
            )
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is required for Gemini provider.")

            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel(self.config.gemini_model)

        image_bytes = base64.b64decode(screenshot_b64)
        generation_config = {
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_output_tokens,
        }
        response = self._gemini_model.generate_content(
            [
                self.SYSTEM_PROMPT,
                prompt,
                {"mime_type": "image/png", "data": image_bytes},
            ],
            generation_config=generation_config,
        )
        return response.text or ""

    def _call_custom(self, prompt: str, screenshot_b64: str) -> str:
        base_url = self.config.custom_base_url
        if not base_url:
            raise RuntimeError("custom_base_url must be set for provider=custom.")

        api_key = (
            self.config.provider_options.get("custom_api_key")
            or os.getenv("OPEN_INTERFACE_CUSTOM_API_KEY")
            or os.getenv("CUSTOM_LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": self.config.custom_model or self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_output_tokens,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"{prompt}\nSCREENSHOT_BASE64::{screenshot_b64}",
                },
            ],
        }

        endpoint = base_url.rstrip("/") + "/v1/chat/completions"
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content

    def _parse_response(self, text: str) -> Dict[str, Any]:
        if not text:
            raise RuntimeError("LLM returned empty response.")

        raw = text.strip()
        if "```" in raw:
            segments = raw.split("```")
            # Prefer the first JSON-looking segment
            for segment in segments:
                candidate = segment.strip()
                if candidate.startswith("{") and candidate.endswith("}"):
                    raw = candidate
                    break
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Attempt to salvage by finding substring between braces
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                raise
            parsed = json.loads(raw[start : end + 1])

        parsed.setdefault("actions", [])
        parsed.setdefault("reasoning", "No reasoning provided")
        parsed.setdefault("confidence", 0.0)

        # Trim actions to configured limit
        actions = parsed["actions"][: self.config.max_actions_per_step]
        parsed["actions"] = [self._normalize_action(action) for action in actions]
        return parsed

    @staticmethod
    def _normalize_action(action: Any) -> Dict[str, Any]:
        if isinstance(action, str):
            return {"type": "type", "text": action}
        if not isinstance(action, dict):
            return {"type": "wait", "seconds": 0.5}

        normalized = {"type": action.get("type", "").lower()}
        for key, value in action.items():
            if key == "type":
                continue
            normalized[key] = value
        if not normalized["type"]:
            normalized["type"] = "wait"
        return normalized


class DesktopActionExecutor:
    """Executes low-level actions using PyAutoGUI."""

    def __init__(self, config: OpenInterfaceConfig, screenshot_manager: ScreenshotManager) -> None:
        if not PYAUTOGUI_AVAILABLE:
            raise RuntimeError("PyAutoGUI is required for desktop automation.")

        self.config = config
        self.screenshot_manager = screenshot_manager
        pyautogui.FAILSAFE = config.allow_mouse_fail_safe  # type: ignore[attr-defined]
        pyautogui.PAUSE = config.cursor_pause_seconds  # type: ignore[attr-defined]

    def execute(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        logs: List[str] = []
        errors: List[str] = []
        finish_message: Optional[str] = None
        last_screenshot: Optional[str] = None

        for idx, action in enumerate(actions):
            action_type = action.get("type", "").lower()
            try:
                if action_type in {"move", "mouse_move"}:
                    logs.append(self._handle_move(action))
                elif action_type in {"click", "single_click"}:
                    logs.append(self._handle_click(action, clicks=1))
                elif action_type == "double_click":
                    logs.append(self._handle_click(action, clicks=2))
                elif action_type == "right_click":
                    logs.append(self._handle_click(action, clicks=1, button="right"))
                elif action_type == "drag":
                    logs.append(self._handle_drag(action))
                elif action_type == "scroll":
                    logs.append(self._handle_scroll(action))
                elif action_type == "type":
                    logs.append(self._handle_type(action))
                elif action_type == "key":
                    logs.append(self._handle_key(action))
                elif action_type == "hotkey":
                    logs.append(self._handle_hotkey(action))
                elif action_type == "wait":
                    logs.append(self._handle_wait(action))
                elif action_type == "screenshot":
                    last_screenshot = self._handle_screenshot_action()
                    logs.append(f"Screenshot captured: {last_screenshot}")
                elif action_type == "finish":
                    finish_message = action.get("message") or "Goal marked complete by LLM."
                    logs.append(finish_message)
                else:
                    errors.append(f"Unsupported action type: {action_type}")
            except Exception as exc:  # pragma: no cover - device specific
                errors.append(f"{action_type} failed: {exc}")

            time.sleep(self.config.action_delay_seconds)

        return {
            "logs": logs,
            "errors": errors,
            "finish_message": finish_message,
            "last_screenshot": last_screenshot,
        }

    def _handle_move(self, action: Dict[str, Any]) -> str:
        x = int(action.get("x", 0))
        y = int(action.get("y", 0))
        duration = float(action.get("duration", 0.1))
        pyautogui.moveTo(x, y, duration=duration)  # type: ignore[attr-defined]
        return f"Moved mouse to ({x}, {y})"

    def _handle_click(
        self,
        action: Dict[str, Any],
        *,
        clicks: int,
        button: str = "left",
    ) -> str:
        x = action.get("x")
        y = action.get("y")
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), clicks=clicks, button=button)  # type: ignore[attr-defined]
        else:
            pyautogui.click(clicks=clicks, button=button)  # type: ignore[attr-defined]
        return f"Clicked ({button}) {clicks}x at ({x}, {y})"

    def _handle_drag(self, action: Dict[str, Any]) -> str:
        start_x = int(action.get("start_x", pyautogui.position().x))  # type: ignore[attr-defined]
        start_y = int(action.get("start_y", pyautogui.position().y))  # type: ignore[attr-defined]
        end_x = int(action.get("end_x", start_x))
        end_y = int(action.get("end_y", start_y))
        duration = float(action.get("duration", 0.5))
        pyautogui.moveTo(start_x, start_y, duration=0.1)  # type: ignore[attr-defined]
        pyautogui.dragTo(end_x, end_y, duration=duration)  # type: ignore[attr-defined]
        return f"Dragged cursor from ({start_x},{start_y}) to ({end_x},{end_y})"

    def _handle_scroll(self, action: Dict[str, Any]) -> str:
        clicks = int(action.get("clicks", action.get("amount", -400)))
        x = action.get("x")
        y = action.get("y")
        pyautogui.scroll(clicks, x=x, y=y)  # type: ignore[attr-defined]
        return f"Scrolled {'up' if clicks > 0 else 'down'} {abs(clicks)} units"

    def _handle_type(self, action: Dict[str, Any]) -> str:
        text = action.get("text") or ""
        interval = float(action.get("interval", 0.02))
        pyautogui.typewrite(text, interval=interval)  # type: ignore[attr-defined]
        return f"Typed text ({len(text)} chars)"

    def _handle_key(self, action: Dict[str, Any]) -> str:
        key = action.get("key") or action.get("name")
        if not key:
            raise ValueError("key action missing 'key'")
        pyautogui.press(key)  # type: ignore[attr-defined]
        return f"Pressed key {key}"

    def _handle_hotkey(self, action: Dict[str, Any]) -> str:
        keys = action.get("keys") or []
        if isinstance(keys, str):
            keys = [keys]
        if not keys:
            raise ValueError("hotkey action missing 'keys'")
        pyautogui.hotkey(*keys)  # type: ignore[attr-defined]
        return f"Pressed hotkey {'+'.join(keys)}"

    def _handle_wait(self, action: Dict[str, Any]) -> str:
        seconds = float(action.get("seconds", 0.5))
        time.sleep(seconds)
        return f"Waited {seconds:.2f}s"

    def _handle_screenshot_action(self) -> str:
        path, _ = self.screenshot_manager.capture(include_base64=False)
        return path


class OpenInterfaceSession:
    """Coordinates repeated LLM planning + execution cycles."""

    def __init__(
        self,
        config: Optional[OpenInterfaceConfig] = None,
        *,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config = config or load_open_interface_config(overrides)
        self.screenshot_manager = ScreenshotManager(self.config)
        self.planner = LLMPlanner(self.config)
        self.executor = DesktopActionExecutor(self.config, self.screenshot_manager)
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

    def run(self, goal: str) -> Dict[str, Any]:
        history: List[Dict[str, Any]] = []
        formatted_history = ""
        session_log: List[Dict[str, Any]] = []
        finish_message: Optional[str] = None
        completed = False

        for step in range(1, self.config.max_iterations + 1):
            screenshot_path, screenshot_b64 = self.screenshot_manager.capture()

            plan = self.planner.plan(goal, screenshot_b64, formatted_history, step)
            log_ai_decision(
                "open_interface",
                f"Planned {len(plan['actions'])} actions",
                ai_model=self.config.model,
                confidence_score=plan.get("confidence"),
            )

            execution = self.executor.execute(plan["actions"])

            step_entry = {
                "step": step,
                "screenshot": screenshot_path,
                "plan": plan,
                "execution": execution,
            }
            session_log.append(step_entry)

            summary = self._summarize_step(step_entry)
            history.append({"step": step, "summary": summary})
            history = history[-self.config.history_limit :]
            formatted_history = "\n".join(entry["summary"] for entry in history)

            log_info("open_interface", summary)

            if execution.get("finish_message"):
                finish_message = execution["finish_message"]
                completed = True
                break
            if plan["actions"] and plan["actions"][-1].get("type") == "finish":
                finish_message = plan["actions"][-1].get("message")
                completed = True
                break

        if not finish_message:
            finish_message = "Autopilot run ended without explicit completion."

        log_path = self._persist_session(goal, session_log, finished=completed, finish_message=finish_message)

        return {
            "goal": goal,
            "completed": completed,
            "finish_message": finish_message,
            "steps": session_log,
            "log_path": log_path,
        }

    def _summarize_step(self, entry: Dict[str, Any]) -> str:
        step = entry["step"]
        plan = entry["plan"]
        execution = entry["execution"]
        reasoning = plan.get("reasoning", "")
        actions = len(plan.get("actions", []))
        errors = execution.get("errors") or []
        error_text = f" Errors: {errors}" if errors else ""
        return f"Step {step}: {actions} actions planned. Reasoning: {reasoning[:120]}{error_text}"

    def _persist_session(
        self,
        goal: str,
        log: List[Dict[str, Any]],
        *,
        finished: bool,
        finish_message: str,
    ) -> str:
        payload = {
            "goal": goal,
            "finished": finished,
            "finish_message": finish_message,
            "created_at": self.session_id,
            "steps": log,
        }
        log_file = self.config.log_dir / f"session_{self.session_id}.json"
        with open(log_file, "w", encoding="utf-8") as dst:
            json.dump(payload, dst, indent=2)

        return str(log_file)


def run_open_interface(goal: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper for callers who just want to trigger a session."""
    session = OpenInterfaceSession(overrides=overrides)
    return session.run(goal)
