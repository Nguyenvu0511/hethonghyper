import http.server
import socketserver
import json
import base64
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    import ddddocr
    ocr = ddddocr.DdddOcr(show_ad=False)
except ImportError:
    logging.error("ddddocr chua duoc cai dat. Vui long chay: pip install ddddocr")
    ocr = None

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
            
            if ocr:
                res = ocr.classification(img_bytes)
            else:
                res = ""
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"text": res}).encode('utf-8'))
            logging.info(f"Da giai ma: {res}")
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            logging.error(f"Loi giai ma: {e}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    PORT = 8080
    with ThreadedHTTPServer(("0.0.0.0", PORT), MyHandler) as httpd:
        logging.info(f"🚀 ddddocr Private API Server dang chay tai http://0.0.0.0:{PORT}")
        httpd.serve_forever()
