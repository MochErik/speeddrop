"""Lightweight HTTP server for LAN file sending and receiving."""

import os
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional


class FileDropHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean terminal output
        return


def start_send_server(filepath: str, host: str, port: int):
    """Serve a single file for download across the local network."""
    directory = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    
    class SingleFileHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            return

        def do_GET(self):
            if self.path == "/" or self.path == "":
                self.send_response(302)
                self.send_header("Location", f"/{urllib.parse.quote(filename)}")
                self.end_headers()
            else:
                super().do_GET()

    httpd = HTTPServer((host, port), SingleFileHandler)
    file_size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)
    
    print(f"\n📦 Serving File: {filename} ({file_size_mb} MB)")
    print(f"🔗 LAN Download URL: http://{host}:{port}/{urllib.parse.quote(filename)}")
    print("Press Ctrl+C to stop sharing.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SpeedDrop...")
        httpd.server_close()


def start_receive_server(destination_dir: str, host: str, port: int):
    """Start local file receiving server with simple HTML upload form."""
    os.makedirs(destination_dir, exist_ok=True)

    class UploadHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            html = f"""<!DOCTYPE html>
<html>
<head><title>SpeedDrop Receive</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
.card {{ background: #1e293b; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 400px; width: 90%; }}
h2 {{ color: #38bdf8; margin-top: 0; }}
input[type=file] {{ margin: 1.5rem 0; color: #94a3b8; }}
button {{ background: #0284c7; color: white; border: none; padding: 0.75rem 1.5rem; font-size: 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: bold; width: 100%; }}
button:hover {{ background: #0369a1; }}
</style>
</head>
<body>
<div class="card">
  <h2>⚡ SpeedDrop LAN Receiver</h2>
  <p>Select a file to upload directly to this machine.</p>
  <form method="POST" enctype="multipart/form-data">
    <input type="file" name="file" required><br>
    <button type="submit">Send File</button>
  </form>
</div>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def do_POST(self):
            # Parse multipart upload
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            # Simple boundary parsing
            out_path = os.path.join(destination_dir, "speeddrop_received.bin")
            with open(out_path, "wb") as f:
                f.write(body)
                
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Upload Received Successfully!</h1><p>File saved to receiver.</p>")
            print(f"📥 File received and saved to {out_path}")

    httpd = HTTPServer((host, port), UploadHandler)
    print(f"\n📥 SpeedDrop Receiver listening on: http://{host}:{port}/")
    print("Open this URL on any phone or laptop on the same Wi-Fi to send files.")
    print("Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SpeedDrop receiver...")
        httpd.server_close()
