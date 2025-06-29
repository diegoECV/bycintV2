// product_card.js - Funcionalidad para tarjetas de producto

class ProductCard {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Evento para agregar al carrito
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-add-cart')) {
                this.handleAddToCart(e);
            }
            
            // Evento para click en la tarjeta (excepto botón Agregar)
            if (e.target.closest('.tarjeta-producto')) {
                this.handleCardClick(e);
            }
        });

        // Evento para favoritos
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-fav')) {
                this.handleFavorite(e);
            }
        });
    }

    handleAddToCart(e) {
        const btn = e.target.closest('.btn-add-cart');
        const productoId = btn.getAttribute('data-id');
        
        btn.disabled = true;
        
        fetch('/api/agregar_carrito', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ producto_id: productoId })
        })
        .then(res => {
            if (res.status === 401) {
                this.showNotification('Debes iniciar sesión para agregar al carrito', 'error');
                setTimeout(() => window.location.href = '/login', 1500);
                throw new Error('No logueado');
            }
            return res.json();
        })
        .then(data => {
            btn.disabled = false;
            if (data.success) {
                this.showNotification('Producto agregado al carrito', 'success');
                this.updateCartCount();
            } else {
                this.showNotification(data.message || 'No se pudo agregar', 'error');
            }
        })
        .catch((err) => {
            btn.disabled = false;
            if (err.message !== 'No logueado') {
                this.showNotification('Error al agregar al carrito', 'error');
            }
        });
    }

    handleCardClick(e) {
        if (e.target.closest('.btn-add-cart') || e.target.closest('.btn-fav')) {
            return; // No navegar si es el botón Agregar o Favorito
        }
        const card = e.target.closest('.tarjeta-producto');
        const id = card.getAttribute('data-id');
        window.location.href = `/producto/${id}`;
    }

    handleFavorite(e) {
        const btn = e.target.closest('.btn-fav');
        const icon = btn.querySelector('i');
        
        // Toggle del estado de favorito
        if (icon.classList.contains('fa-regular')) {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid', 'text-red-500');
            this.showNotification('Agregado a favoritos', 'success');
        } else {
            icon.classList.remove('fa-solid', 'text-red-500');
            icon.classList.add('fa-regular');
            this.showNotification('Removido de favoritos', 'info');
        }
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-600',
            error: 'bg-red-600',
            info: 'bg-blue-600'
        };
        
        const notification = document.createElement('div');
        notification.className = `fixed top-6 right-6 z-50 px-6 py-3 rounded shadow-lg text-white font-bold transition-all ${colors[type] || colors.info}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    updateCartCount() {
        fetch('/api/carrito')
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById('cart-count');
                if (badge) {
                    if (data.cantidad > 0) {
                        badge.textContent = data.cantidad;
                        badge.classList.remove('hidden');
                    } else {
                        badge.textContent = '';
                        badge.classList.add('hidden');
                    }
                }
            });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ProductCard();
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProductCard;
} 