from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "ok",
            "model": "llama-3.3-70b-versatile",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
