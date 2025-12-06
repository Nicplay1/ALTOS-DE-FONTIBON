// Función para mostrar alerta
function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
        <span>${message}</span>
    `;
    alertContainer.appendChild(alertDiv);
    
    // Auto-eliminar alerta después de 3 segundos
    setTimeout(() => {
        alertDiv.style.animation = 'fadeOut 0.5s ease-in forwards';
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 500);
    }, 3000);
}

// Efecto de zoom en el logo
document.addEventListener('DOMContentLoaded', function() {
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });

        logo.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }
});