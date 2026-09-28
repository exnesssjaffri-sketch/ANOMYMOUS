#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Start the server in a separate thread
class TestServerHandler(BaseHTTPRequestHandler):
    def handle(self):
        request = self.request
        path = request.getpreferredencodings()[0] + request.path
        print(f"Request: {path}")
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        elif path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "accepted", "execution": {}}')
        elif path.startswith('/static/'):
            static_path = os.path.normpath(os.path.join(os.getcwd(), 'static', path[7:]))
            if not static_path.endswith(os.path.join(os.getcwd(), 'static')):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden: Traversal attempt detected')
            elif not os.path.exists(static_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                with open(static_path, 'rb') as f:
                    self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

def run_test_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, TestServerHandler)
    print('Testing server running on port 8000...')
    httpd.serve_forever()

def test_endpoints():
    # Test /health endpoint
    health_url = 'http://127.0.0.1:8000/health'
    try:
        health_response = urllib.request.urlopen(health_url)
        health_data = json.loads(health_response.read().decode())
        print(f'Health endpoint: {health_data}')
    except Exception as e:
        print(f'Health endpoint error: {e}')
    
    # Test /status endpoint
    status_url = 'http://127.0.0.1:8000/status'
    try:
        status_response = urllib.request.urlopen(status_url)
        status_data = json.loads(status_response.read().decode())
        print(f'Status endpoint: {status_data}')
    except Exception as e:
        print(f'Status endpoint error: {e}')
    
    # Test static file serving
    static_url = 'http://127.0.0.1:8000/static/index.html'
    try:
        static_response = urllib.request.urlopen(static_url)
        static_data = static_response.read().decode()
        print(f'Static file response: {static_data[:200]}...')
    except Exception as e:
        print(f'Static file error: {e}')
    
    # Test traversal attempt
    traversal_url = 'http://127.0.0.1:8000/static/../server.py'
    try:
        traversal_response = urllib.request.urlopen(traversal_url)
        traversal_data = traversal_response.read().decode()
        print(f'Traversal attempt response: {traversal_data}')
    except Exception as e:
        print(f'Traversal attempt error: {e}')

if __name__ == '__main__':
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_test_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Run tests
    test_endpoints()
    
    # Cleanup
    server_thread.join(timeout=5)
    print('Testing completed.')