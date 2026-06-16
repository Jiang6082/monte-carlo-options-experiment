"""Serve the static dashboard locally."""

from __future__ import annotations

import contextlib
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    dashboard_dir = repo_root / "dashboard"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8877

    class DashboardHandler(QuietHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(dashboard_dir), **kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"Serving dashboard at http://127.0.0.1:{port}", flush=True)
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


if __name__ == "__main__":
    main()
