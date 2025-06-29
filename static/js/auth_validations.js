// Archivo de validaciones de autenticación

/**
 * Validaciones de autenticación para bycint Cosméticos
 * Funciones de validación para login y registro
 */

// Variables globales
let isSubmitting = false;

// ===== FUNCIONES DE VALIDACIÓN =====

/**
 * Validar nombre completo
 */
function validateNombre(input) {
    const nombre = input.value.trim();
    const errorDiv = document.getElementById('nombre-error');
    
    if (!nombre) {
        showError(input, errorDiv, 'El nombre es obligatorio');
        return false;
    }
    
    if (nombre.length < 2) {
        showError(input, errorDiv, 'El nombre debe tener al menos 2 caracteres');
        return false;
    }
    
    if (nombre.length > 100) {
        showError(input, errorDiv, 'El nombre no puede exceder 100 caracteres');
        return false;
    }
    
    const nombreRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    if (!nombreRegex.test(nombre)) {
        showError(input, errorDiv, 'El nombre solo puede contener letras y espacios');
        return false;
    }
    
    hideError(input, errorDiv);
    return true;
}

/**
 * Validar email
 */
function validateEmail(input) {
    const email = input.value.trim();
    const errorDiv = document.getElementById('email-error');
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (!email) {
        showError(input, errorDiv, 'El email es obligatorio');
        return false;
    }
    
    if (!emailRegex.test(email)) {
        showError(input, errorDiv, 'Por favor ingresa un email válido');
        return false;
    }
    
    if (email.length > 254) {
        showError(input, errorDiv, 'El email es demasiado largo');
        return false;
    }
    
    // Verificar caracteres sospechosos
    const suspiciousChars = ['<', '>', '"', "'", ';', '(', ')', '[', ']', '\\', '/'];
    if (suspiciousChars.some(char => email.includes(char))) {
        showError(input, errorDiv, 'El email contiene caracteres no permitidos');
        return false;
    }
    
    hideError(input, errorDiv);
    return true;
}

/**
 * Validar contraseña
 */
function validatePassword(input) {
    const password = input.value;
    const errorDiv = document.getElementById('password-error');
    
    if (!password) {
        showError(input, errorDiv, 'La contraseña es obligatoria');
        return false;
    }
    
    if (password.length < 8) {
        showError(input, errorDiv, 'La contraseña debe tener al menos 8 caracteres');
        return false;
    }
    
    if (password.length > 128) {
        showError(input, errorDiv, 'La contraseña no puede exceder 128 caracteres');
        return false;
    }
    
    if (!/[A-Z]/.test(password)) {
        showError(input, errorDiv, 'La contraseña debe contener al menos una letra mayúscula');
        return false;
    }
    
    if (!/[a-z]/.test(password)) {
        showError(input, errorDiv, 'La contraseña debe contener al menos una letra minúscula');
        return false;
    }
    
    if (!/\d/.test(password)) {
        showError(input, errorDiv, 'La contraseña debe contener al menos un número');
        return false;
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        showError(input, errorDiv, 'La contraseña debe contener al menos un carácter especial (!@#$%^&*)');
        return false;
    }
    
    // Verificar contraseñas comunes
    const commonPasswords = [
        'password', '123456', '123456789', 'qwerty', 'abc123', 
        'password123', 'admin', 'letmein', 'welcome', 'monkey',
        '12345678', '1234567', '1234567890', 'password1', '123123'
    ];
    if (commonPasswords.includes(password.toLowerCase())) {
        showError(input, errorDiv, 'La contraseña es demasiado común, elige una más segura');
        return false;
    }
    
    hideError(input, errorDiv);
    return true;
}

/**
 * Validar confirmación de contraseña
 */
function validateConfirmPassword(input) {
    const confirmPassword = input.value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('confirm-password-error');
    
    if (!confirmPassword) {
        showError(input, errorDiv, 'Debes confirmar tu contraseña');
        return false;
    }
    
    if (confirmPassword !== password) {
        showError(input, errorDiv, 'Las contraseñas no coinciden');
        return false;
    }
    
    hideError(input, errorDiv);
    return true;
}

/**
 * Validar teléfono
 */
function validateTelefono(input) {
    const telefono = input.value.trim();
    const errorDiv = document.getElementById('telefono-error');
    
    if (!telefono) {
        hideError(input, errorDiv); // Es opcional
        return true;
    }
    
    // Patrón para teléfonos peruanos
    const peruRegex = /^(\+51\s?)?[9]\d{8}$/;
    // Patrón internacional básico
    const intlRegex = /^\+?[\d\s\-\(\)]{7,15}$/;
    
    if (!peruRegex.test(telefono) && !intlRegex.test(telefono)) {
        showError(input, errorDiv, 'Formato de teléfono inválido');
        return false;
    }
    
    hideError(input, errorDiv);
    return true;
}

/**
 * Verificar fortaleza de contraseña
 */
