"""Tiny CORS receiver: the player's __filmstrip() POSTs strip PNGs here."""
import http.server, base64, json, sys
from pathlib import Path
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "build-f/filmstrips")
OUT.mkdir(parents=True, exist_ok=True)

class H(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()
    def do_POST(self):
        n = int(self.headers["Content-Length"])
        d = json.loads(self.rfile.read(n))
        p = OUT / d["name"]
        p.write_bytes(base64.b64decode(d["png"].split(",", 1)[1]))
        print("saved", p, flush=True)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *a): pass

http.server.HTTPServer(("127.0.0.1", 8732), H).serve_forever()
