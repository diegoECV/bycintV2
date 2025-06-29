// components.js - Cargador principal de componentes

// Clase principal para gestionar componentes
class ComponentManager {
    constructor() {
        this.components = new Map();
        this.init();
    }

    init() {
        // Registrar componentes disponibles
        this.registerComponents();
        
        // Inicializar componentes según la página
        this.initializePageComponents();
    }

    registerComponents() {
        // Aquí se pueden registrar componentes adicionales
        console.log('Componentes registrados:', this.components.size);
    }

    initializePageComponents() {
        const currentPage = this.getCurrentPage();
        
        // Inicializar componentes según la página
        switch (currentPage) {
            case 'tienda':
            case 'catalogo':
            case 'categoria':
                this.initProductComponents();
                break;
            case 'carrito':
                this.initCartComponents();
                break;
            case 'profile':
                this.initProfileComponents();
                break;
            default:
                this.initGlobalComponents();
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/tienda')) return 'tienda';
        if (path.includes('/catalogo')) return 'catalogo';
        if (path.includes('/categoria')) return 'categoria';
        if (path.includes('/carrito')) return 'carrito';
        if (path.includes('/profile')) return 'profile';
        return 'home';
    }

    initProductComponents() {
        // Componentes específicos para páginas de productos
        console.log('Inicializando componentes de productos');
    }

    initCartComponents() {
        // Componentes específicos para el carrito
        console.log('Inicializando componentes del carrito');
    }

    initProfileComponents() {
        // Componentes específicos para el perfil
        console.log('Inicializando componentes del perfil');
    }

    initGlobalComponents() {
        // Componentes globales (mini carrito, etc.)
        console.log('Inicializando componentes globales');
    }

    // Método para registrar nuevos componentes
    registerComponent(name, component) {
        this.components.set(name, component);
    }

    // Método para obtener un componente
    getComponent(name) {
        return this.components.get(name);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.componentManager = new ComponentManager();
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentManager;
} 