// categoria.js - Lógica AJAX para filtros y renderizado de productos en categorías

document.addEventListener('DOMContentLoaded', function() {
  initCategoriaFiltros();
  fetchAndRenderProductosCategoria();
});

function initCategoriaFiltros() {
  const form = document.getElementById('filtros-categoria');
  if (!form) return;
  form.addEventListener('change', fetchAndRenderProductosCategoria);
  document.getElementById('ordenar-categoria').addEventListener('change', fetchAndRenderProductosCategoria);
  const slider = document.getElementById('precio-slider');
  if (slider) {
    slider.addEventListener('input', function() {
      document.getElementById('precio-max').textContent = this.value;
    });
  }
}

function fetchAndRenderProductosCategoria() {
  const form = document.getElementById('filtros-categoria');
  const formData = new FormData(form);
  const params = new URLSearchParams();
  formData.forEach((value, key) => {
    params.append(key, value);
  });
  params.append('orden', document.getElementById('ordenar-categoria').value);
  params.append('categoria', form.getAttribute('data-categoria'));

  showLoaderCategoria();

  fetch('/api/productos_categoria?' + params.toString())
    .then(res => res.json())
    .then(data => {
      renderProductosCategoria(data.productos);
      const contador = document.getElementById('contador-productos');
      if (contador) {
        contador.textContent = `${data.productos.length} productos`;
      }
    })
    .catch(() => {
      renderProductosCategoria([]);
      const contador = document.getElementById('contador-productos');
      if (contador) contador.textContent = '0 productos';
    });
}

function showLoaderCategoria() {
  const cont = document.getElementById('productos-categoria-lista');
  if (cont) cont.innerHTML = '<div class="text-center w-full py-12"><span class="loader"></span> Cargando productos...</div>';
}

function renderProductosCategoria(productos) {
  const cont = document.getElementById('productos-categoria-lista');
  if (!cont) return;
  if (!productos.length) {
    cont.innerHTML = '<div class="col-span-4 text-center text-gray-400 py-12">No se encontraron productos.</div>';
    return;
  }
  cont.innerHTML = productos.map(prod => `
    <div class="relative bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center group hover:shadow-2xl transition">
      ${prod.descuento ? `<span class="absolute left-4 top-4 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">-${prod.descuento}%</span>` : ''}
      <button class="absolute right-4 top-4 text-gray-300 hover:text-red-500 text-xl transition"><i class="fa-regular fa-heart"></i></button>
      <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-40 h-40 object-contain mb-4 rounded-lg shadow">
      <h3 class="text-lg font-bold text-center mb-1">${prod.nombre}</h3>
      <div class="flex items-center gap-2 mb-3">
        ${prod.precio_original ? `<span class="text-gray-400 line-through text-sm">S/ ${prod.precio_original.toFixed(2)}</span>` : ''}
        <span class="text-black font-bold text-xl">S/ ${prod.precio.toFixed(2)}</span>
      </div>
      <button class="w-full flex items-center justify-center gap-2 bg-green-600 text-white py-2 rounded-lg font-bold text-base mt-auto hover:bg-green-700 transition shadow btn-add-cart" data-id="${prod.id}">
        <i class="fa-solid fa-cart-plus"></i> Agregar
      </button>
    </div>
  `).join('');

  // Agregar funcionalidad al botón Agregar
  cont.querySelectorAll('.btn-add-cart').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      const id = this.getAttribute('data-id');
      fetch('/api/agregar_carrito', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ producto_id: id })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          mostrarToast('Producto añadido al carrito');
        } else {
          alert(data.message || 'No se pudo agregar al carrito');
        }
      })
      .catch(() => {
        alert('Error al agregar al carrito');
      });
    });
  });

  // Permitir navegar al detalle al hacer clic en la card (excepto botón Agregar)
  cont.querySelectorAll('.relative.bg-white').forEach(card => {
    card.addEventListener('click', function(e) {
      if (e.target.closest('.btn-add-cart')) return; // No navegar si es el botón Agregar
      const idx = Array.from(cont.children).indexOf(this);
      const id = productos[idx]?.id;
      if (id) {
        window.location.href = `/producto/${id}`;
      }
    });
  });
}

function mostrarToast(mensaje) {
  let toast = document.getElementById('toast-msg');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast-msg';
    toast.style.position = 'fixed';
    toast.style.bottom = '32px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.background = '#22c55e';
    toast.style.color = 'white';
    toast.style.padding = '16px 32px';
    toast.style.borderRadius = '9999px';
    toast.style.fontWeight = 'bold';
    toast.style.fontSize = '1rem';
    toast.style.boxShadow = '0 2px 16px rgba(65, 243, 110, 0.94)';
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);
  }
  toast.textContent = mensaje;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 2000);
} 