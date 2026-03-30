"""
Shared helpers for executing ADB commands and common device operations.
Centralizing these utilities avoids duplication between ADB Socket.IO
integrations while keeping a single place to adjust defaults.
"""

import base64
import os
import subprocess
from typing import Optional


def _resolve_adb_path(adb_path: Optional[str] = None) -> str:
    """Select the adb executable, preferring explicit override, then env, then default."""
    return adb_path or os.environ.get("ADB_PATH", "adb")


def run_adb_command(args, device=None, adb_path: Optional[str] = None):
    """Execute an adb command and return a result payload."""
    try:
        cmd = [_resolve_adb_path(adb_path)]
        if device:
            cmd.extend(["-s", device])
        cmd.extend(args)

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Command timeout (30s)"}
    except Exception as exc:  # pragma: no cover - passthrough error wrapper
        return {"success": False, "output": "", "error": str(exc)}


def get_devices(adb_path: Optional[str] = None):
    """Get list of connected devices."""
    result = run_adb_command(["devices", "-l"], adb_path=adb_path)
    if not result["success"]:
        return []

    devices = []
    for line in result["output"].split("\n")[1:]:
        if not line.strip() or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            serial = parts[0]
            status = parts[1]
            devices.append(
                {
                    "serial": serial,
                    "status": status,
                    "model": parts[3] if len(parts) > 3 else "Unknown",
                    "device": parts[5] if len(parts) > 5 else "Unknown",
                }
            )

    return devices


def execute_shell_command(device, command, adb_path: Optional[str] = None):
    """Execute shell command on device."""
    return run_adb_command(["shell", command], device, adb_path=adb_path)


def get_logcat(device, lines=100, adb_path: Optional[str] = None):
    """Get logcat output."""
    return run_adb_command(["logcat", "-d", "-t", str(lines)], device, adb_path=adb_path)


def clear_logcat(device, adb_path: Optional[str] = None):
    """Clear logcat."""
    return run_adb_command(["logcat", "-c"], device, adb_path=adb_path)


def get_process_list(device, adb_path: Optional[str] = None):
    """Get running processes."""
    return run_adb_command(["shell", "ps"], device, adb_path=adb_path)


def uninstall_app(device, package_name, adb_path: Optional[str] = None):
    """Uninstall application."""
    return run_adb_command(["uninstall", package_name], device, adb_path=adb_path)


def tap_screen(device, x, y, adb_path: Optional[str] = None):
    """Tap screen at coordinates."""
    return run_adb_command(["shell", "input", "tap", str(x), str(y)], device, adb_path=adb_path)


def swipe_screen(device, x1, y1, x2, y2, duration=500, adb_path: Optional[str] = None):
    """Swipe on screen."""
    return run_adb_command(
        ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)],
        device,
        adb_path=adb_path,
    )


def input_text(device, text, adb_path: Optional[str] = None):
    """Type text on device."""
    escaped_text = text.replace('"', '\\"').replace("'", "\\'")
    return run_adb_command(["shell", "input", "text", escaped_text], device, adb_path=adb_path)


def press_key(device, key_code, adb_path: Optional[str] = None):
    """Press hardware key."""
    return run_adb_command(["shell", "input", "keyevent", str(key_code)], device, adb_path=adb_path)


def take_screenshot(device, adb_path: Optional[str] = None):
    """Take device screenshot."""
    temp_path = "/sdcard/screenshot.png"
    result = run_adb_command(["shell", "screencap", "-p", temp_path], device, adb_path=adb_path)

    if result["success"]:
        local_path = "/tmp/adb_screenshot.png"
        pull_result = run_adb_command(["pull", temp_path, local_path], device, adb_path=adb_path)

        if pull_result["success"]:
            try:
                with open(local_path, "rb") as file_handle:
                    img_data = file_handle.read()
                    img_base64 = base64.b64encode(img_data).decode()
                    if os.path.exists(local_path):
                        os.remove(local_path)
                    return {"success": True, "image": img_base64}
            except Exception as exc:  # pragma: no cover - passthrough error wrapper
                return {"success": False, "error": str(exc)}

    return result


def list_files(device, path="/sdcard/", adb_path: Optional[str] = None):
    """List files in directory."""
    result = run_adb_command(["shell", "ls", "-la", path], device, adb_path=adb_path)
    if not result["success"]:
        return []

    files = []
    for line in result["output"].split("\n")[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 9:
            files.append(
                {
                    "name": parts[-1],
                    "size": parts[4],
                    "type": "d" if line.startswith("d") else "f",
                    "perms": parts[0],
                }
            )

    return files


def pull_file(device, remote_path, local_path=None, adb_path: Optional[str] = None):
    """Download file from device."""
    if not local_path:
        local_path = f"/tmp/{os.path.basename(remote_path)}"

    result = run_adb_command(["pull", remote_path, local_path], device, adb_path=adb_path)
    return {**result, "local_path": local_path}


def push_file(device, local_path, remote_path, adb_path: Optional[str] = None):
    """Upload file to device."""
    return run_adb_command(["push", local_path, remote_path], device, adb_path=adb_path)


def forward_port(device, local_port, remote_port, adb_path: Optional[str] = None):
    """Setup port forwarding."""
    return run_adb_command(["forward", f"tcp:{local_port}", f"tcp:{remote_port}"], device, adb_path=adb_path)


def reverse_forward(device, remote_port, local_port, adb_path: Optional[str] = None):
    """Setup reverse port forwarding."""
    return run_adb_command(["reverse", f"tcp:{remote_port}", f"tcp:{local_port}"], device, adb_path=adb_path)
