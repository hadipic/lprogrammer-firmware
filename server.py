#!/usr/bin/env python3
"""
سرور پروکسی برای تست فرانت‌اند با ESP32 واقعی
همه درخواست‌ها را به ESP32 واقعی هدایت می‌کند
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import socket
import time
import os

# ============================================================
#  تنظیمات
# ============================================================

ESP32_IP = "192.168.1.17"  # آدرس IP واقعی ESP32
ESP32_PORT = 80
PROXY_PORT = 8081

# ============================================================
#  کلاس Proxy Handler
# ============================================================

class ProxyHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Address')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def forward_request(self, method, path, body=None, headers=None, is_binary=False):
        """هدایت درخواست به ESP32"""
        esp32_url = f"http://{ESP32_IP}:{ESP32_PORT}{path}"
        
        try:
            req = urllib.request.Request(esp32_url, method=method)
            
            # اضافه کردن هدرها
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            # اضافه کردن body (باینری یا متن)
            if body is not None:
                if is_binary:
                    req.data = body  # data قبلاً bytes است
                else:
                    req.data = body.encode('utf-8')
                req.add_header('Content-Type', 'application/octet-stream' if is_binary else 'application/json')
            
            # ارسال درخواست
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                # اگر response JSON است، آن را به str تبدیل کن
                try:
                    response_data = response_data.decode('utf-8')
                except UnicodeDecodeError:
                    response_data = response_data.hex()
                
                return {
                    'status': response.getcode(),
                    'headers': response.headers,
                    'data': response_data,
                    'is_binary': False
                }
                
        except urllib.error.URLError as e:
            error_msg = f'ESP32 not reachable: {str(e)}'
            return {
                'status': 502,
                'error': error_msg,
                'data': json.dumps({'status': 'error', 'message': error_msg}),
                'is_binary': False
            }
        except urllib.error.HTTPError as e:
            try:
                error_data = e.read().decode('utf-8')
            except:
                error_data = str(e)
            return {
                'status': e.code,
                'data': error_data,
                'is_binary': False
            }
        except Exception as e:
            return {
                'status': 500,
                'error': str(e),
                'data': json.dumps({'status': 'error', 'message': str(e)}),
                'is_binary': False
            }
    
    def do_GET(self):
        """پردازش درخواست‌های GET"""
        
        # ===== API های ESP32 =====
        if self.path.startswith('/api/'):
            print(f"📡 GET {self.path} -> ESP32")
            result = self.forward_request('GET', self.path)
            
            self.send_response(result.get('status', 200))
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            if 'error' in result:
                self.wfile.write(result['data'].encode('utf-8'))
            else:
                self.wfile.write(result['data'].encode('utf-8'))
            return
        
        # ===== فایل‌های استاتیک =====
        if self.path == '/':
            self.path = '/index.html'
        
        static_dir = os.path.join(os.path.dirname(__file__), 'frontend')
        file_path = os.path.join(static_dir, self.path.lstrip('/'))
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.send_cors_headers()
            
            if file_path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif file_path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif file_path.endswith('.html'):
                self.send_header('Content-Type', 'text/html')
            elif file_path.endswith('.json'):
                self.send_header('Content-Type', 'application/json')
            elif file_path.endswith('.png'):
                self.send_header('Content-Type', 'image/png')
            elif file_path.endswith('.ico'):
                self.send_header('Content-Type', 'image/x-icon')
            else:
                self.send_header('Content-Type', 'text/plain')
            
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'File not found')
    
    def do_POST(self):
        """پردازش درخواست‌های POST"""
        
        # ===== تشخیص نوع محتوا =====
        content_type = self.headers.get('Content-Type', '').lower()
        is_binary = 'application/octet-stream' in content_type
        
        # ===== خواندن body =====
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            body = self.rfile.read(content_length)
            # اگر باینری نبود، به str تبدیل کن
            if not is_binary:
                try:
                    body = body.decode('utf-8')
                except UnicodeDecodeError:
                    body = body.hex()
                    is_binary = True
        else:
            body = None
        
        # ===== API های ESP32 =====
        if self.path.startswith('/api/'):
            print(f"📡 POST {self.path} -> ESP32 (binary={is_binary}, size={content_length})")
            
            # گرفتن هدرها
            headers = {}
            for key, value in self.headers.items():
                if key.lower() in ['content-type', 'x-address']:
                    headers[key] = value
            
            result = self.forward_request('POST', self.path, body, headers, is_binary)
            
            self.send_response(result.get('status', 200))
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            if 'error' in result:
                self.wfile.write(result['data'].encode('utf-8'))
            else:
                self.wfile.write(result['data'].encode('utf-8'))
            return
        
        # ===== مسیر ناشناخته =====
        self.send_response(404)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(b'Unknown endpoint')
    
    def do_PUT(self):
        """پردازش درخواست‌های PUT (برای upload)"""
        
        # ===== تشخیص نوع محتوا =====
        content_type = self.headers.get('Content-Type', '').lower()
        is_binary = 'application/octet-stream' in content_type
        
        # ===== خواندن body =====
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        if self.path.startswith('/api/'):
            print(f"📡 PUT {self.path} -> ESP32 (binary={is_binary}, size={content_length})")
            
            headers = {}
            for key, value in self.headers.items():
                if key.lower() in ['content-type', 'x-address']:
                    headers[key] = value
            
            try:
                esp32_url = f"http://{ESP32_IP}:{ESP32_PORT}{self.path}"
                req = urllib.request.Request(esp32_url, method='PUT')
                
                for key, value in headers.items():
                    req.add_header(key, value)
                
                if body is not None:
                    req.data = body
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_data = response.read()
                    try:
                        response_data = response_data.decode('utf-8')
                    except:
                        response_data = response_data.hex()
                    
                    self.send_response(response.getcode())
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(response_data.encode('utf-8'))
                    
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
            return
        
        self.send_response(404)
        self.send_cors_headers()
        self.end_headers()

# ============================================================
#  اجرای سرور
# ============================================================

def main():
    # بررسی اتصال به ESP32
    try:
        socket.create_connection((ESP32_IP, ESP32_PORT), timeout=2)
        print(f"✅ ESP32 found at {ESP32_IP}:{ESP32_PORT}")
    except:
        print(f"⚠️  ESP32 not reachable at {ESP32_IP}:{ESP32_PORT}")
        print("   Make sure ESP32 is connected to the network")
    
    print("\n" + "="*60)
    print("🚀 Proxy Server for L-Programmer")
    print("="*60)
    print(f"📡 ESP32: http://{ESP32_IP}:{ESP32_PORT}")
    print(f"🌐 Proxy: http://localhost:{PROXY_PORT}")
    print()
    print("📋 API Endpoints (proxied to ESP32):")
    print("   GET  /api/status")
    print("   GET  /api/capabilities")
    print("   GET  /api/protocols")
    print("   POST /api/connect")
    print("   POST /api/disconnect")
    print("   POST /api/detect")
    print("   POST /api/read")
    print("   POST /api/program")
    print("   POST /api/erase")
    print("   POST /api/verify")
    print("   POST /api/vpp")
    print()
    print("📁 Static files: ./frontend/")
    print("="*60)
    print("Press Ctrl+C to stop")
    print()
    
    server = HTTPServer(("0.0.0.0", PROXY_PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == '__main__':
    main()