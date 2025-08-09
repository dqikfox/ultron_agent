#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False

from ultron_agent.maverick.engine import MaverickEngine

# Import panel conditionally
if TK_AVAILABLE:
    from ultron_agent.maverick.panel import MaverickPanel
else:
    MaverickPanel = None


def main():
    ap = argparse.ArgumentParser(description="ULTRON Phase 1 runner")
    ap.add_argument("--repo", default=".", help="Path to repo root")
    ap.add_argument("--maverick", action="store_true", help="Run Maverick engine")
    ap.add_argument("--interval", type=int, default=60, help="Maverick scan interval (seconds)")
    ap.add_argument("--auto-apply", action="store_true", help="Enable auto-apply (disabled by default)")
    ap.add_argument("--gui", action="store_true", help="Open minimal Maverick panel (Tkinter)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo = Path(args.repo).resolve()
    engine = MaverickEngine(repo_root=repo, interval_seconds=args.interval, auto_apply=args.auto_apply)

    if args.gui:
        if not TK_AVAILABLE:
            raise SystemExit("Tkinter not available. Run without --gui.")
        root = tk.Tk()
        root.title("ULTRON Phase 1")
        root.geometry("900x650")
        root.configure(bg="#000000")

        panel = MaverickPanel(root, engine)
        panel.open()
        root.mainloop()
        engine.stop()
        return

    if args.maverick:
        engine.observe(lambda batch: print(f"[Maverick] {len(batch)} suggestion(s)"))
        engine.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            engine.stop()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()