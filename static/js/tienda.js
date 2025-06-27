// tienda.js - Lógica AJAX y animaciones para /tienda

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar filtros y eventos
  initTiendaFiltros();
});

let ordenActual = 'relevancia';

function initTiendaFiltros() {
  const form = document.getElementById('filtros-tienda');
  if (!form) return;
  form.addEventListener('change', fetchAndRenderProductos);
  fetchAndRenderProductos(); // Cargar productos al inicio

  // Selector de orden
  const ordenarBtn = document.getElementById('ordenar-btn');
  const ordenarMenu = document.getElementById('ordenar-menu');
  const ordenActualSpan = document.getElementById('orden-actual');
  if (ordenarBtn && ordenarMenu) {
    ordenarBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      ordenarMenu.classList.toggle('hidden');
    });
    document.body.addEventListener('click', function() {
      ordenarMenu.classList.add('hidden');
    });
    ordenarMenu.querySelectorAll('.orden-opcion').forEach(btn => {
      btn.addEventListener('click', function() {
        ordenActual = this.getAttribute('data-orden');
        ordenActualSpan.textContent = this.textContent;
        ordenarMenu.classList.add('hidden');
        fetchAndRenderProductos();
      });
    });
  }
}

function fetchAndRenderProductos() {
  showLoader();
  const form = document.getElementById('filtros-tienda');
  const formData = new FormData(form);
  const params = new URLSearchParams();
  // Categorías (pueden ser varias)
  formData.getAll('categoria').forEach(cat => params.append('categoria', cat));
  // Ofertas y novedades
  if (formData.get('oferta')) params.append('oferta', '1');
  if (formData.get('novedad')) params.append('novedad', '1');
  // Precio
  if (formData.get('precio')) params.append('precio', formData.get('precio'));
  // Orden
  params.append('orden', ordenActual);

  fetch('/api/productos?' + params.toString())
    .then(res => res.json())
    .then(data => {
      renderProductos(data.productos);
      // Actualizar contador
      const contador = document.getElementById('contador-productos');
      if (contador) {
        contador.textContent = `${data.productos.length} productos`;
      }
    })
    .catch(() => {
      renderProductos([]);
      const contador = document.getElementById('contador-productos');
      if (contador) contador.textContent = '0 productos';
    });
}

function renderProductos(productos) {
  const cont = document.getElementById('productos-lista');
  if (!cont) return;
  if (!productos.length) {
    cont.innerHTML = '<div class="col-span-4 text-center text-gray-400 py-12">No se encontraron productos.</div>';
    return;
  }
  cont.innerHTML = productos.map(prod => `
    <div class="relative bg-white rounded-2xl shadow-lg p-5 flex flex-col items-center group transition-transform hover:-translate-y-1 hover:shadow-2xl cursor-pointer tarjeta-producto" data-id="${prod.id}">
      ${prod.descuento ? `<span class="absolute left-4 top-4 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">-${prod.descuento}%</span>` : ''}
      <button class="absolute right-4 top-4 text-gray-300 hover:text-red-500 text-xl transition"><i class="fa-regular fa-heart"></i></button>
      <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-48 h-48 object-contain mb-4 rounded-lg shadow">
      <h3 class="text-base font-bold text-center mb-1">${prod.nombre}</h3>
      <div class="flex items-center gap-2 mb-3">
        ${prod.precio_original ? `<span class="text-gray-400 line-through text-sm">S/ ${prod.precio_original.toFixed(2)}</span>` : ''}
        <span class="text-black font-bold text-lg">S/ ${prod.precio.toFixed(2)}</span>
      </div>
      <button class="w-full flex items-center justify-center gap-2 bg-green-600 text-white py-2 rounded-lg font-bold text-base mt-auto hover:bg-green-700 transition shadow btn-add-cart" data-id="${prod.id}">
        <i class="fa-solid fa-cart-plus"></i> Agregar
      </button>
    </div>
  `).join('');

  // Evento para click en la tarjeta (excepto botón Agregar)
  cont.querySelectorAll('.tarjeta-producto').forEach(card => {
    card.addEventListener('click', function(e) {
      if (e.target.closest('.btn-add-cart')) return; // No navegar si es el botón Agregar
      const id = this.getAttribute('data-id');
      window.location.href = `/producto/${id}`;
    });
  });

  // Evento para agregar al carrito
  cont.addEventListener('click', function(e) {
    if (e.target.closest('.btn-add-cart')) {
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
          alert('Debes iniciar sesión para agregar al carrito');
          setTimeout(() => window.location.href = '/login', 1500);
          throw new Error('No logueado');
        }
        return res.json();
      })
      .then(data => {
        btn.disabled = false;
        if (data.success) {
          // Notificación visual
          let notif = document.createElement('div');
          notif.className = 'fixed top-6 right-6 z-50 px-6 py-3 rounded shadow-lg text-white font-bold transition-all bg-green-600';
          notif.textContent = 'Producto agregado al carrito';
          document.body.appendChild(notif);
          setTimeout(() => notif.remove(), 2000);
          // Actualizar contador
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
        btn.disabled = false;
        if (err.message !== 'No logueado') {
          alert('Error al agregar al carrito');
        }
      });
    }
  });
}

function showLoader() {
  const cont = document.getElementById('productos-lista');
  if (cont) cont.innerHTML = '<div class="text-center w-full py-12"><span class="loader"></span> Cargando productos...</div>';
}

function hideLoader() {
  // El renderizado real de productos reemplazará el loader
}

// Aquí puedes agregar animaciones para la tienda general 