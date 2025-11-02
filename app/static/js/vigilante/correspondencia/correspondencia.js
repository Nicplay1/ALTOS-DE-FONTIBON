// correspondencia.js - TODO el JavaScript en un archivo

// =========================
// Alertas automáticas
// =========================
setTimeout(() => {
    document.querySelectorAll('.alert-modern').forEach(el => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    });
}, 4000);

// =========================
// Toggle Sidebar
// =========================
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const modalOverlay = document.getElementById('overlay');

function toggleSidebar() {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

if (toggleBtn && overlay) {
    toggleBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);
}

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

// =========================
// Control del overlay para modales
// =========================
let openModals = 0;

function showModalOverlay() {
    openModals++;
    if (modalOverlay) modalOverlay.style.display = 'block';
}

function hideModalOverlay() {
    openModals--;
    if (openModals <= 0 && modalOverlay) {
        modalOverlay.style.display = 'none';
        openModals = 0;
    }
}

function closeAllModals() {
    // Cerrar todos los modales de Bootstrap
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    hideModalOverlay();
}

// =========================
// Búsqueda de Paquetes
// =========================
function inicializarBusqueda() {
    const btnBuscar = document.getElementById("btnBuscarPaquete");
    const resultadosDiv = document.getElementById("resultadosBusqueda");
    const tablaResultados = document.getElementById("tablaResultadosBusqueda");

    if (btnBuscar) {
        btnBuscar.addEventListener("click", async () => {
            const apartamento = document.getElementById("busquedaApartamento").value;
            const torre = document.getElementById("busquedaTorre").value;

            // URL ABSOLUTA - funciona en archivo .js separado
           const url = `${window.DJANGO_URLS.buscarPaquete}?apartamento=${apartamento}&torre=${torre}`;
            try {
                const response = await fetch(url);
                const data = await response.json();

                // Limpiar tabla antes de agregar resultados
                if (tablaResultados) tablaResultados.innerHTML = "";

                if (data.resultados && data.resultados.length > 0) {
                    data.resultados.forEach(p => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${p.apartamento || apartamento || 'Todos'}</td>
                            <td>${p.torre || torre || 'Todas'}</td>
                            <td>${p.fecha_recepcion}</td>
                            <td>${p.vigilante_recepcion}</td>
                            <td>
                                <button class="btn-modern"
                                        data-bs-toggle="modal"
                                        data-bs-target="#modalEntregaPaquetes"
                                        data-id="${p.id}">
                                    Registrar entrega
                                </button>
                            </td>
                        `;
                        if (tablaResultados) tablaResultados.appendChild(row);
                    });
                    if (resultadosDiv) resultadosDiv.style.display = "block";
                } else {
                    if (tablaResultados) {
                        tablaResultados.innerHTML = `<tr><td colspan="5" class="text-center">No se encontraron paquetes</td></tr>`;
                    }
                    if (resultadosDiv) resultadosDiv.style.display = "block";
                }
            } catch (error) {
                console.error('Error al buscar paquetes:', error);
                if (tablaResultados) {
                    tablaResultados.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al buscar paquetes</td></tr>`;
                }
                if (resultadosDiv) resultadosDiv.style.display = "block";
            }
        });
    }
}

// =========================
// Modal de Entrega
// =========================
function inicializarModalEntrega() {
    const entregaModal = document.getElementById('modalEntregaPaquetes');
    if (entregaModal) {
        entregaModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const paqueteId = button.getAttribute('data-id');
            // Buscar el campo oculto del formulario de entrega
            const idPaqueteField = document.querySelector('input[name="id_paquete"]');
            if (idPaqueteField) {
                idPaqueteField.value = paqueteId;
            }
        });
    }
}

// =========================
// Inicialización General
// =========================
document.addEventListener('DOMContentLoaded', function() {
    // Configurar eventos para todos los modales
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            showModalOverlay();
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            hideModalOverlay();
        });
    });

    // Cerrar modales con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // Inicializar funcionalidades
    inicializarBusqueda();
    inicializarModalEntrega();

    console.log('✅ JavaScript de correspondencia cargado correctamente');
});