#!/usr/bin/env python3
"""Fix server.py to add missing routes and refactor static file serving."""
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
with open(path, "r") as f:
    content = f.read()

# 1. Add root route and capabilities route before /static
old_static = 'elif parsed.path.startswith("/static/"):'
new_routes = '''elif parsed.path == "/":
            # Serve the dashboard UI
            self._serve_static("index.html", "text/html")
        elif parsed.path == "/capabilities":
            # Return available capabilities from the orchestrator
            orchestrator = _get_orchestrator()
            if orchestrator is None:
                self._set_json(503)
                self.wfile.write(json.dumps({"error": "No orchestrator available"}).encode())
                return
            # Get capabilities from the task classifier
            capabilities = orchestrator.task_classifier.get_all_capabilities()
            self._set_json(200)
            self.wfile.write(json.dumps({
                "capabilities": capabilities,
                "count": len(capabilities)
            }, indent=2).encode())
        elif parsed.path.startswith("/static/"):'''

content = content.replace(old_static, new_routes)

# 2. Refactor /static handler to use _serve_static
old_static_block = '''elif parsed.path.startswith("/static/"):
            # Serve static files
            filename = parsed.path[len("/static/"):]'''
new_static_block = '''elif parsed.path.startswith("/static/"):
            # Serve static files
            filename = parsed.path[len("/static/"):]
            self._serve_static(filename)'''

content = content.replace(old_static_block, new_static_block)

# 3. Remove the old inline static serving code (after filename assignment)
old_inline = '''            # Security: prevent directory traversal
            if ".." in filename or filename.startswith("/"):
                self.send_error(403, "Forbidden")
                return
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
            file_path = os.path.normpath(os.path.join(static_dir, filename))
            if not file_path.startswith(static_dir):
                self.send_error(403, "Forbidden")
                return
            if not os.path.isfile(file_path):
                self.send_error(404, "File not found")
                return
            self.send_response(200)
            # Basic content type detection
            if filename.endswith(".html"):
                self.send_header("Content-Type", "text/html")
            elif filename.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            elif filename.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            else:
                self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Not found")'''

new_end = '''        else:
            self.send_error(404, "Not found")'''

content = content.replace(old_inline, new_end)

# 4. Add _serve_static method before do_POST
old_do_post = '    def do_POST(self):'
new_method = '''    def _serve_static(self, filename, content_type=None):
        """Serve a static file from the static directory."""
        # Security: prevent directory traversal
        if ".." in filename or filename.startswith("/"):
            self.send_error(403, "Forbidden")
            return
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        file_path = os.path.normpath(os.path.join(static_dir, filename))
        if not file_path.startswith(static_dir):
            self.send_error(403, "Forbidden")
            return
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return
        self.send_response(200)
        # Basic content type detection
        if content_type:
            self.send_header("Content-Type", content_type)
        elif filename.endswith(".html"):
            self.send_header("Content-Type", "text/html")
        elif filename.endswith(".css"):
            self.send_header("Content-Type", "text/css")
        elif filename.endswith(".js"):
            self.send_header("Content-Type", "application/javascript")
        else:
            self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def do_POST(self):'''

content = content.replace(old_do_post, new_method)

with open(path, "w") as f:
    f.write(content)

print("server.py updated successfully")