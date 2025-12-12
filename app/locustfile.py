from locust import HttpUser, task, between
import re
import random

class SistemaUser(HttpUser):
    wait_time = between(1, 3)

    usuarios = [
        {"numero_documento": "10000002", "contraseña": "12345", "rol": 3},
    ]

    #
    # ----------- UTILIDADES -----------
    #

    def get_csrf_token(self, url="/login/"):
        """Obtiene token CSRF desde cookie o HTML."""
        response = self.client.get(url, allow_redirects=True)

        if "csrftoken" in response.cookies:
            return response.cookies["csrftoken"]

        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
        if match:
            return match.group(1)

        return None

    def login(self):
        """Autenticación del usuario administrador."""
        if hasattr(self, "logged_in") and self.logged_in:
            return

        user = random.choice(self.usuarios)
        csrf_token = self.get_csrf_token()

        headers = {"X-CSRFToken": csrf_token}

        response = self.client.post(
            "/login/",
            data={
                "numero_documento": user["numero_documento"],
                "contraseña": user["contraseña"],
                "csrfmiddlewaretoken": csrf_token
            },
            headers=headers,
            allow_redirects=True
        )

        if response.status_code in (200, 302):
            self.logged_in = True
        else:
            print("❌ Error en login:", response.status_code, response.text)

    #
    # ---------- TAREAS SOBRE SORTEOS ----------
    #

    @task(2)
    def crear_sorteo(self):
        """CREAR un sorteo automáticamente."""
        self.login()

        csrf = self.get_csrf_token("/administrador/sorteos/")

        data = {
            "nombre": f"Sorteo Locust {random.randint(1, 999)}",
            "descripcion": "Sorteo generado por Locust",
            "fecha_inicio": "2025-01-20",
            "crear_sorteo": "1",
            "csrfmiddlewaretoken": csrf
        }

        headers = {"X-CSRFToken": csrf}

        self.client.post(
            "/administrador/sorteos/",
            data=data,
            headers=headers,
            name="crear_sorteo",
            allow_redirects=True
        )

    @task(3)
    def ejecutar_sorteo(self):
        """
        Selecciona un sorteo aleatorio y ejecuta el sorteo de vehículos.
        """
        self.login()

        # 1️⃣ obtener la lista de sorteos
        lista = self.client.get("/administrador/sorteos/", name="listar_sorteos")
        ids = re.findall(r'data-id="(\d+)"', lista.text)

        if not ids:
            return  # no hay sorteos creados

        sorteo_id = random.choice(ids)

        # 2️⃣ obtener token CSRF para la vista del sorteo
        csrf = self.get_csrf_token(f"/administrador/sorteo/{sorteo_id}/vehiculos/")

        data = {
            "realizar_sorteo": "1",
            "csrfmiddlewaretoken": csrf
        }

        headers = {"X-CSRFToken": csrf}

        # 3️⃣ POST para ejecutar el sorteo
        self.client.post(
            f"/administrador/sorteo/{sorteo_id}/vehiculos/",
            data=data,
            headers=headers,
            name="ejecutar_sorteo",
            allow_redirects=True
        )
