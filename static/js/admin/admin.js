// JavaScript para el panel de administración
document.addEventListener('DOMContentLoaded', function() {
    console.log('Panel de administración cargado');
    
    // Inicializar tooltips
    initializeTooltips();
    
    // Inicializar notificaciones
    initializeNotifications();
    
    // Inicializar confirmaciones
    initializeConfirmations();
    
    // Inicializar búsquedas en tiempo real
    initializeRealTimeSearch();
});

// Funciones de utilidad
function initializeTooltips() {
    // Agregar tooltips a elementos con data-tooltip
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.left = this.offsetLeft + 'px';
            tooltip.style.top = (this.offsetTop - 30) + 'px';
            document.body.appendChild(tooltip);
            this.tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
}

function initializeNotifications() {
    // Auto-ocultar notificaciones después de 5 segundos
    const notifications = document.querySelectorAll('.bg-green-50, .bg-red-50, .bg-blue-50');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    });
}

function initializeConfirmations() {
    // Confirmar acciones destructivas
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function initializeRealTimeSearch() {
    // Búsqueda en tiempo real para tablas
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetTable = this.getAttribute('data-search');
            const table = document.querySelector(targetTable);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });
}

// Funciones específicas del dashboard
function updateDashboardStats() {
    // Actualizar estadísticas del dashboard en tiempo real
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            // Actualizar contadores
            const totalProductos = document.getElementById('total-productos');
            const totalCategorias = document.getElementById('total-categorias');
            const totalUsuarios = document.getElementById('total-usuarios');
            const totalPedidos = document.getElementById('total-pedidos');
            
            if (totalProductos) totalProductos.textContent = data.productos;
            if (totalCategorias) totalCategorias.textContent = data.categorias;
            if (totalUsuarios) totalUsuarios.textContent = data.usuarios;
            if (totalPedidos) totalPedidos.textContent = data.pedidos;
        })
        .catch(error => console.error('Error actualizando estadísticas:', error));
}

// Funciones de notificación
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Funciones de filtros avanzados
function applyAdvancedFilters() {
    const filters = {
        dateFrom: document.getElementById('date-from')?.value,
        dateTo: document.getElementById('date-to')?.value,
        category: document.getElementById('category-filter')?.value,
        status: document.getElementById('status-filter')?.value
    };
    
    // Aplicar filtros a la tabla actual
    const table = document.querySelector('table');
    if (table) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            let show = true;
            
            // Aplicar lógica de filtros aquí
            if (filters.category && row.dataset.category !== filters.category) {
                show = false;
            }
            
            row.style.display = show ? '' : 'none';
        });
    }
}

// Funciones de paginación
function changePage(page) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('page', page);
    window.location.href = currentUrl.toString();
}

// Funciones de ordenamiento
function sortTable(column, direction = 'asc') {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();
        
        if (direction === 'asc') {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdmin);
} else {
    initializeAdmin();
}

function initializeAdmin() {
    console.log('Panel de administración inicializado');
    
    // Configurar eventos globales
    setupGlobalEvents();
    
    // Inicializar componentes específicos según la página
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('/admin/dashboard')) {
        initializeDashboard();
    } else if (currentPage.includes('/admin/productos')) {
        initializeProducts();
    } else if (currentPage.includes('/admin/usuarios')) {
        initializeUsers();
    } else if (currentPage.includes('/admin/pedidos')) {
        initializeOrders();
    }
}

function setupGlobalEvents() {
    // Evento para cerrar modales con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                }
            });
        }
    });
    
    // Evento para confirmar antes de salir si hay cambios sin guardar
    window.addEventListener('beforeunload', function(e) {
        const forms = document.querySelectorAll('form[data-changed="true"]');
        if (forms.length > 0) {
            e.preventDefault();
            e.returnValue = 'Tienes cambios sin guardar. ¿Estás seguro de que quieres salir?';
        }
    });
}

function initializeDashboard() {
    // Actualizar estadísticas cada 30 segundos
    setInterval(updateDashboardStats, 30000);
    
    // Inicializar gráficos si existen
    if (typeof Chart !== 'undefined') {
        console.log('Gráficos inicializados');
    }
}

function initializeProducts() {
    // Configurar eventos específicos de productos
    console.log('Página de productos inicializada');
}

function initializeUsers() {
    // Configurar eventos específicos de usuarios
    console.log('Página de usuarios inicializada');
}

function initializeOrders() {
    // Configurar eventos específicos de pedidos
    console.log('Página de pedidos inicializada');
} 