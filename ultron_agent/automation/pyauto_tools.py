from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

try:
    import pyautogui
    PYAUTO_AVAILABLE = True
except Exception:
    PYAUTO_AVAILABLE = False
    pyautogui = None


class DesktopAutomation:
    def __init__(self, safe_mode: bool = True, pause: float = 0.1):
        self.safe_mode = safe_mode
        if PYAUTO_AVAILABLE:
            pyautogui.PAUSE = pause
            pyautogui.FAILSAFE = True

    def available(self) -> bool:
        return PYAUTO_AVAILABLE

    def move_mouse(self, x: int, y: int, duration: float = 0.25):
        if not PYAUTO_AVAILABLE:
            return False
        pyautogui.moveTo(x, y, duration=duration)
        return True

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
        if not PYAUTO_AVAILABLE:
            return False
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button=button)
        else:
            pyautogui.click(button=button)
        return True

    def type_text(self, text: str, interval: float = 0.02):
        if not PYAUTO_AVAILABLE:
            return False
        pyautogui.typewrite(text, interval=interval)
        return True

    def screenshot(self, path: str | Path) -> Optional[str]:
        if not PYAUTO_AVAILABLE:
            return None
        img = pyautogui.screenshot()
        path = str(path)
        img.save(path)
        return path