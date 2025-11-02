// ==== Alertas automáticas ====
setTimeout(() => {
    document.querySelectorAll('.alert-modern').forEach(el => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    });
}, 4000);

// ==== Sidebar ====
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

function toggleSidebar() {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

toggleBtn.addEventListener('click', toggleSidebar);
overlay.addEventListener('click', toggleSidebar);

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && sidebar.classList.contains('active')) toggleSidebar();
});

window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
});

// ==== Modal de Novedades ====
function mostrarFormulario(tipo) {
    document.getElementById('overlay').classList.add('show');
    document.getElementById('modal-form').classList.add('show');

    document.getElementById('tipo_novedad_input').value = tipo;
    document.getElementById('paquete_fields').style.display = tipo === 'paquete' ? 'block' : 'none';
    document.getElementById('visitante_fields').style.display = tipo === 'visitante' ? 'block' : 'none';
    document.getElementById('modal-title').innerHTML =
        '<i class="fas fa-exclamation-circle"></i> ' +
        (tipo === 'paquete' ? 'Registrar Daño de Paquete' : 'Registrar Daño de Vehículo');

    actualizarDescripcionPaquete();
}

function cerrarFormulario() {
    document.getElementById('overlay').classList.remove('show');
    document.getElementById('modal-form').classList.remove('show');
}

function actualizarDescripcionPaquete() {
    const select = document.getElementById('id_paquete');
    if (select) {
        const descripcion = select.options[select.selectedIndex]?.getAttribute('data-descripcion') || 'Sin descripción';
        document.getElementById('descripcion_paquete').innerText = descripcion;
    }
}

document.getElementById('id_paquete')?.addEventListener('change', actualizarDescripcionPaquete);

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.getElementById('overlay').classList.contains('show')) {
        cerrarFormulario();
    }
});
