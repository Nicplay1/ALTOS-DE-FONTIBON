from locust import HttpUser, task, between
import re
import random

class LoginUser(HttpUser):
    wait_time = between(1, 3)

    # Usuarios de prueba (reemplaza con tus datos reales)
    usuarios = [
        {"numero_documento": "10000001", "contraseña": "12345", "rol": 2},  # Residente
        {"numero_documento": "10000002", "contraseña": "12345", "rol": 3},  # Administrador
        {"numero_documento": "10000003", "contraseña": "12345", "rol": 4},  # Vigilante
    ]

    def get_csrf_token(self):
        """
        Obtiene el token CSRF desde la cookie o desde el HTML de /login/
        """
        response = self.client.get("/login/", allow_redirects=True)
        # Buscar csrftoken en cookies
        if 'csrftoken' in response.cookies:
            return response.cookies['csrftoken']
        # Buscar en HTML
        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
        if match:
            return match.group(1)
        return None

    @task(3)
    def login_correcto(self):
        """Simula login correcto con un usuario aleatorio"""
        user = random.choice(self.usuarios)
        csrf_token = self.get_csrf_token()
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf_token
        }
        response = self.client.post("/login/", data={
            "numero_documento": user["numero_documento"],
            "contraseña": user["contraseña"],
            "csrfmiddlewaretoken": csrf_token
        }, headers=headers)
        if response.status_code == 200:
            json_resp = response.json()
            if not json_resp.get("success"):
                print("Login correcto falló:", json_resp)

    @task(2)
    def login_incorrecto(self):
        """Simula login con datos incorrectos"""
        csrf_token = self.get_csrf_token()
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf_token
        }
        response = self.client.post("/login/", data={
            "numero_documento": "99999999",
            "contraseña": "wrongpass",
            "csrfmiddlewaretoken": csrf_token
        }, headers=headers)
        if response.status_code == 200:
            json_resp = response.json()
            if json_resp.get("success"):
                print("Login incorrecto pasó!")

    @task(1)
    def login_bloqueado(self):
        """Simula bloqueo por 5 intentos fallidos"""
        csrf_token = self.get_csrf_token()
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf_token
        }
        for _ in range(6):  # 6 intentos para activar bloqueo
            self.client.post("/login/", data={
                "numero_documento": "99999999",
                "contraseña": "wrongpass",
                "csrfmiddlewaretoken": csrf_token
            }, headers=headers)
