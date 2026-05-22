#!/usr/bin/env python3
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
_queue = []
_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != "/call":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        with _lock:
            _queue.append({
                "number": data.get("number", ""),
                "country": data.get("country", ""),
            })
        print(f"Received call: {data.get('number', '')} from {data.get('country', '')}")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        if self.path != "/poll":
            self.send_response(404)
            self.end_headers()
            return
        with _lock:
            if not _queue:
                self.send_response(204)
                self._cors()
                self.end_headers()
                return
            item = _queue.pop(0)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(item).encode())
        print(f"Polled call: {item['number']} from {item['country']}")
    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("", PORT), Handler)
    print(f"Server running on port {PORT}")
    server.serve_forever()
