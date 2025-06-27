// catalogo_categoria.js - Lógica AJAX y animaciones para /categoria/<nombre_categoria>

document.addEventListener('DOMContentLoaded', function() {
  // Inicializar filtros avanzados y eventos
  initCatalogoFiltros();
  initAcordeonesFiltros();
  initAddToCart();
  actualizarCartCount();
  if (document.getElementById('carrito-table-body')) {
    renderizarCarrito();
    setupCuponCarrito();
    setupEnvioCarrito();
  }
  setupMiniCart();
});

function initCatalogoFiltros() {
  const form = document.getElementById('filtros-tienda');
  if (!form) return;
  form.addEventListener('change', fetchAndRenderProductosCategoria);
  fetchAndRenderProductosCategoria(); // Cargar productos al inicio
}

function fetchAndRenderProductosCategoria() {
  showLoaderCategoria();
  const form = document.getElementById('filtros-tienda');
  const formData = new FormData(form);
  const params = new URLSearchParams();
  // Filtros avanzados (tipo, acabado, material, genero, etc.)
  formData.forEach((value, key) => {
    params.append(key, value);
  });
  // Obtener la categoría desde un data-atributo o variable global
  const categoria = form.getAttribute('data-categoria');
  if (categoria) params.append('categoria', categoria);

  fetch('/api/productos_categoria?' + params.toString())
    .then(res => res.json())
    .then(data => {
      renderProductosCategoria(data.productos);
    })
    .catch(() => {
      renderProductosCategoria([]);
    });
}

function renderProductosCategoria(productos) {
  const cont = document.getElementById('productos-lista');
  if (!cont) return;
  if (!productos.length) {
    cont.innerHTML = '<div class="col-span-4 text-center text-gray-400 py-12">No se encontraron productos.</div>';
    return;
  }
  cont.innerHTML = productos.map(prod => `
    <div class="relative bg-white rounded-2xl shadow-lg p-5 flex flex-col items-center group transition-transform hover:-translate-y-1 hover:shadow-2xl">
      ${prod.descuento ? `<span class="absolute left-4 top-4 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">-${prod.descuento}%</span>` : ''}
      <button class="absolute right-4 top-4 text-gray-300 hover:text-red-500 text-xl transition"><i class="fa-regular fa-heart"></i></button>
      <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-32 h-32 object-contain mb-4 rounded-lg shadow">
      <h3 class="text-base font-bold text-center mb-1">${prod.nombre}</h3>
      <div class="flex items-center gap-2 mb-3">
        ${prod.precio_original ? `<span class="text-gray-400 line-through text-sm">S/ ${prod.precio_original.toFixed(2)}</span>` : ''}
        <span class="text-black font-bold text-lg">S/ ${prod.precio.toFixed(2)}</span>
      </div>
      <button class="w-full flex items-center justify-center gap-2 bg-green-600 text-white py-2 rounded-lg font-bold text-base mt-auto hover:bg-green-700 transition shadow">
        <i class="fa-solid fa-cart-plus"></i> Agregar
      </button>
    </div>
  `).join('');
}

function showLoaderCategoria() {
  const cont = document.getElementById('productos-lista');
  if (cont) cont.innerHTML = '<div class="text-center w-full py-12"><span class="loader"></span> Cargando productos...</div>';
}

function hideLoaderCategoria() {
  // El renderizado real de productos reemplazará el loader
}

function initAcordeonesFiltros() {
  // TODO: Lógica para abrir/cerrar acordeones de filtros avanzados
}

