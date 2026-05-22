from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = b''
            while len(body) < length:
                chunk = self.rfile.read(length - len(body))
                if not chunk:
                    break
                body += chunk
            data = json.loads(body.decode('utf-8'))
            path = data['path']
            content = data['content']
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'ok')
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())
    def log_message(self, *a): pass

server = HTTPServer(('127.0.0.1', 18765), Handler)
server.serve_forever()
