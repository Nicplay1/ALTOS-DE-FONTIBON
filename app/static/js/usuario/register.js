// Función para mostrar/ocultar contraseña
document.getElementById('togglePassword1').addEventListener('click', function() {
    const passwordInput = document.getElementById('contraseña');
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

document.getElementById('togglePassword2').addEventListener('click', function() {
    const passwordInput = document.getElementById('confirmar_contraseña');
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

// Función para limpiar errores
function clearErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.innerHTML = '';
    });
}

// Función para mostrar errores de campo
function showFieldError(field, message) {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
        errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    }
}

// Manejo del envío del formulario con AJAX
document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Limpiar errores anteriores
    clearErrors();
    
    // Obtener datos del formulario
    const formData = new FormData(this);
    
    // Enviar solicitud AJAX
    fetch(registerUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito y redirigir
            showAlert(data.messages[0], 'success');
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 2000);
        } else {
            // Mostrar errores de campo
            if (data.field_errors) {
                for (const field in data.field_errors) {
                    showFieldError(field, data.field_errors[field]);
                }
            }
            
            // Mostrar alertas
            if (data.messages) {
                data.messages.forEach(message => {
                    showAlert(message, 'error');
                });
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de conexión. Intente nuevamente.', 'error');
    });
});

// Efecto de zoom en el logo
document.querySelector('.logo').addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.1)';
});

document.querySelector('.logo').addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1)';
});

// Manejo del select para el efecto de label flotante
document.getElementById('tipo_documento').addEventListener('change', function() {
    if (this.value !== '') {
        this.classList.add('has-value');
    } else {
        this.classList.remove('has-value');
    }
});