// residente/detalles_residente/noticias.js

const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/noticias/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    document.getElementById('noticiasContainer').innerHTML = data.html;
};

socket.onclose = function(e) {
    console.error('WebSocket cerrado inesperadamente');
};



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
