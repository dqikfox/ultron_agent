from __future__ import annotations

import threading
import time
from pathlib import Path
from queue import Queue, Empty
from typing import Callable, List, Optional

from .tasks import Task, Suggestion, DEFAULT_TASKS


Observer = Callable[[List[Suggestion]], None]


class MaverickEngine:
    """
    Background engine that scans the repository on an interval, produces suggestions,
    and can optionally apply them (disabled by default).
    """
    def __init__(
        self,
        repo_root: Path,
        tasks: Optional[List[Task]] = None,
        interval_seconds: int = 60,
        auto_apply: bool = False,
    ):
        self.repo_root = Path(repo_root).resolve()
        self.tasks = tasks or list(DEFAULT_TASKS)
        self.interval_seconds = max(10, interval_seconds)
        self.auto_apply = auto_apply

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._outbox: "Queue[List[Suggestion]]" = Queue()
        self._observers: List[Observer] = []

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def observe(self, fn: Observer) -> None:
        self._observers.append(fn)

    def poll(self, timeout: float = 0.0) -> Optional[List[Suggestion]]:
        try:
            return self._outbox.get(timeout=timeout)
        except Empty:
            return None

    def _emit(self, suggestions: List[Suggestion]) -> None:
        self._outbox.put(suggestions)
        for ob in list(self._observers):
            try:
                ob(suggestions)
            except Exception:
                # observers are best-effort
                pass

    def _collect(self) -> List[Suggestion]:
        suggestions: List[Suggestion] = []
        for task in self.tasks:
            try:
                out = task.run(self.repo_root)
                if out:
                    suggestions.extend(out)
            except Exception:
                # keep engine resilient
                continue
        return suggestions

    def _apply_all(self, suggestions: List[Suggestion]) -> None:
        if not self.auto_apply:
            return
        for s in suggestions:
            for task in self.tasks:
                try:
                    if s.metadata and s.metadata.get("task") == getattr(task, "name", ""):
                        applied = task.apply(self.repo_root, s)
                        if applied:
                            break
                except Exception:
                    continue

    def _loop(self) -> None:
        while not self._stop.is_set():
            suggestions = self._collect()
            if suggestions:
                self._emit(suggestions)
                self._apply_all(suggestions)
            # Sleep in small chunks to be more responsive to stop()
            for _ in range(self.interval_seconds):
                if self._stop.is_set():
                    break
                time.sleep(1)