import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

# Datos del servidor de autorización
TOKEN_URL = os.getenv("TOKEN")
API_URL =os.getenv("API")

# Credenciales de la aplicación cliente (copia desde el admin de Django)
CLIENT_ID = os.getenv("ID")
CLIENT_SECRET = os.getenv("SECRET")

# Credenciales del usuario
USERNAME = os.getenv("USER") # Usuario Django
PASSWORD = os.getenv("PASS")

# Obtener un token de acceso
data = {
    "grant_type": "password",
    "username": USERNAME,
    "password": PASSWORD,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

response = requests.post(TOKEN_URL, data=data)
token_info = response.json()

if "access_token" in token_info:
    access_token = token_info["access_token"]
    print(f"✅ Token obtenido: {access_token}")

    # Hacer una petición a la API protegida
    headers = {"Authorization": f"Bearer {access_token}"}
    api_response = requests.get(API_URL, headers=headers)

    print("🔹 Respuesta de la API:", api_response.json())
else:
    print("❌ Error al obtener el token:", token_info)
