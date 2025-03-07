import requests
import webbrowser
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

# Configuración del cliente (reemplaza con tus valores reales)
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:3000/callback"
# URL de autorización: se solicita los scopes openid, profile y email
AUTHORIZATION_URL = (
    f"http://127.0.0.1:8000/o/authorize/?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
    f"&scope=openid%20profile%20email"
)
TOKEN_URL = "http://127.0.0.1:8000/o/token/"
PROTECTED_URL = "http://127.0.0.1:8000/api/protected/"
USERINFO_URL = "http://127.0.0.1:8000/o/userinfo/"

# Variable global para almacenar el código de autorización
authorization_code = None

# Definimos un handler simple para capturar la respuesta en el callback
class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/callback":
            params = parse_qs(parsed_path.query)
            code = params.get("code", [None])[0]
            if code:
                authorization_code = code
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h2>Authorization code received. You can close this window.</h2></body></html>")
            else:
                self.send_error(400, "Missing code parameter.")
        else:
            self.send_error(404)

def run_callback_server():
    with socketserver.TCPServer(("", 3000), CallbackHandler) as httpd:
        # Solo esperamos una única petición (la del callback)
        httpd.handle_request()

if __name__ == "__main__":
    # Inicia el servidor en un hilo para capturar el callback
    server_thread = threading.Thread(target=run_callback_server, daemon=True)
    server_thread.start()

    print("Abriendo navegador para autorización...")
    webbrowser.open(AUTHORIZATION_URL)

    # Esperamos a que se reciba el código de autorización
    server_thread.join(timeout=300)  # espera hasta 5 minutos
    if authorization_code is None:
        print("No se recibió el código de autorización.")
        exit(1)
    print("Authorization code recibido:", authorization_code)

    # Intercambia el código por el token
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": "ZUyzuZGidkI72vU3akgHlZESuOzQKMQy6QmDT0E6",
        "client_secret": "9CeSpFwtl25LsOCHmCiPsW1VGrFbzj6HNBrjPydYeyHUJ5Kx4kmz9UehB9lmdDHt2nJuHW85vXFN1BbCoCQfCdK0ZMkyRIgBVY3C0NJxoDawZfxE9PREDLV0VGG40oi8",
        "redirect_uri": REDIRECT_URI,
    }
   
    token_response = requests.post(TOKEN_URL, data=data)
    print("Status code:", token_response.status_code)
    print("Response text:", token_response.text)

    token_info = token_response.json()
    print("Token info:", token_info)

    if "access_token" not in token_info:
        print("Error al obtener el token.")
        exit(1)

    access_token = token_info["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Llama al endpoint protegido
    api_response = requests.get(PROTECTED_URL, headers=headers)
    print("Respuesta API Protegida:", api_response.json())

    # Llama al endpoint de información del usuario (UserInfo)
    userinfo_response = requests.get(USERINFO_URL, headers=headers)
    print("User Info:", userinfo_response.json())
