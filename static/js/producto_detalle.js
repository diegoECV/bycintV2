// producto_detalle.js

document.addEventListener('DOMContentLoaded', function() {
    // Acordeón
    document.querySelectorAll('[data-accordion]').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = document.getElementById(this.dataset.accordion);
            if (target) target.classList.toggle('hidden');
        });
    });

    // Selección de miniaturas
    document.querySelectorAll('.flex-row img').forEach(img => {
        img.addEventListener('click', function() {
            document.getElementById('main-img').src = this.src;
            document.querySelectorAll('.flex-row img').forEach(el => {
                el.classList.remove('border-green-500', 'ring-2', 'ring-green-400');
                el.classList.add('border-gray-200');
            });
            this.classList.remove('border-gray-200');
            this.classList.add('border-green-500', 'ring-2', 'ring-green-400');
        });
    });

    // Cambiar cantidad
    document.querySelectorAll('[data-cantidad]').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = document.getElementById('cantidad');
            let val = parseInt(input.value) + parseInt(this.dataset.cantidad);
            if (val < 1) val = 1;
            input.value = val;
        });
    });

    // Swiper para relacionados
    if (document.querySelector('.relacionadosSwiper')) {
        const relacionadosSwiper = new Swiper('.relacionadosSwiper', {
            slidesPerView: 4,
            spaceBetween: 20,
            loop: true,
            slidesPerGroup: 4,
            autoplay: false,
            navigation: {
                nextEl: '.relacionadosSwiper .swiper-button-next',
                prevEl: '.relacionadosSwiper .swiper-button-prev',
            },
            pagination: {
                el: '.relacionadosSwiper .swiper-pagination',
                clickable: true,
            }
        });
        let direction = 'next';
        setInterval(() => {
            if (direction === 'next') {
                relacionadosSwiper.slideNext();
                if (relacionadosSwiper.isEnd) direction = 'prev';
            } else {
                relacionadosSwiper.slidePrev();
                if (relacionadosSwiper.isBeginning) direction = 'next';
            }
        }, 4000);
    }

    // Evento para agregar al carrito
    const addBtn = document.querySelector('.btn-add-cart');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            const productoId = addBtn.getAttribute('data-id');
            const cantidad = parseInt(document.getElementById('cantidad').value) || 1;
            addBtn.disabled = true;
            fetch('/api/agregar_carrito', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ producto_id: productoId, cantidad: cantidad })
            })
            .then(res => {
                if (res.status === 401) {
                    alert('Debes iniciar sesión para agregar al carrito');
                    setTimeout(() => window.location.href = '/login', 1500);
                    throw new Error('No logueado');
                }
                return res.json();
            })
            .then(data => {
                addBtn.disabled = false;
                if (data.success) {
                    let notif = document.createElement('div');
                    notif.className = 'fixed top-6 right-6 z-50 px-6 py-3 rounded shadow-lg text-white font-bold transition-all bg-green-600';
                    notif.textContent = 'Producto agregado al carrito';
                    document.body.appendChild(notif);
                    setTimeout(() => notif.remove(), 2000);
                    fetch('/api/carrito').then(res => res.json()).then(data => {
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
                } else {
                    alert(data.message || 'No se pudo agregar');
                }
            })
            .catch((err) => {
                addBtn.disabled = false;
                if (err.message !== 'No logueado') {
                    alert('Error al agregar al carrito');
                }
            });
        });
    }
}); 