function initAddToCart() {
  document.body.addEventListener('click', function(e) {
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
          mostrarNotificacion('Debes iniciar sesión para agregar al carrito', 'error');
          setTimeout(() => window.location.href = '/login', 1500);
          throw new Error('No logueado');
        }
        return res.json();
      })
      .then(data => {
        btn.disabled = false;
        if (data.success) {
          mostrarNotificacion('Producto agregado al carrito', 'success');
          actualizarCartCount();
          if (window.location.pathname.includes('/carrito')) {
            renderizarCarrito();
          }
        } else {
          mostrarNotificacion(data.message || 'No se pudo agregar', 'error');
          console.error('Error al agregar al carrito:', data);
        }
      })
      .catch((err) => {
        btn.disabled = false;
        if (err.message !== 'No logueado') {
          mostrarNotificacion('Error al agregar al carrito', 'error');
          console.error('Error AJAX:', err);
        }
      });
    }
    // Eliminar producto
    if (e.target.closest('.btn-remove-cart')) {
      const btn = e.target.closest('.btn-remove-cart');
      const productoId = btn.getAttribute('data-id');
      btn.disabled = true;
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
        btn.disabled = false;
        if (data.success) {
          mostrarNotificacion('Producto eliminado del carrito', 'success');
          renderizarCarrito();
          actualizarCartCount();
        } else {
          mostrarNotificacion(data.message || 'No se pudo eliminar', 'error');
        }
      })
      .catch(() => {
        btn.disabled = false;
        mostrarNotificacion('Error al eliminar del carrito', 'error');
      });
    }
    // Aumentar cantidad
    if (e.target.closest('.btn-mas-cantidad')) {
      const btn = e.target.closest('.btn-mas-cantidad');
      const input = document.querySelector('.input-cantidad-carrito[data-id="' + btn.getAttribute('data-id') + '"]');
      let val = parseInt(input.value) || 1;
      cambiarCantidadCarrito(btn.getAttribute('data-id'), val + 1);
    }
    // Disminuir cantidad
    if (e.target.closest('.btn-menos-cantidad')) {
      const btn = e.target.closest('.btn-menos-cantidad');
      const input = document.querySelector('.input-cantidad-carrito[data-id="' + btn.getAttribute('data-id') + '"]');
      let val = parseInt(input.value) || 1;
      if (val > 1) cambiarCantidadCarrito(btn.getAttribute('data-id'), val - 1);
    }
  });
}

