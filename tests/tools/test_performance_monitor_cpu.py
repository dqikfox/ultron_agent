import types

import pytest

from tools import performance_monitor


pytestmark = pytest.mark.unit


class FakeProcess:
    def __init__(self, name: str, cpu_values):
        self.info = {"name": name}
        self._cpu_values = list(cpu_values)
        self.cpu_percent_calls = []
        self.pid = abs(hash(name)) % 10000

    def cpu_percent(self, interval=None):
        self.cpu_percent_calls.append(interval)
        if self._cpu_values:
            return self._cpu_values.pop(0)
        return 0.0


def test_cpu_analysis_avoids_per_process_sleep(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr(performance_monitor.time, "sleep", lambda seconds: sleep_calls.append(seconds))

    fake_processes = [
        FakeProcess("proc-a", [0.0, 10.0]),
        FakeProcess("proc-b", [0.0, 20.0]),
    ]

    # Patch psutil dependencies used inside PerformanceMonitor
    monkeypatch.setattr(performance_monitor.psutil, "Process", lambda: FakeProcess("agent", [0.0, 5.0]))
    monkeypatch.setattr(performance_monitor.psutil, "cpu_times_percent", lambda interval=0.1: types.SimpleNamespace(user=1.0, system=2.0, idle=97.0))
    monkeypatch.setattr(performance_monitor.psutil, "cpu_count", lambda logical=False: 8 if logical else 4)
    monkeypatch.setattr(performance_monitor.psutil, "cpu_percent", lambda interval=None: 12.5)
    monkeypatch.setattr(performance_monitor.psutil, "process_iter", lambda attrs=None: fake_processes)

    monitor = performance_monitor.PerformanceMonitor()

    result = monitor.get_cpu_analysis()

    assert "CPU Usage Analysis" in result
    # Only one global sleep should occur while sampling CPU usage
    assert sleep_calls == [0.1]
    # Each process should only require two cpu_percent calls (prime + sample)
    assert all(proc.cpu_percent_calls == [None, None] for proc in fake_processes)
