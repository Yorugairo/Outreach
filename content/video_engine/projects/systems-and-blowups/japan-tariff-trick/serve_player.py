from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler   # THREADED (2026-09-09): one client streaming a Range or holding a socket wedged every other client - four render shards timed out on Page.goto against the single-threaded server
import os, sys, re

class RangeFileWrapper:
    def __init__(self, f, length):
        self.f = f
        self.remaining = length

    def read(self, size=-1):
        if self.remaining <= 0:
            return b""
        to_read = self.remaining if (size == -1 or size > self.remaining) else size
        data = self.f.read(to_read)
        self.remaining -= len(data)
        return data

    def close(self):
        self.f.close()

class RangeHTTPRequestHandler(SimpleHTTPRequestHandler):
    # P51 T1: .mjs is not in Python's mimetypes table on Windows, and a module served as
    # application/octet-stream is refused by the browser's strict MIME check - a split build
    # would show its shell and mount nothing.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.mjs': 'text/javascript'}

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-store')   # a rebuilt player.html is always the one served (2026-09-05)
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        range_header = self.headers.get('Range')
        if not range_header:
            return super().send_head()

        total_size = os.path.getsize(path)
        m = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not m:
            return super().send_head()

        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else total_size - 1

        if start >= total_size:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None

        end = min(end, total_size - 1)
        length = end - start + 1

        ctype = self.guess_type(path)
        self.send_response(206)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Range', f'bytes {start}-{end}/{total_size}')
        self.send_header('Content-Length', str(length))
        self.end_headers()

        f = open(path, 'rb')
        f.seek(start)
        return RangeFileWrapper(f, length)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__)))   # [dir]: the build to serve (build-short)
    server = ThreadingHTTPServer(('127.0.0.1', port), RangeHTTPRequestHandler)
    print(f"Serving Japan Tariff Trick review player on http://127.0.0.1:{port}/player.html with full Range/seek support...")
    server.serve_forever()
