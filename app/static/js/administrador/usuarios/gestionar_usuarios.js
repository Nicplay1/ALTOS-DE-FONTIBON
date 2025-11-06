// static/js/administrador/usuarios/gestionar_usuarios.js
(function () {

    // ---- ELEMENTOS PRINCIPALES ----
    const resultadosDiv = document.getElementById("resultados-usuarios");
    const searchInput = document.querySelector(".search-input");
    const notificaciones = document.getElementById("notificaciones");
    const userCountEl = document.getElementById("userCount");

    // Modal
    const confirmationModal = document.getElementById('confirmationModal');
    const userNameModal = document.getElementById('userNameModal');
    const roleNameModal = document.getElementById('roleNameModal');
    const cancelChangeBtn = document.getElementById('cancelChange');
    const confirmChangeBtn = document.getElementById('confirmChange');
    const loadingIndicator = document.getElementById('loadingIndicator');
    let currentForm = null;

    // URL gestion
    const gestionarUsuariosUrl = document.body.dataset.gestionarUsuariosUrl;

    // ---- FUNCIONES ÚTILES ----
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // ---- WEBSOCKET ----
    const loc = window.location;
    const wsScheme = (loc.protocol === "https:") ? "wss" : "ws";
    const wsUrl = wsScheme + "://" + loc.host + "/ws/usuarios/";
    let socket = null;

    function conectarWS() {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => console.log("✅ WebSocket de usuarios conectado");

        socket.onmessage = function (event) {
            try {
                const data = JSON.parse(event.data);

                if (data.html && resultadosDiv) {
                    resultadosDiv.innerHTML = data.html;
                    bindRoleForms();
                }

                if (data.count !== null && userCountEl) {
                    userCountEl.innerHTML = `<i class="fas fa-users"></i> Total: ${data.count} usuarios`;
                }

                if (data.mensaje) showNotification(data.mensaje);

            } catch (err) {
                console.error("Error parseando mensaje WS:", err);
            }
        };

        socket.onclose = e => {
            console.warn("❌ WebSocket cerrado — reconectando en 3s", e.reason);
            setTimeout(conectarWS, 3000);
        };
        socket.onerror = err => socket.close();
    }

    // ---- NOTIFICACIONES ----
    function showNotification(text) {
        if (!notificaciones) return;

        const div = document.createElement("div");
        div.className = "alert-modern alert-success";
        div.innerHTML = `
            <i class="fas fa-check-circle"></i> ${text}
        `;
        notificaciones.appendChild(div);

        setTimeout(() => {
            div.classList.remove('show');
            setTimeout(() => div.remove(), 300);
        }, 4000);
    }

    // ---- FORMULARIOS CAMBIO ROL ----
    function bindRoleForms() {
        document.querySelectorAll(".role-form").forEach(form => {
            const changeBtn = form.querySelector(".change-role-btn");
            if (!changeBtn || changeBtn.dataset.bound) return;
            changeBtn.dataset.bound = "true";

            changeBtn.addEventListener("click", function () {
                const userName = form.getAttribute('data-user-name');
                const roleSelect = form.querySelector('select[name="id_rol"]');
                const roleName = roleSelect.options[roleSelect.selectedIndex].textContent;

                userNameModal.textContent = userName;
                roleNameModal.textContent = roleName;

                currentForm = form;
                confirmationModal.classList.add('active');
            });
        });
    }

    // Confirmar en modal
    confirmChangeBtn.addEventListener("click", function () {
        if (!currentForm) return;

        const formData = new FormData(currentForm);
        loadingIndicator.classList.add('active');

        fetch(gestionarUsuariosUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            resultadosDiv.innerHTML = data.html;
            confirmationModal.classList.remove('active');
            loadingIndicator.classList.remove('active');

            bindRoleForms();
            if (data.mensaje) showNotification(data.mensaje);

        })
        .catch(() => {
            loadingIndicator.classList.remove('active');
            alert("Error al cambiar el rol.");
        });

        currentForm = null;
    });
    cancelChangeBtn.addEventListener("click", function () {
        confirmationModal.classList.remove('active');
        currentForm = null;
    });

    // ---- BÚSQUEDA AJAX ----
    searchInput.addEventListener("keyup", function () {
        const query = searchInput.value;

        fetch(`${gestionarUsuariosUrl}?q=${encodeURIComponent(query)}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(r => r.json())
        .then(data => {
            resultadosDiv.innerHTML = data.html;
            bindRoleForms();
        });
    });

    // ---- SIDEBAR ----
    const toggleBtn = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function toggleSidebar() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }

    toggleBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    window.addEventListener('keydown', e => {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });

    // ---- INICIALIZACIÓN ----
    bindRoleForms();
    conectarWS();

})();
