import http.server
import socketserver
import json
import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            img_b64 = data.get('image', '')
            img_bytes = base64.b64decode(img_b64)
            
            res = ocr.classification(img_bytes)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"text": res}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

PORT = 8080
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"🚀 ddddocr Server đang chạy tại http://0.0.0.0:{PORT}")
    httpd.serve_forever()
