// Función para mostrar/ocultar contraseña
function setupPasswordToggle(toggleId, passwordId) {
    const toggle = document.getElementById(toggleId);
    const passwordInput = document.getElementById(passwordId);
    
    toggle.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Cambiar icono
        const icon = this.querySelector('i');
        if (type === 'password') {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        } else {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    });
}

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
document.querySelector('.logo').addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1)';
});

document.querySelector('.logo').addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
});

// Validación en tiempo real de requisitos de contraseña
document.getElementById('nueva_contraseña').addEventListener('input', function() {
    const password = this.value;
    const errorElement = document.getElementById('nueva-error');
    
    // Limpiar error anterior
    errorElement.innerHTML = '';
    
    // Validar longitud
    if (password.length > 0 && password.length < 6) {
        errorElement.innerHTML = '<i class="fas fa-exclamation-circle"></i> La contraseña debe tener al menos 6 caracteres';
        return;
    }
    
    // Validar mayúscula
    if (password.length >= 6 && !/(?=.*[A-Z])/.test(password)) {
        errorElement.innerHTML = '<i class="fas fa-exclamation-circle"></i> La contraseña debe contener al menos una letra mayúscula';
        return;
    }
});

// Validación de coincidencia de contraseñas
document.getElementById('confirmar_contraseña').addEventListener('input', function() {
    const confirmPassword = this.value;
    const password = document.getElementById('nueva_contraseña').value;
    const errorElement = document.getElementById('confirmar-error');
    
    // Limpiar error anterior
    errorElement.innerHTML = '';
    
    // Validar coincidencia
    if (confirmPassword && password !== confirmPassword) {
        errorElement.innerHTML = '<i class="fas fa-exclamation-circle"></i> Las contraseñas no coinciden';
    }
});

// Configurar toggles para ambas contraseñas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupPasswordToggle('togglePassword1', 'nueva_contraseña');
    setupPasswordToggle('togglePassword2', 'confirmar_contraseña');
});