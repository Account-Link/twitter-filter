from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TELEPORT_AUTH = os.getenv('TELEPORT_AUTH')
TWITTER_AUTH = os.getenv('TWITTER_AUTH')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy.log'),
        logging.StreamHandler()
    ]
)

class ProxyHandler(BaseHTTPRequestHandler):
    def forward_request(self, method):
        url = f"https://api.twitter.com{self.path}"
        headers = dict(self.headers)
        
        # Replace auth_token cookie
        if 'cookie' in headers:
            cookies = {c.split('=')[0].strip(): c.split('=', 1)[1].strip() 
                      for c in headers['cookie'].split(';')}
            if 'auth_token' in cookies:
                # Verify the provided auth token matches TELEPORT_AUTH
                if cookies['auth_token'] != TELEPORT_AUTH:
                    self.send_error(403, "Invalid auth_token")
                    return
                cookies['auth_token'] = TWITTER_AUTH
            headers['cookie'] = '; '.join(f'{k}={v}' for k, v in cookies.items())
        
        # Read body for POST requests
        body = None
        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
        
        try:
            # Forward the request to Twitter API
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                allow_redirects=False
            )
            
            # Log the proxied request
            logging.info(f"{method} {url}")
            logging.info(f"Request Headers: {headers}")
            if body:
                logging.info(f"Request Body: {body.decode()}")
            logging.info(f"Response Status: {response.status_code}")
            logging.info(f"Response Headers: {response.headers}")
            
            # Forward the response back to client
            self.send_response(response.status_code)
            
            # Get the content first so we can set accurate headers
            content = response.content
            
            # Forward response headers, excluding ones we'll set ourselves
            skip_headers = {'content-encoding', 'transfer-encoding', 'content-length'}
            for header, value in response.headers.items():
                if header.lower() not in skip_headers:
                    self.send_header(header, value)
            
            # Set our own content length
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            
            # Send the decompressed content
            self.wfile.write(content)
            
        except Exception as e:
            logging.error(f"Error forwarding request: {str(e)}")
            self.send_error(502, f"Error forwarding request: {str(e)}")
    
    def do_GET(self):
        self.forward_request('GET')
    
    def do_POST(self):
        self.forward_request('POST')

def run_server():
    server_address = ('', 443)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    # Setup SSL/TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('api.twitter.com.crt', 'key.pem')
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print("Starting HTTPS proxy server on port 443...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 