function checkPasswordStrength(input) {
    const password = input.value;
    const strength1 = document.getElementById('strength-1');
    const strength2 = document.getElementById('strength-2');
    const strength3 = document.getElementById('strength-3');
    const strength4 = document.getElementById('strength-4');
    const strengthText = document.getElementById('strength-text');
    
    if (!strength1) return; // Si no existe el elemento, salir
    
    let score = 0;
    let text = '';
    let color = '';
    
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
    if (password.length >= 12) score++;
    
    // Reset colors
    [strength1, strength2, strength3, strength4].forEach(bar => {
        bar.className = 'h-1 flex-1 bg-gray-200 rounded';
    });
    
    if (score <= 2) {
        color = 'bg-red-500';
        text = 'Débil';
    } else if (score <= 4) {
        color = 'bg-yellow-500';
        text = 'Media';
    } else if (score <= 5) {
        color = 'bg-blue-500';
        text = 'Buena';
    } else {
        color = 'bg-green-500';
        text = 'Excelente';
    }
    
    // Apply colors
    for (let i = 0; i < Math.min(score, 4); i++) {
        [strength1, strength2, strength3, strength4][i].className = `h-1 flex-1 ${color} rounded`;
    }
    
    strengthText.textContent = text;
    strengthText.className = `text-xs mt-1 ${color.replace('bg-', 'text-')}`;
}

// ===== FUNCIONES DE UI =====

/**
 * Mostrar error en campo
 */
function showError(input, errorDiv, message) {
    if (!input || !errorDiv) return;
    
    input.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
    input.classList.remove('border-gray-300', 'focus:border-green-500', 'focus:ring-green-500');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

/**
 * Ocultar error en campo
 */
function hideError(input, errorDiv) {
    if (!input || !errorDiv) return;
    
    input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
    input.classList.add('border-gray-300', 'focus:border-green-500', 'focus:ring-green-500');
    errorDiv.classList.add('hidden');
}

/**
 * Limpiar todos los errores
 */
function clearAllErrors() {
    document.querySelectorAll('.text-red-600').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('input').forEach(input => {
        input.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-300', 'focus:border-green-500', 'focus:ring-green-500');
    });
}

/**
 * Mostrar estado de carga
 */
function showLoading(buttonId, textId, iconId, loadingText) {
    const submitBtn = document.getElementById(buttonId);
    const submitText = document.getElementById(textId);
    const loadingIcon = document.getElementById(iconId);
    
    if (submitBtn) submitBtn.disabled = true;
    if (submitText) submitText.textContent = loadingText;
    if (loadingIcon) loadingIcon.classList.remove('hidden');
}

/**
 * Ocultar estado de carga
 */
function hideLoading(buttonId, textId, iconId, originalText) {
    const submitBtn = document.getElementById(buttonId);
    const submitText = document.getElementById(textId);
    const loadingIcon = document.getElementById(iconId);
    
    if (submitBtn) submitBtn.disabled = false;
    if (submitText) submitText.textContent = originalText;
    if (loadingIcon) loadingIcon.classList.add('hidden');
}

// ===== VALIDACIÓN DE FORMULARIOS =====

/**
 * Validar formulario de login
 */
function validateLoginForm() {
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    
    return isEmailValid && isPasswordValid;
}

/**
 * Validar formulario de registro
 */
function validateRegisterForm() {
    const nombre = document.getElementById('nombre');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const telefono = document.getElementById('telefono');
    const terms = document.getElementById('terms');
    
    const isNombreValid = validateNombre(nombre);
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword);
    const isTelefonoValid = validateTelefono(telefono);
    
    if (!terms.checked) {
        alert('Debes aceptar los términos y condiciones');
        return false;
    }
    
    return isNombreValid && isEmailValid && isPasswordValid && isConfirmPasswordValid && isTelefonoValid;
}

// ===== EVENT LISTENERS =====

/**
 * Configurar event listeners para limpiar errores al escribir
 */
function setupInputListeners() {
    const inputs = {
        'nombre': 'nombre-error',
        'email': 'email-error',
        'password': 'password-error',
        'confirm_password': 'confirm-password-error',
        'telefono': 'telefono-error'
    };
    
    Object.entries(inputs).forEach(([inputId, errorId]) => {
        const input = document.getElementById(inputId);
        const errorDiv = document.getElementById(errorId);
        
        if (input && errorDiv) {
            input.addEventListener('input', function() {
                if (this.value.trim()) {
                    hideError(this, errorDiv);
                }
            });
        }
    });
}

/**
 * Configurar validación de formulario
 */
function setupFormValidation(formId, validationFunction, loadingConfig) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        
        if (!validationFunction()) {
            e.preventDefault();
            return false;
        }
        
        // Mostrar loading
        showLoading(loadingConfig.buttonId, loadingConfig.textId, loadingConfig.iconId, loadingConfig.loadingText);
        
        // Limpiar errores previos
        clearAllErrors();
        
        isSubmitting = true;
    });
}

// ===== INICIALIZACIÓN =====

/**
 * Inicializar validaciones cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', function() {
    setupInputListeners();
    
    // Configurar validación de login
    setupFormValidation('loginForm', validateLoginForm, {
        buttonId: 'submitBtn',
        textId: 'submitText',
        iconId: 'loadingIcon',
        loadingText: 'Iniciando sesión...'
    });
    
    // Configurar validación de registro
    setupFormValidation('registerForm', validateRegisterForm, {
        buttonId: 'submitBtn',
        textId: 'submitText',
        iconId: 'loadingIcon',
        loadingText: 'Creando cuenta...'
    });
});

// Exportar funciones para uso global
window.authValidations = {
    validateNombre,
    validateEmail,
    validatePassword,
    validateConfirmPassword,
    validateTelefono,
    checkPasswordStrength,
    validateLoginForm,
    validateRegisterForm,
    showError,
    hideError,
    clearAllErrors,
    showLoading,
    hideLoading
};
