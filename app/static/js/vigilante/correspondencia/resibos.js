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
function showModalOverlay() {
    modalOverlay.style.display = 'block';
}

function hideModalOverlay() {
    modalOverlay.style.display = 'none';
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    hideModalOverlay();
}

document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', showModalOverlay);
        modal.addEventListener('hidden.bs.modal', hideModalOverlay);
    });

    // Cerrar modales con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
});

// =========================
// Funcionalidad Ajax (Código 2)
// =========================
$(document).ready(function () {

    // Limpiar modal al cerrarlo
    $("#entregaModal").on("hidden.bs.modal", function () {
        $("#registros-container").html("");
        $("#form-filtrar")[0].reset();
    });

    // Filtrar registros
    $("#form-filtrar").submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: URL_REGISTRAR_ENTREGA, // ✅ Usa la variable global
            data: $(this).serialize(),
            headers: { "X-Requested-With": "XMLHttpRequest" },
            success: function (response) {
                $("#registros-container").html(response.html);
            },
        });
    });

    // Registrar entrega desde tabla
    $(document).on("click", ".btn-entregar", function () {
        var id_corres = $(this).data("idcorres");
        var id_res = $(this).data("idres");

        $.ajax({
            type: "POST",
            url: URL_REGISTRAR_ENTREGA, // ✅ Usa la variable global
            data: {
                accion: "registrar_entrega",
                id_correspondencia: id_corres,
                id_residente: id_res,
                csrfmiddlewaretoken: CSRF_TOKEN, // ✅ Token global
            },
            success: function (response) {
                if (response.success) {
                    var toast = `
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            Entrega registrada correctamente
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>`;
                    $("#alert-container").append(toast);
                    $("#form-filtrar").submit(); // refresca tabla
                }
            },
        });
    });
});
