"""Local browser application. Start with: python app.py

Uses only the Python standard library. Binds to the loopback interface.
"""
import argparse
import os
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from engine import infer
from knowledge_base import GROUPS, QUESTIONS, RULES, SOURCES, rule_text

STATIC = Path(__file__).resolve().parent / "static"


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="application/json; charset=utf-8"):
        data = json.dumps(body, ensure_ascii=False).encode() if isinstance(body, (dict, list)) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/config":
            return self.send(200, {"groups": GROUPS, "questions": QUESTIONS, "sources": SOURCES,
                                   "rules": [{**r, "condition_text": rule_text(r)} for r in RULES]})
        files = {"/": ("index.html", "text/html"), "/style.css": ("style.css", "text/css"), "/app.js": ("app.js", "text/javascript")}
        if path not in files:
            return self.send(404, {"error": "Not found"})
        name, mime = files[path]
        self.send(200, (STATIC / name).read_bytes(), mime + "; charset=utf-8")

    def do_POST(self):
        if urlsplit(self.path).path != "/api/diagnose":
            return self.send(404, {"error": "Not found"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self.send(415, {"error": "Send application/json."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                raise ValueError("Request must contain 1 to 16384 bytes.")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or set(payload) != {"answers"}:
                raise ValueError("Request must contain only an answers object.")
            result = infer(payload["answers"])
        except (ValueError, UnicodeDecodeError) as error:
            return self.send(400, {"error": str(error)})
        self.send(200, result)

    def log_message(self, fmt, *args):
        pass  # No consultation answers are written to disk.


def main():
    parser = argparse.ArgumentParser(description="PlantCare Expert local application")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Cannot start server: {error}. Try --port 8001.\n")
    print(f"PlantCare Expert is ready at http://127.0.0.1:{args.port}", flush=True)
    print("Open that address in your browser. Press Ctrl+C here to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