function mostrarNotificacion(msg, tipo) {
  let notif = document.createElement('div');
  notif.className = `fixed top-6 right-6 z-50 px-6 py-3 rounded shadow-lg text-white font-bold transition-all ${tipo === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
  notif.textContent = msg;
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 2000);
}

function actualizarCartCount() {
  fetch('/api/carrito')
    .then(res => res.json())
    .then(data => {
      const count = data.cantidad || 0;
      const badge = document.getElementById('cart-count');
      if (badge) {
        if (count > 0) {
          badge.textContent = count;
          badge.classList.remove('hidden');
        } else {
          badge.textContent = '';
          badge.classList.add('hidden');
        }
      }
    });
}

function renderizarCarrito() {
  fetch('/api/carrito')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('carrito-table-body');
      if (!tbody) return;
      if (!data.productos.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-gray-500">Tu carrito está vacío</td></tr>';
        document.getElementById('carrito-subtotal').textContent = 'S/ 0.00';
        document.getElementById('carrito-total').textContent = 'S/ 0.00';
        return;
      }
      let subtotal = 0;
      tbody.innerHTML = data.productos.map(prod => {
        subtotal += prod.subtotal;
        return `<tr>
          <td class="py-2 flex items-center gap-3">
            <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-12 h-12 object-contain rounded shadow">
            <span class="font-semibold">${prod.nombre}</span>
          </td>
          <td class="py-2">S/ ${prod.precio.toFixed(2)}</td>
          <td class="py-2">
            <div class="flex items-center gap-2">
              <button class="btn-menos-cantidad px-2 py-1 rounded bg-gray-200 text-lg font-bold" data-id="${prod.id}">-</button>
              <input type="number" class="input-cantidad-carrito w-12 text-center border rounded" value="${prod.cantidad}" min="1" data-id="${prod.id}">
              <button class="btn-mas-cantidad px-2 py-1 rounded bg-gray-200 text-lg font-bold" data-id="${prod.id}">+</button>
            </div>
          </td>
          <td class="py-2 font-bold">S/ ${prod.subtotal.toFixed(2)}</td>
          <td class="py-2 text-center">
            <button class="btn-remove-cart text-red-600 hover:text-red-800" data-id="${prod.id}">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>`;
      }).join('');
      document.getElementById('carrito-subtotal').textContent = `S/ ${subtotal.toFixed(2)}`;
      document.getElementById('carrito-total').textContent = `S/ ${subtotal.toFixed(2)}`;
    });
}

document.body.addEventListener('change', function(e) {
  if (e.target.classList.contains('input-cantidad-carrito')) {
    const input = e.target;
    let val = parseInt(input.value) || 1;
    if (val < 1) val = 1;
    cambiarCantidadCarrito(input.getAttribute('data-id'), val);
  }
});

function cambiarCantidadCarrito(productoId, cantidad) {
  fetch('/api/cambiar_cantidad_carrito', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ producto_id: productoId, cantidad: cantidad })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      renderizarCarrito();
      actualizarCartCount();
    } else {
      mostrarNotificacion(data.message || 'No se pudo cambiar cantidad', 'error');
    }
  })
  .catch(() => {
    mostrarNotificacion('Error al cambiar cantidad', 'error');
  });
}

function setupMiniCart() {
  const cartIcon = document.getElementById('cart-icon-link');
  const miniCart = document.getElementById('mini-cart');
  if (!cartIcon || !miniCart) return;

  // Mostrar mini-cart al pasar mouse o hacer clic
  let miniCartTimeout;
  function showMiniCart() {
    clearTimeout(miniCartTimeout);
    miniCart.classList.remove('hidden');
    renderMiniCart();
  }
  function hideMiniCart() {
    miniCartTimeout = setTimeout(() => miniCart.classList.add('hidden'), 200);
  }
  cartIcon.addEventListener('mouseenter', showMiniCart);
  cartIcon.addEventListener('mouseleave', hideMiniCart);
  miniCart.addEventListener('mouseenter', () => clearTimeout(miniCartTimeout));
  miniCart.addEventListener('mouseleave', hideMiniCart);
}

function renderMiniCart() {
  fetch('/api/carrito')
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('mini-cart-list');
      const total = document.getElementById('mini-cart-total');
      if (!list || !total) return;
      if (!data.productos.length) {
        list.innerHTML = '<div class="text-center text-gray-400 py-8">Tu carrito está vacío</div>';
        total.textContent = 'S/ 0.00';
        return;
      }
      let sum = 0;
      list.innerHTML = data.productos.map(prod => {
        sum += prod.subtotal;
        return `<div class="flex items-center gap-3 mb-3">
          <img src="/static/img/${prod.imagen}" alt="${prod.nombre}" class="w-12 h-12 object-contain rounded shadow">
          <div class="flex-1">
            <div class="font-semibold text-sm">${prod.nombre}</div>
            <div class="text-xs text-gray-500">x${prod.cantidad} • S/ ${prod.subtotal.toFixed(2)}</div>
          </div>
        </div>`;
      }).join('');
      total.textContent = `S/ ${sum.toFixed(2)}`;
    });
}

function setupCuponCarrito() {
  const cuponInput = document.getElementById('input-cupon');
  const aplicarBtn = document.getElementById('btn-aplicar-cupon');
  if (!cuponInput || !aplicarBtn) return;

  aplicarBtn.addEventListener('click', function() {
    const cupon = cuponInput.value.trim();
    if (!cupon) {
      mostrarNotificacion('Ingresa un código de cupón', 'error');
      return;
    }
    aplicarBtn.disabled = true;
    fetch('/api/aplicar_cupon', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ cupon })
    })
    .then(res => res.json())
    .then(data => {
      aplicarBtn.disabled = false;
      if (data.success) {
        mostrarNotificacion(data.message, 'success');
        // Actualizar descuento y total
        if (descuentoSpan) {
          descuentoSpan.textContent = `-S/ ${data.descuento.toFixed(2)}`;
        }
        document.getElementById('carrito-total').textContent = `S/ ${data.total.toFixed(2)}`;
        cuponInput.disabled = true;
        aplicarBtn.disabled = true;
      } else {
        mostrarNotificacion(data.message || 'Cupón inválido', 'error');
        if (data.message && data.message.includes('usaste')) {
          cuponInput.disabled = true;
          aplicarBtn.disabled = true;
        }
      }
    })
    .catch(() => {
      aplicarBtn.disabled = false;
      mostrarNotificacion('Error al aplicar cupón', 'error');
    });
  });
}

function setupEnvioCarrito() {
  const calcularBtn = document.querySelector('button.border-black');
  if (!calcularBtn) return;
  let envioContainer = document.getElementById('envio-opciones');
  if (!envioContainer) {
    envioContainer = document.createElement('div');
    envioContainer.id = 'envio-opciones';
    calcularBtn.parentElement.appendChild(envioContainer);
  }
  calcularBtn.addEventListener('click', function() {
    calcularBtn.disabled = true;
    fetch('/api/calcular_envio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.json())
    .then(data => {
      calcularBtn.disabled = false;
      if (!data.success) {
        mostrarNotificacion(data.message || 'No se pudo calcular el envío', 'error');
        return;
      }
      // Mostrar opciones
      envioContainer.innerHTML = '<div class="mt-4 mb-2 font-semibold">Selecciona una opción de envío:</div>' +
        data.opciones.map(opt => `
          <label class="flex items-center gap-2 mb-2 cursor-pointer">
            <input type="radio" name="opcion-envio" value="${opt.codigo}" data-precio="${opt.precio}" class="accent-green-600" />
            <span>${opt.nombre} <span class="text-xs text-gray-500">(${opt.descripcion})</span> <span class="font-bold">S/ ${opt.precio.toFixed(2)}</span></span>
          </label>
        `).join('');
      // Evento para seleccionar opción
      envioContainer.querySelectorAll('input[name="opcion-envio"]').forEach(radio => {
        radio.addEventListener('change', function() {
          const precioEnvio = parseFloat(this.getAttribute('data-precio'));
          // Actualizar resumen
          let envioResumen = document.getElementById('carrito-envio');
          if (!envioResumen) {
            const totalDiv = document.getElementById('carrito-total').parentElement;
            envioResumen = document.createElement('div');
            envioResumen.className = 'flex justify-between text-sm mb-2';
            envioResumen.innerHTML = '<span>Envío</span><span id="carrito-envio">S/ 0.00</span>';
            totalDiv.parentElement.insertBefore(envioResumen, totalDiv);
          }
          envioResumen.querySelector('#carrito-envio').textContent = `S/ ${precioEnvio.toFixed(2)}`;
          // Actualizar total final
          const subtotal = parseFloat(document.getElementById('carrito-subtotal').textContent.replace('S/', '').replace(',', '.') || 0);
          let descuento = 0;
          document.querySelectorAll('div.flex.justify-between.text-sm.mb-2 span').forEach(span => {
            if (span.textContent.includes('Descuento')) {
              descuento = parseFloat(span.nextElementSibling.textContent.replace('-S/', '').replace(',', '.') || 0);
            }
          });
          const totalFinal = subtotal - descuento + precioEnvio;
          document.getElementById('carrito-total').textContent = `S/ ${totalFinal.toFixed(2)}`;
        });
      });
    })
    .catch(() => {
      calcularBtn.disabled = false;
      mostrarNotificacion('Error al calcular envío', 'error');
    });
  });
}

// Aquí puedes agregar animaciones para el catálogo por categoría 