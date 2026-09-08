import http.server
import os
import socketserver
import urllib.parse

PORT = 5173
DIRECTORY = os.path.join(os.path.dirname(__file__), "frontend")

class VaxKavachHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        # Decode url
        parsed = urllib.parse.urlparse(path)
        clean_path = parsed.path

        # URL rewrites matching vite.config.js
        if clean_path in ["/", "", "/index.html"]:
            path = "/landing.html"
        elif clean_path in ["/overview", "/overview/"]:
            path = "/overview.html"
        elif clean_path in ["/shipments", "/shipments/"]:
            path = "/shipments.html"
        elif clean_path.startswith("/shipments/") and len(clean_path.split("/")) > 2 and not clean_path.endswith(".html"):
            path = "/shipment.html"
        elif clean_path in ["/problems", "/problems/"]:
            path = "/problems.html"
        elif clean_path.startswith("/problems/") and len(clean_path.split("/")) > 2 and not clean_path.endswith(".html"):
            path = "/problem.html"
        elif clean_path in ["/map", "/map/"]:
            path = "/map.html"
        elif clean_path in ["/fleet", "/fleet/"]:
            path = "/fleet.html"
        elif clean_path in ["/history", "/history/"]:
            path = "/history.html"
        elif clean_path in ["/technical", "/technical/"]:
            path = "/technical.html"
        elif clean_path in ["/settings", "/settings/"]:
            path = "/settings.html"
        elif clean_path in ["/syringe-3d", "/syringe-3d/"]:
            path = "/syringe-3d.html"
        elif clean_path in ["/india-map", "/india-map/"]:
            path = "/india-map.html"
        elif "." not in clean_path and not clean_path.endswith("/"):
            potential_file = os.path.join(DIRECTORY, clean_path.lstrip("/") + ".html")
            if os.path.exists(potential_file):
                path = clean_path + ".html"

        return super().translate_path(path)

    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), VaxKavachHandler) as httpd:
        print(f"VaxKavach dev server running on http://localhost:{PORT} (root -> landing.html)", flush=True)
        httpd.serve_forever()
