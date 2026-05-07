from tls import create_ssl_context, get_cert_and_key

import cv2
import numpy as np
import state
from http.server import BaseHTTPRequestHandler, HTTPServer

cert_path, key_path, ca_file = get_cert_and_key()
ssl_context = create_ssl_context(cert_path, key_path, ca_file)


class StreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != "/video":
            self.send_error(404)
            return

        print("Client connected")

        # Check TLS client cert
        ssl_object = self.connection.getpeercert()

        if not ssl_object:
            print("No client cert")
            self.send_error(403)
            return

        cn = None
        for item in ssl_object.get("subject", []):
            for k, v in item:
                if k == "commonName":
                    cn = v

        if cn != state.CLIENT_ID:
            print("Unauthorized CN:", cn)
            self.send_error(403)
            return

        print("Client authorized:", cn)

        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        try:
            while True:
                result = self.server.camera.read()

                if not result:
                    continue

                success, frame, _ = result
                if not success:
                    continue

                frame = np.array(frame, dtype=np.uint8)

                _, jpg = cv2.imencode(
                    ".jpg",
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 40]
                )

                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                self.wfile.write(jpg.tobytes())
                self.wfile.write(b"\r\n")

        except Exception as e:
            print("Client disconnected:", e)

def start_http(camera):
    server = HTTPServer(("0.0.0.0", 8765), StreamHandler)
    server.camera = camera

    server.socket = ssl_context.wrap_socket(
        server.socket,
        server_side=True
    )

    print("HTTPS MJPEG server running")
    server.serve_forever()


