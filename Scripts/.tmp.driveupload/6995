#!/usr/bin/env python3
"""
Grabs Substack session cookie from Chrome's network requests.
Opens a helper page that walks you through the 3-click process.

Usage: python3 grab_substack_cookie.py
"""
import http.server
import json
import os
import subprocess
import sys
import threading
import time

COOKIE_PATH = os.path.expanduser("~/.lhm_substack_cookie")

# Add venv for requests
from pathlib import Path
venv_site = "/Users/bob/LHM/Scripts/.venv/lib"
for d in Path(venv_site).glob("python*/site-packages"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

HTML = r"""<!DOCTYPE html>
<html><head><title>LHM - Substack Setup</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 650px; margin: 50px auto; padding: 20px; background: #0a1628; color: #e8edf3; }
h1 { color: #0089D1; font-size: 24px; }
.step { margin: 16px 0; padding: 16px; background: #0f1f38; border-left: 3px solid #0089D1; border-radius: 0 6px 6px 0; }
.step strong { color: #33CCFF; }
code { background: #1e3350; padding: 3px 8px; border-radius: 4px; font-size: 14px; }
textarea { width: 100%; font-family: monospace; font-size: 13px; background: #1e3350; color: #e8edf3; border: 1px solid #0089D1; padding: 10px; border-radius: 6px; resize: vertical; }
button { background: #0089D1; color: white; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; cursor: pointer; border-radius: 6px; margin-top: 12px; }
button:hover { background: #006da8; }
#status { margin-top: 16px; padding: 14px; border-radius: 6px; display: none; font-weight: bold; }
.success { background: #00BB99; color: white; display: block !important; }
.error { background: #FF2389; color: white; display: block !important; }
img { max-width: 100%; border-radius: 6px; margin: 8px 0; }
ol li { margin: 6px 0; }
</style></head>
<body>
<h1>Lighthouse Macro — Substack Cookie Setup</h1>
<p style="color:#6b7d99">One-time setup. Takes 60 seconds.</p>

<div class="step">
<strong>Step 1:</strong> Open <a href="https://substack.com" target="_blank" style="color:#33CCFF">substack.com</a> in Chrome. Make sure you're logged in.
</div>

<div class="step">
<strong>Step 2:</strong> Press <code>Cmd+Option+I</code> to open DevTools, then click the <strong>Network</strong> tab.
</div>

<div class="step">
<strong>Step 3:</strong> In the Network tab, reload the page (<code>Cmd+R</code>). You'll see requests appear.
</div>

<div class="step">
<strong>Step 4:</strong> Click on the very first request (usually <code>substack.com</code> or <code>/</code>).
On the right side, scroll down in the <strong>Headers</strong> section to find <strong>Request Headers</strong>.
Find the line that says <code>cookie:</code> and copy the ENTIRE value (it's very long).
</div>

<div class="step">
<strong>Step 5:</strong> Paste it below:
<br><br>
<textarea id="cookiebox" rows="5" placeholder="Paste the full cookie: header value here..."></textarea>
<br>
<button onclick="saveCookie()">Save & Test Connection</button>
</div>

<div id="status"></div>

<script>
function saveCookie() {
    var cookies = document.getElementById('cookiebox').value.trim();
    if (!cookies) { alert('Paste the cookie string first'); return; }
    // Strip "cookie: " prefix if they copied the header name too
    if (cookies.toLowerCase().startsWith('cookie:')) {
        cookies = cookies.substring(7).trim();
    }
    document.getElementById('status').style.display = 'block';
    document.getElementById('status').className = '';
    document.getElementById('status').innerHTML = 'Testing connection...';

    fetch('/save_cookie', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cookies: cookies})
    }).then(r => r.json()).then(data => {
        var el = document.getElementById('status');
        if (data.success) {
            el.className = 'success';
            el.innerHTML = '&#10003; Connected as: ' + data.user + '<br>Cookie saved! You can close this tab.';
        } else {
            el.className = 'error';
            el.innerHTML = '&#10007; ' + data.error + '<br>Try again — make sure you copied the full cookie value.';
        }
    }).catch(e => {
        document.getElementById('status').className = 'error';
        document.getElementById('status').innerHTML = 'Request failed: ' + e;
    });
}
</script>
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path == "/save_cookie":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            cookies_str = body.get("cookies", "")

            # Verify connect.sid exists
            has_sid = "connect.sid=" in cookies_str
            if not has_sid:
                self._respond({"success": False, "error": "No connect.sid found in cookie string"})
                return

            # Test the cookie against Substack API
            import requests
            session = requests.Session()
            # Parse and set all cookies
            for part in cookies_str.split(";"):
                part = part.strip()
                if "=" in part:
                    key, val = part.split("=", 1)
                    session.cookies.set(key.strip(), val.strip())

            try:
                r = session.get("https://substack.com/api/v1/user/profile/self", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    name = data.get("name", "Unknown")
                    # Save the cookie string
                    with open(COOKIE_PATH, "w") as f:
                        f.write(cookies_str)
                    os.chmod(COOKIE_PATH, 0o600)
                    self._respond({"success": True, "user": name})
                    # Shutdown after success
                    threading.Thread(target=lambda: (time.sleep(2), os._exit(0))).start()
                else:
                    self._respond({"success": False, "error": f"Auth failed (HTTP {r.status_code})"})
            except Exception as e:
                self._respond({"success": False, "error": str(e)})

    def _respond(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


def main():
    port = 9876
    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Opening cookie setup at {url}")
    print("Follow the steps in the browser window.")
    print("(Ctrl+C to cancel)\n")
    subprocess.Popen(["open", url])
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCancelled.")


if __name__ == "__main__":
    main()
