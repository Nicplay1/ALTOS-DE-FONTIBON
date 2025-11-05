function togglePassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    
    if (input.type === "password") {
        input.type = "text";
        iconElement.classList.remove("fa-eye");
        iconElement.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        iconElement.classList.remove("fa-eye-slash");
        iconElement.classList.add("fa-eye");
    }
}

function validarPassword() {
    const passwordInput = document.getElementById("id_contraseña");
    const errorMsg = document.getElementById("passwordHelp");
    const regex = /^(?=.*[A-Z]).{6,}$/;
    
    const pass = passwordInput.value;
    if (!regex.test(pass)) {
        errorMsg.classList.add("show-error");
        setTimeout(() => {
            errorMsg.classList.remove("show-error");
        }, 5500); // se oculta después de la animación
        return false; // evita enviar el form
    }
    return true;
}