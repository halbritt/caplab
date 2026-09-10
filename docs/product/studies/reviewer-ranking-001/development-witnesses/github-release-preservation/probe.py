"""Exercise original fetch() against local, certificate-verified HTTPS."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import ssl
import sys
import threading
import urllib.parse
import urllib.request


def main() -> None:
    condition = sys.argv[1]
    if condition not in {"preflight", "ordinary", "low-eligible", "low-draft", "low-empty"}:
        raise ValueError("unknown condition")
    published = datetime.now(timezone.utc) - timedelta(hours=1)
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            parts = parsed.path.strip("/").split("/")
            repo = "/".join(parts[1:3]) if len(parts) == 4 and parts[0] == "repos" and parts[3] == "releases" else None
            search = parsed.path == "/search/repositories"
            if self.path == "/preflight" and condition == "preflight":
                status, body = 200, {"local_tls": True}
            elif search:
                status, body = 200, {"items": []}
            elif repo is None or parsed.query != "per_page=3":
                status, body = 404, {"unexpected_path": self.path}
            else:
                status = 200
                body = [] if condition == "low-empty" or repo not in {"openai/openai-python", "anthropics/anthropic-sdk-python"} else [{
                    "id": 101 if repo == "openai/openai-python" else 102,
                    "draft": condition == "low-draft", "prerelease": False,
                    "published_at": published.isoformat(),
                    "tag_name": "v1.0.0", "name": "Fixture release",
                    "html_url": f"https://github.com/{repo}/releases/tag/v1.0.0",
                    "body": "A release returned successfully by the fixture endpoint.",
                }]
            remaining = "50" if condition == "ordinary" or search else "1"
            payload = json.dumps(body).encode()
            requests.append({"path": self.path, "host": self.headers.get("Host"),
                             "authorization_present": "Authorization" in self.headers,
                             "status": status, "remaining": remaining,
                             "body": body, "body_bytes": len(payload)})
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-RateLimit-Remaining", remaining)
            self.send_header("X-RateLimit-Resource", "search" if search else "core")
            self.end_headers()
            self.wfile.write(payload)

    server = HTTPServer(("127.0.0.1", 443), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("/fixture/cert.pem", "/fixture/key.pem")
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        if condition == "preflight":
            # Default urllib verification must accept only our installed fixture CA.
            with urllib.request.urlopen("https://api.github.com/preflight", timeout=3) as response:
                result = json.load(response)
            if result != {"local_tls": True}:
                raise ValueError("TLS preflight response mismatch")
            output = {"condition": condition, "result": result}
        else:
            sys.path.insert(0, "/source")
            from newsroom.sources.github import GithubAdapter

            adapter = GithubAdapter({"state_dir": "/tmp/state"})
            articles = adapter.fetch(window_hours=72)
            output = {"condition": condition, "published_at": published.isoformat(),
                      "articles": [asdict(article) for article in articles],
                      "state": json.loads(Path("/tmp/state/github_trending_state.json").read_text())}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    output["requests"] = requests
    print(json.dumps(output, default=lambda value: value.isoformat(), sort_keys=True))


if __name__ == "__main__":
    main()
