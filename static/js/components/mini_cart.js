// mini_cart.js - Funcionalidad para el mini carrito

class MiniCart {
    constructor() {
        this.cartIcon = document.getElementById('cart-icon-link');
        this.miniCart = document.getElementById('mini-cart');
        this.miniCartList = document.getElementById('mini-cart-list');
        this.miniCartTotal = document.getElementById('mini-cart-total');
        this.miniCartPagar = document.getElementById('mini-cart-pagar');
        
        this.init();
    }

    init() {
        if (!this.cartIcon || !this.miniCart) return;
        
        this.setupEventListeners();
        this.updateCartCount();
    }

    setupEventListeners() {
        // Mostrar mini-cart al pasar mouse o hacer clic
        let miniCartTimeout;
        
        const showMiniCart = () => {
            clearTimeout(miniCartTimeout);
            this.miniCart.classList.remove('hidden');
            this.renderMiniCart();
        };
        
        const hideMiniCart = () => {
            miniCartTimeout = setTimeout(() => {
                this.miniCart.classList.add('hidden');
            }, 200);
        };

        this.cartIcon.addEventListener('mouseenter', showMiniCart);
        this.cartIcon.addEventListener('mouseleave', hideMiniCart);
        this.miniCart.addEventListener('mouseenter', () => clearTimeout(miniCartTimeout));
        this.miniCart.addEventListener('mouseleave', hideMiniCart);

        // Evento para ir a pagar
        if (this.miniCartPagar) {
            this.miniCartPagar.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/carrito';
            });
        }
    }

    renderMiniCart() {
        fetch('/api/carrito')
            .then(res => res.json())
            .then(data => {
                if (!data.productos || data.productos.length === 0) {
                    this.miniCartList.innerHTML = '<div class="text-center text-gray-500 py-4">Tu carrito está vacío</div>';
                    this.miniCartTotal.textContent = 'S/ 0.00';
                    return;
                }

                let total = 0;
                this.miniCartList.innerHTML = data.productos.map(prod => {
                    total += prod.subtotal;
                    return `
                        <div class="flex items-center gap-3 py-2 border-b border-gray-100 last:border-b-0">
                            <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-12 h-12 object-contain rounded shadow">
                            <div class="flex-1 min-w-0">
                                <div class="font-semibold text-sm truncate">${prod.nombre}</div>
                                <div class="text-xs text-gray-500">Cantidad: ${prod.cantidad}</div>
                                <div class="text-sm font-bold text-green-600">S/ ${prod.subtotal.toFixed(2)}</div>
                            </div>
                            <button class="text-red-500 hover:text-red-700 text-lg btn-remove-mini-cart" data-id="${prod.id}">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;
                }).join('');

                this.miniCartTotal.textContent = `S/ ${total.toFixed(2)}`;

                // Eventos para eliminar productos del mini carrito
                this.miniCartList.querySelectorAll('.btn-remove-mini-cart').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const productoId = btn.getAttribute('data-id');
                        this.removeFromCart(productoId);
                    });
                });
            })
            .catch(err => {
                console.error('Error al cargar mini carrito:', err);
                this.miniCartList.innerHTML = '<div class="text-center text-red-500 py-4">Error al cargar carrito</div>';
            });
    }

    removeFromCart(productoId) {
        fetch('/api/eliminar_carrito', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ producto_id: productoId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                this.renderMiniCart();
                this.updateCartCount();
                this.showNotification('Producto eliminado del carrito', 'success');
            } else {
                this.showNotification(data.message || 'No se pudo eliminar', 'error');
            }
        })
        .catch(() => {
            this.showNotification('Error al eliminar del carrito', 'error');
        });
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
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new MiniCart();
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MiniCart;
} 