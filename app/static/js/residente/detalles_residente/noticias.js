const noticiasContainer = document.getElementById("noticias-container");

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${protocol}://${window.location.host}/ws/noticias/`);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    noticiasContainer.innerHTML = "";

    data.noticias.forEach(noticia => {
        const div = document.createElement("div");
        div.innerHTML = `<h3>${noticia.titulo}</h3>
                         <p>${noticia.descripcion}</p>
                         <small>${noticia.fecha_publicacion}</small>`;
        noticiasContainer.appendChild(div);
    });
};

socket.onclose = function(e) {
    console.error("Socket cerrado inesperadamente.");
};

setTimeout(() => {
    document.querySelectorAll('.alert-modern').forEach(el => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    });
}, 4000);

// Sidebar Responsive
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const mainContent = document.getElementById('mainContent');

function toggleSidebar() {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

toggleBtn.addEventListener('click', toggleSidebar);
overlay.addEventListener('click', toggleSidebar);

// Cerrar sidebar con tecla Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && sidebar.classList.contains('active')) {
        toggleSidebar();
    }
});

// Manejo responsive automático
function handleResize() {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
}

window.addEventListener('resize', handleResize);
