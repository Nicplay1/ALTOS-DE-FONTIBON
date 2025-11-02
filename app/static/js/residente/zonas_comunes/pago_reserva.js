document.addEventListener('DOMContentLoaded', function () {
    // =========================
    // Elementos principales
    // =========================
    const toggleBtn = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const modalOverlay = document.getElementById('overlay');
    const editarModalEl = document.getElementById('editarPagoModal');

    // =========================
    // Sidebar
    // =========================
    function toggleSidebar() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }

    if (toggleBtn && overlay) {
        toggleBtn.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);
    }

    // Cerrar sidebar con tecla Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });

    // Ajuste automático en pantallas grandes
    function handleResize() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }
    window.addEventListener('resize', handleResize);

    // =========================
    // Control del overlay de modales
    // =========================
    function showModalOverlay() {
        modalOverlay.classList.add('active');
    }

    function hideModalOverlay() {
        modalOverlay.classList.remove('active');
    }

    function closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) modalInstance.hide();
        });
        hideModalOverlay();
    }

    // Configurar overlays en todos los modales (excepto editar)
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (modal.id !== 'editarPagoModal') {
            modal.addEventListener('show.bs.modal', showModalOverlay);
            modal.addEventListener('hidden.bs.modal', hideModalOverlay);
        }
    });

    // Cerrar modales con tecla Escape (excepto edición)
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const editarModal = document.getElementById('editarPagoModal');
            if (!editarModal || !editarModal.classList.contains('show')) {
                closeAllModals();
            }
        }
    });

    // =========================
    // Auto-ocultar alertas
    // =========================
    setTimeout(() => {
        document.querySelectorAll('.alert-modern').forEach(el => {
            el.classList.remove('show');
            setTimeout(() => el.remove(), 300);
        });
    }, 4000);

    // =========================
    // Modal de edición de pago
    // =========================
    if (editarModalEl) {
        // Activar overlay de desenfoque suave
        modalOverlay.classList.add('active');

        // Mostrar el modal con configuración estática
        const editarModal = new bootstrap.Modal(editarModalEl, {
            backdrop: 'static',
            keyboard: false
        });
        editarModal.show();

        // Al cerrarse, quitar overlay y redirigir
        editarModalEl.addEventListener('hidden.bs.modal', function () {
            modalOverlay.classList.remove('active');
            window.location.href = editarModalEl.getAttribute('data-redirect-url');
        });
    }
});

// Función global para cerrar todos los modales
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) modalInstance.hide();
    });
    
    const modalOverlay = document.getElementById('overlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
    }
}