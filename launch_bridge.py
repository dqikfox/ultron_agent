#!/usr/bin/env python3
"""
Direct Bridge Launcher - No CMD/PowerShell Required
This bypasses all shell restrictions by launching directly from Python
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    # Get script directory
    script_dir = Path(__file__).parent.absolute()

    # Set up environment
    os.chdir(script_dir)

    # Paths
    venv_python = script_dir / ".venv" / "Scripts" / "python.exe"
    bridge_script = script_dir / "copilot_amazon_q_bridge.py"

    print("=" * 50)
    print("COPILOT ↔ AMAZON Q DIRECT BRIDGE")
    print("=" * 50)
    print()

    # Verify files exist
    if not venv_python.exists():
        print(f"[ERROR] Python not found: {venv_python}")
        print("[*] Trying system Python instead...")
        venv_python = Path("python")

    if not bridge_script.exists():
        print(f"[ERROR] Bridge script not found: {bridge_script}")
        sys.exit(1)

    print(f"[+] Python: {venv_python}")
    print(f"[+] Script: {bridge_script}")
    print()
    print("[✓] Starting bridge in PRODUCTION mode...")
    print("[*] Press Ctrl+C to stop")
    print()

    try:
        # Launch bridge process directly
        result = subprocess.run(
            [str(venv_python), str(bridge_script), "--listen"],
            cwd=str(script_dir)
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[!] Bridge stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed to start bridge: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
