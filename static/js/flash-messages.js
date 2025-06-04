/**
 * Flash Messages Manager
 * Maneja la visualización y auto-ocultación de mensajes flash
 */

class FlashMessages {
    constructor(options = {}) {
        this.options = {
            autoHideDelay: options.autoHideDelay || 5000, // 5 segundos
            animationDuration: options.animationDuration || 500,
            enableAutoHide: options.enableAutoHide !== false,
            enableClickToClose: options.enableClickToClose !== false,
            toastStyle: options.toastStyle || false
        };
        
        this.init();
    }
    
    init() {
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupMessages());
        } else {
            this.setupMessages();
        }
    }
    
    setupMessages() {
        const flashContainer = document.querySelector('.flash-messages');
        if (!flashContainer) return;
        
        // Aplicar estilo toast si está habilitado
        if (this.options.toastStyle) {
            flashContainer.classList.add('toast-style');
        }
        
        const messages = flashContainer.querySelectorAll('.flash-message');
        
        messages.forEach((message, index) => {
            this.setupMessage(message, index);
        });
    }
    
    setupMessage(message, index = 0) {
        // Configurar botón de cerrar
        if (this.options.enableClickToClose) {
            const closeButton = message.querySelector('.flash-close');
            if (closeButton) {
                closeButton.addEventListener('click', () => this.closeMessage(message));
            }
            
            // También permitir cerrar haciendo click en el mensaje completo
            message.style.cursor = 'pointer';
            message.addEventListener('click', (e) => {
                if (e.target !== closeButton && !closeButton.contains(e.target)) {
                    this.closeMessage(message);
                }
            });
        }
        
        // Auto-hide si está habilitado
        if (this.options.enableAutoHide) {
            const delay = this.options.autoHideDelay + (index * 200); // Stagger para múltiples mensajes
            setTimeout(() => {
                this.closeMessage(message);
            }, delay);
        }
    }
    
    closeMessage(message) {
        if (message.classList.contains('fade-out')) return; // Ya se está cerrando
        
        message.classList.add('fade-out');
        
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, this.options.animationDuration);
    }
    
    // Método para agregar mensajes dinámicamente
    addMessage(text, category = 'info', options = {}) {
        const flashContainer = document.querySelector('.flash-messages');
        if (!flashContainer) {
            console.warn('Flash messages container not found');
            return;
        }
        
        const messageElement = this.createMessageElement(text, category, options);
        flashContainer.appendChild(messageElement);
        
        this.setupMessage(messageElement);
        
        return messageElement;
    }
    
    createMessageElement(text, category, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flash-message alert-${category}`;
        messageDiv.setAttribute('role', 'alert');
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const iconClass = icons[category] || icons.info;
        
        messageDiv.innerHTML = `
            <div class="flash-content">
                <i class="flash-icon ${iconClass}"></i>
                <span class="flash-text">${text}</span>
            </div>
            <button type="button" class="flash-close" title="Cerrar">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return messageDiv;
    }
    
    // Método para cerrar todos los mensajes
    closeAll() {
        const messages = document.querySelectorAll('.flash-message');
        messages.forEach(message => this.closeMessage(message));
    }
    
    // Método para configurar mensajes AJAX
    setupAjaxMessages() {
        // Interceptar respuestas AJAX para mostrar mensajes flash
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            return originalFetch(...args).then(response => {
                // Buscar mensajes flash en headers o respuesta
                const flashMessages = response.headers.get('X-Flash-Messages');
                if (flashMessages) {
                    try {
                        const messages = JSON.parse(flashMessages);
                        messages.forEach(msg => {
                            this.addMessage(msg.message, msg.category);
                        });
                    } catch (e) {
                        console.warn('Error parsing flash messages:', e);
                    }
                }
                return response;
            });
        };
    }
}

// Configuraciones predefinidas
const FlashConfigs = {
    default: {
        autoHideDelay: 5000,
        enableAutoHide: true,
        enableClickToClose: true,
        toastStyle: false
    },
    
    toast: {
        autoHideDelay: 4000,
        enableAutoHide: true,
        enableClickToClose: true,
        toastStyle: true
    },
    
    persistent: {
        enableAutoHide: false,
        enableClickToClose: true,
        toastStyle: false
    }
};

// Inicializar automáticamente
let flashManager;

// Función global para fácil acceso
window.FlashMessages = {
    init: (config = 'default') => {
        const options = typeof config === 'string' ? FlashConfigs[config] : config;
        flashManager = new FlashMessages(options);
        return flashManager;
    },
    
    add: (text, category = 'info', options = {}) => {
        if (!flashManager) {
            flashManager = new FlashMessages();
        }
        return flashManager.addMessage(text, category, options);
    },
    
    closeAll: () => {
        if (flashManager) {
            flashManager.closeAll();
        }
    }
};

// Auto-inicializar con configuración por defecto
document.addEventListener('DOMContentLoaded', () => {
    window.FlashMessages.init();
});