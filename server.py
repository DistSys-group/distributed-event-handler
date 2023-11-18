import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer


class LocalData(object):
    likes = 0


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if re.search('/api/post/*', self.path):
            length = int(self.headers.get('content-length'))
            data = self.rfile.read(length).decode('utf8')
            jsondata = json.loads(data)

            LocalData.likes = LocalData.likes + jsondata["likes"];

            logging.info("added %s likes", data)            
            self.send_response(200)
        else:
            self.send_response(403)
        self.end_headers()

    def do_GET(self):
        if re.search('/api/get/*', self.path):
            endpoint = self.path.split('/')[-1]
            if endpoint == 'likes':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
		
                jsondata = {'likes': LocalData.likes}
                data = json.dumps(jsondata).encode('utf-8')
                logging.info("Total likes: %s", data);
                self.wfile.write(data)

            else:
                self.send_response(404, 'Not Found: endpoint does not exist')
        else:
            self.send_response(403)
        self.end_headers()

        
if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), HTTPRequestHandler)
    logging.info('Starting httpd...\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info('Stopping httpd...\n')
