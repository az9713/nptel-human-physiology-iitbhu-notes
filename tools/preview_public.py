"""Read-only loopback preview with an explicit public-artifact allowlist."""
import argparse
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    allowed = {'/': ROOT/'index.html',
               '/assets/ATTRIBUTION.md': ROOT/'assets/ATTRIBUTION.md',
               '/assets/mathjax/LICENSE': ROOT/'assets/mathjax/LICENSE'}
    for path in ROOT.glob('*.html'):
        allowed['/'+path.name] = path
    for path in (ROOT/'code').glob('ch*.py'):
        if path.is_file():
            allowed['/'+path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT/'figures').glob('ch*.py'):
        if path.is_file():
            allowed['/'+path.relative_to(ROOT).as_posix()] = path
    suffixes = {'.html', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff',
                '.js', '.css', '.json', '.md', '.txt', '.woff2', '.zip', '.bin',
                '.mp4', '.webm', '.mov', '.vtt', '.avi'}
    for path in (ROOT/'assets').rglob('*'):
        if path.is_file() and path.suffix.lower() in suffixes:
            allowed['/'+path.relative_to(ROOT).as_posix()] = path

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            port = self.server.server_address[1]
            hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
            if self.headers.get('Host') not in hosts:
                self.send_error(403)
                return
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{h}' for h in hosts}:
                self.send_error(403)
                return
            key = unquote(urlsplit(self.path).path)
            path = allowed.get(key)
            if path is None or not path.is_file():
                self.send_error(404)
                return
            body = path.read_bytes()
            total = len(body)
            selected_range = self.headers.get('Range')
            start, end = 0, total - 1
            if selected_range:
                match = re.fullmatch(r'bytes=(\d*)-(\d*)', selected_range.strip())
                if match and total and any(match.groups()):
                    first, last = match.groups()
                    if first:
                        start = int(first)
                        end = min(int(last), total - 1) if last else total - 1
                    else:
                        suffix = int(last)
                        start = max(0, total - suffix)
                    valid = 0 <= start <= end < total
                else:
                    valid = False
                if not valid:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{total}')
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                body = body[start:end + 1]
            self.send_response(206 if selected_range else 200)
            self.send_header('Content-Type', mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Accept-Ranges', 'bytes')
            if selected_range:
                self.send_header('Content-Range', f'bytes {start}-{end}/{total}')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            # Teaching panels fetch only allowlisted local model data.
            self.send_header('Content-Security-Policy', "default-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; object-src 'self'")
            self.end_headers()
            if self.command != 'HEAD':
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # A metadata-only media request may close early.

        def do_HEAD(self):
            self.do_GET()

        def log_message(self, fmt, *values):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'PUBLIC_PREVIEW http://127.0.0.1:{server.server_address[1]}/ ({len(allowed)} allowlisted files)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
