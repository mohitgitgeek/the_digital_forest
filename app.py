from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse

from digital_forest import DigitalForestGame


game = DigitalForestGame()


class ForestRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.serve_file("index.html", "text/html; charset=utf-8")
            return

        if parsed.path == "/api/state":
            self.send_json(game.get_state())
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/move":
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 0

            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            payload = json.loads(body or "{}")
            direction = str(payload.get("direction", "")).lower()
            result = game.move_player(direction)
            self.send_json({"ok": result["ok"], "message": result["message"], "state": game.get_state()})
            return

        if parsed.path == "/api/reset":
            game.reset()
            self.send_json(game.get_state())
            return

        self.send_error(404, "Not Found")

    def send_json(self, payload, status=200):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def serve_file(self, filename, content_type):
        try:
            with open(filename, "r", encoding="utf-8") as handle:
                content = handle.read().encode("utf-8")
        except FileNotFoundError:
            self.send_error(404, "File not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), ForestRequestHandler)
    print("The Digital Forest is running at http://localhost:8000")
    server.serve_forever()
