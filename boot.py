"""Runs inside a rented GPU pod. A tiny token-protected file/job server plus a hard self-destruct timer.

Started by session.py through the pod's start command. Only the Python standard library is used.
"""

import hmac
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOKEN = os.environ["CF_TOKEN"]
MAX_MIN = float(os.environ.get("CF_MAX_MINUTES", "45"))
WORK = Path("/work")
IN, OUT, LOG = WORK / "in", WORK / "out", WORK / "log.txt"
for d in (IN, OUT):
    d.mkdir(parents=True, exist_ok=True)
LOG.touch()


def self_destruct():
    """Delete this pod after MAX_MIN minutes no matter what the job or the laptop is doing."""
    time.sleep(MAX_MIN * 60)
    pod = os.environ.get("RUNPOD_POD_ID", "")
    with LOG.open("a") as f:
        f.write(f"\nWATCHDOG: {MAX_MIN} min limit reached, deleting pod {pod}\n")
    for cmd in (["runpodctl", "remove", "pod", pod], ["runpodctl", "pod", "delete", pod]):
        try:
            subprocess.run(cmd, timeout=60)
        except Exception:
            pass
    os._exit(1)


threading.Thread(target=self_destruct, daemon=True).start()
job = {"proc": None}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _ok(self):
        if hmac.compare_digest(self.headers.get("X-Token", ""), TOKEN):
            return True
        self.send_response(403)
        self.end_headers()
        return False

    def _send(self, body: bytes, code=200, ctype="application/octet-stream"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(b"ok", ctype="text/plain")
        if not self._ok():
            return
        if self.path.startswith("/log"):
            off = int(self.path.partition("=")[2] or 0)
            with LOG.open("rb") as f:
                f.seek(off)
                return self._send(f.read(), ctype="text/plain")
        if self.path == "/list":
            return self._send("\n".join(p.name for p in sorted(OUT.iterdir())).encode(), ctype="text/plain")
        if self.path.startswith("/out/"):
            p = OUT / Path(self.path[5:]).name
            return self._send(p.read_bytes()) if p.is_file() else self._send(b"", 404)
        self._send(b"", 404)

    def do_PUT(self):
        if not self._ok():
            return
        if not self.path.startswith("/upload/"):
            return self._send(b"", 404)
        data = self.rfile.read(int(self.headers["Content-Length"]))
        (IN / Path(self.path[8:]).name).write_bytes(data)
        self._send(b"saved", ctype="text/plain")

    def do_POST(self):
        if not self._ok():
            return
        if self.path == "/run" and job["proc"] is None:
            # tee to the container's stdout too, so progress shows in the RunPod console's Logs tab
            job["proc"] = subprocess.Popen(
                ["bash", "-c", "(cd /work/in && bash setup.sh && python -u job.py && echo JOB DONE || echo JOB FAILED)"
                 " 2>&1 | tee -a /work/log.txt"])
            return self._send(b"started", ctype="text/plain")
        self._send(b"busy or unknown", 409)


ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
