// profile.js - Funcionalidad AJAX para perfil, avatar y boletín

// Toast visual
function mostrarToast(mensaje, tipo = 'success') {
  let toast = document.getElementById('toast-msg');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast-msg';
    toast.style.position = 'fixed';
    toast.style.bottom = '32px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.background = tipo === 'success' ? '#22c55e' : '#ef4444';
    toast.style.color = 'white';
    toast.style.padding = '16px 32px';
    toast.style.borderRadius = '9999px';
    toast.style.fontWeight = 'bold';
    toast.style.fontSize = '1rem';
    toast.style.boxShadow = '0 2px 16px rgba(0,0,0,0.12)';
    toast.style.zIndex = '9999';
    toast.style.cursor = 'pointer';
    toast.addEventListener('click', () => toast.style.display = 'none');
    document.body.appendChild(toast);
  }
  toast.textContent = mensaje;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
  // Guardar cambios de perfil
  const formPerfil = document.querySelector('form[action="/profile"]');
  if (formPerfil) {
    formPerfil.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch('/profile', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        mostrarToast(data.message, data.success ? 'success' : 'error');
      })
      .catch(() => mostrarToast('Error al actualizar perfil', 'error'));
    });
  }

  // Cambiar avatar
  const avatarInput = document.getElementById('avatar-upload');
  if (avatarInput) {
    avatarInput.addEventListener('change', function() {
      if (!this.files.length) return;
      const formData = new FormData();
      formData.append('avatar', this.files[0]);
      fetch('/profile/avatar', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          document.querySelector('img[alt="Avatar"]').src = data.avatar_url + '?t=' + Date.now();
          mostrarToast(data.message, 'success');
        } else {
          mostrarToast(data.message, 'error');
        }
      })
      .catch(() => mostrarToast('Error al actualizar avatar', 'error'));
    });
  }

  // Actualizar preferencia de boletín
  const formBoletin = document.querySelector('form[action="/profile/boletin"]');
  if (formBoletin) {
    formBoletin.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch('/profile/boletin', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        mostrarToast(data.message, data.success ? 'success' : 'error');
      })
      .catch(() => mostrarToast('Error al actualizar preferencia', 'error'));
    });
  }

  // Cambiar contraseña
  const formPass = document.querySelector('form[action="/profile/cambiar_contrasena"]');
  if (formPass) {
    formPass.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch('/profile/cambiar_contrasena', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        mostrarToast(data.message, data.success ? 'success' : 'error');
        if (data.success) {
          formPass.reset();
        }
      })
      .catch(() => mostrarToast('Error al cambiar contraseña', 'error'));
    });
  }

  // --- Tarjetas de crédito ---
  const tarjetasSection = document.getElementById('tarjetas-section');
  if (tarjetasSection) {
    const lista = document.createElement('div');
    lista.className = 'w-full flex flex-col gap-4 mb-4';
    tarjetasSection.insertBefore(lista, tarjetasSection.querySelector('button'));

    function validarTarjeta(data) {
      // Validar número: 16 dígitos
      if (!/^\d{16}$/.test(data.numero.replace(/\s+/g, ''))) {
        mostrarToast('El número de tarjeta debe tener 16 dígitos.', 'error');
        return false;
      }
      // Validar vencimiento: MM/AAAA
      if (!/^\d{2}\/\d{4}$/.test(data.vencimiento)) {
        mostrarToast('El vencimiento debe tener formato MM/AAAA.', 'error');
        return false;
      }
      // Validar CVV: 3 o 4 dígitos
      if (!/^\d{3,4}$/.test(data.cvv)) {
        mostrarToast('El CVV debe tener 3 o 4 dígitos.', 'error');
        return false;
      }
      return true;
    }

    function renderTarjetas(tarjetas) {
      lista.innerHTML = '';
      if (!tarjetas.length) {
        lista.innerHTML = '<div class="border rounded-lg p-6 bg-gray-50 text-gray-500 italic">(Aquí aparecerán las tarjetas guardadas del usuario. Puedes agregar, editar o eliminar tarjetas.)</div>';
        return;
      }
      tarjetas.forEach(t => {
        const card = document.createElement('div');
        card.className = 'flex items-center justify-between bg-white border rounded-lg px-4 py-3 shadow';
        card.innerHTML = `
          <div>
            <div class="font-semibold">${t.titular}</div>
            <div class="text-sm text-gray-600">${t.numero} <span class="ml-2">${t.marca || ''}</span></div>
            <div class="text-xs text-gray-400">Vence: ${t.vencimiento}</div>
          </div>
          <div class="flex gap-2">
            <button class="text-blue-500 hover:text-blue-700 font-bold btn-edit-tarjeta" data-id="${t.id}"><i class="fa-solid fa-pen"></i></button>
            <button class="text-red-500 hover:text-red-700 font-bold btn-del-tarjeta" data-id="${t.id}"><i class="fa-solid fa-trash"></i></button>
          </div>
        `;
        lista.appendChild(card);
      });
    }

    function cargarTarjetas() {
      fetch('/profile/tarjetas')
        .then(res => res.json())
        .then(data => renderTarjetas(data.tarjetas || []));
    }
    cargarTarjetas();

    // Eliminar tarjeta
    lista.addEventListener('click', function(e) {
      if (e.target.closest('.btn-del-tarjeta')) {
        const btn = e.target.closest('.btn-del-tarjeta');
        const id = btn.getAttribute('data-id');
        if (confirm('¿Eliminar esta tarjeta?')) {
          fetch(`/profile/tarjetas/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
              mostrarToast(data.message, data.success ? 'success' : 'error');
              if (data.success) cargarTarjetas();
            });
        }
      }
    });

    // --- Validaciones en tiempo real para formularios de tarjeta ---
    function addRealtimeValidation(form) {
      const numInput = form.querySelector('input[name="numero"]');
      const vencInput = form.querySelector('input[name="vencimiento"]');
      const cvvInput = form.querySelector('input[name="cvv"]');
      const btn = form.querySelector('button[type="submit"]');
      // Mensajes de error
      let numErr = document.createElement('div');
      numErr.className = 'text-xs text-red-500 mt-1';
      numInput.after(numErr);
      let vencErr = document.createElement('div');
      vencErr.className = 'text-xs text-red-500 mt-1';
      vencInput.after(vencErr);
      let cvvErr = document.createElement('div');
      cvvErr.className = 'text-xs text-red-500 mt-1';
      cvvInput.after(cvvErr);
      function check() {
        let valid = true;
        // Número
        let numVal = numInput.value.replace(/\s+/g, '');
        if (!/^\d{16}$/.test(numVal)) {
          numErr.textContent = 'Debe tener 16 dígitos.';
          valid = false;
        } else {
          numErr.textContent = '';
        }
        // Vencimiento
        if (!/^\d{2}\/\d{4}$/.test(vencInput.value)) {
          vencErr.textContent = 'Formato: MM/AAAA';
          valid = false;
        } else {
          vencErr.textContent = '';
        }
        // CVV
        if (!/^\d{3,4}$/.test(cvvInput.value)) {
          cvvErr.textContent = 'Debe tener 3 o 4 dígitos.';
          valid = false;
        } else {
          cvvErr.textContent = '';
        }
        btn.disabled = !valid;
      }
      [numInput, vencInput, cvvInput].forEach(inp => inp.addEventListener('input', check));
      check();
    }

    // Modificar modal de agregar tarjeta
    const btnAdd = tarjetasSection.querySelector('button');
    btnAdd.addEventListener('click', function() {
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50';
      modal.innerHTML = `
        <div class="bg-white rounded-lg p-8 shadow-lg w-full max-w-sm relative">
          <button class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl" id="cerrar-modal-tarjeta">&times;</button>
          <h3 class="font-bold mb-4 text-lg">Agregar tarjeta</h3>
          <form id="form-tarjeta" class="flex flex-col gap-4">
            <input type="text" name="titular" placeholder="Titular" class="border rounded px-3 py-2" required>
            <input type="text" name="numero" placeholder="Número de tarjeta" maxlength="19" class="border rounded px-3 py-2" required>
            <input type="text" name="vencimiento" placeholder="MM/AAAA" maxlength="7" class="border rounded px-3 py-2" required>
            <input type="text" name="cvv" placeholder="CVV" maxlength="5" class="border rounded px-3 py-2" required>
            <input type="text" name="marca" placeholder="Marca (Visa, MasterCard...)" class="border rounded px-3 py-2">
            <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-semibold">Guardar</button>
          </form>
        </div>
      `;
      document.body.appendChild(modal);
      modal.querySelector('#cerrar-modal-tarjeta').onclick = () => modal.remove();
      const form = modal.querySelector('#form-tarjeta');
      addRealtimeValidation(form);
      form.onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        fetch('/profile/tarjetas', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
          mostrarToast(data.message, data.success ? 'success' : 'error');
          if (data.success) {
            modal.remove();
            cargarTarjetas();
          }
        });
      };
    });

    // Modificar modal de editar tarjeta para usar validación en tiempo real
    lista.addEventListener('click', function(e) {
      if (e.target.closest('.btn-edit-tarjeta')) {
        const btn = e.target.closest('.btn-edit-tarjeta');
        const id = btn.getAttribute('data-id');
        const card = btn.closest('div');
        const titular = card.querySelector('.font-semibold').textContent;
        const numero = card.querySelector('.text-sm').textContent.replace(/\D/g, '');
        const vencimiento = card.querySelector('.text-xs').textContent.replace('Vence: ', '').trim();
        const marca = card.querySelector('.text-sm span').textContent.trim();
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50';
        modal.innerHTML = `
          <div class="bg-white rounded-lg p-8 shadow-lg w-full max-w-sm relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl" id="cerrar-modal-tarjeta">&times;</button>
            <h3 class="font-bold mb-4 text-lg">Editar tarjeta</h3>
            <form id="form-tarjeta-edit" class="flex flex-col gap-4">
              <input type="text" name="titular" placeholder="Titular" class="border rounded px-3 py-2" required value="${titular}">
              <input type="text" name="numero" placeholder="Número de tarjeta" maxlength="19" class="border rounded px-3 py-2" required value="${numero}">
              <input type="text" name="vencimiento" placeholder="MM/AAAA" maxlength="7" class="border rounded px-3 py-2" required value="${vencimiento}">
              <input type="text" name="cvv" placeholder="CVV" maxlength="5" class="border rounded px-3 py-2" required>
              <input type="text" name="marca" placeholder="Marca (Visa, MasterCard...)" class="border rounded px-3 py-2" value="${marca}">
              <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-semibold">Guardar cambios</button>
            </form>
          </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('#cerrar-modal-tarjeta').onclick = () => modal.remove();
        const form = modal.querySelector('#form-tarjeta-edit');
        addRealtimeValidation(form);
        form.onsubmit = function(ev) {
          ev.preventDefault();
          const formData = new FormData(this);
          const data = Object.fromEntries(formData.entries());
          if (!validarTarjeta(data)) return;
          fetch(`/profile/tarjetas/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(res => res.json())
          .then(data => {
            mostrarToast(data.message, data.success ? 'success' : 'error');
            if (data.success) {
              modal.remove();
              cargarTarjetas();
            }
          });
        };
      }
    });
  }

  // --- Direcciones ---
  const direccionesSection = document.getElementById('direcciones-section');
  if (direccionesSection) {
    const lista = document.createElement('div');
    lista.className = 'w-full flex flex-col gap-4 mb-4';
    direccionesSection.insertBefore(lista, direccionesSection.querySelector('button'));

    function renderDirecciones(direcciones) {
      lista.innerHTML = '';
      if (!direcciones.length) {
        lista.innerHTML = '<div class="border rounded-lg p-6 bg-gray-50 text-gray-500 italic">(Aquí aparecerán las direcciones guardadas del usuario. Puedes agregar, editar o eliminar direcciones.)</div>';
        return;
      }
      direcciones.forEach(d => {
        const card = document.createElement('div');
        card.className = 'flex items-center justify-between bg-white border rounded-lg px-4 py-3 shadow';
        card.innerHTML = `
          <div>
            <div class="font-semibold">${d.nombre}</div>
            <div class="text-sm text-gray-600">${d.direccion}, ${d.ciudad}${d.departamento ? ', ' + d.departamento : ''}, ${d.pais}</div>
            <div class="text-xs text-gray-400">${d.tipo === 'facturacion' ? 'Facturación' : 'Envío'} | Tel: ${d.telefono}${d.codigo_postal ? ' | CP: ' + d.codigo_postal : ''}</div>
          </div>
          <div class="flex gap-2">
            <button class="text-blue-500 hover:text-blue-700 font-bold btn-edit-direccion" data-id="${d.id}"><i class="fa-solid fa-pen"></i></button>
            <button class="text-red-500 hover:text-red-700 font-bold btn-del-direccion" data-id="${d.id}"><i class="fa-solid fa-trash"></i></button>
          </div>
        `;
        lista.appendChild(card);
      });
    }

    function cargarDirecciones() {
      fetch('/profile/direcciones')
        .then(res => res.json())
        .then(data => renderDirecciones(data.direcciones || []));
    }
    cargarDirecciones();

    // Eliminar dirección
    lista.addEventListener('click', function(e) {
      if (e.target.closest('.btn-del-direccion')) {
        const btn = e.target.closest('.btn-del-direccion');
        const id = btn.getAttribute('data-id');
        if (confirm('¿Eliminar esta dirección?')) {
          fetch(`/profile/direcciones/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
              mostrarToast(data.message, data.success ? 'success' : 'error');
              if (data.success) cargarDirecciones();
            });
        }
      }
    });

    // Validación en tiempo real para direcciones
    function addDireccionValidation(form) {
      const campos = ['nombre', 'direccion', 'ciudad', 'pais', 'telefono'];
      let errores = {};
      campos.forEach(c => {
        const inp = form.querySelector(`[name="${c}"]`);
        let err = document.createElement('div');
        err.className = 'text-xs text-red-500 mt-1';
        inp.after(err);
        errores[c] = err;
        inp.addEventListener('input', () => check());
      });
      const btn = form.querySelector('button[type="submit"]');
      function check() {
        let valid = true;
        campos.forEach(c => {
          const inp = form.querySelector(`[name="${c}"]`);
          if (!inp.value.trim()) {
            errores[c].textContent = 'Obligatorio';
            valid = false;
          } else {
            errores[c].textContent = '';
          }
        });
        btn.disabled = !valid;
      }
      check();
    }

    // Agregar dirección
    const btnAdd = direccionesSection.querySelector('button');
    btnAdd.addEventListener('click', function() {
      const modal = document.createElement('div');
      modal.className = 'fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50';
      modal.innerHTML = `
        <div class="bg-white rounded-lg p-8 shadow-lg w-full max-w-sm relative">
          <button class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl" id="cerrar-modal-direccion">&times;</button>
          <h3 class="font-bold mb-4 text-lg">Agregar dirección</h3>
          <form id="form-direccion" class="flex flex-col gap-4">
            <input type="text" name="nombre" placeholder="Nombre de la dirección (ej: Casa, Oficina)" class="border rounded px-3 py-2" required>
            <input type="text" name="direccion" placeholder="Dirección" class="border rounded px-3 py-2" required>
            <input type="text" name="ciudad" placeholder="Ciudad" class="border rounded px-3 py-2" required>
            <input type="text" name="departamento" placeholder="Departamento/Estado" class="border rounded px-3 py-2">
            <input type="text" name="pais" placeholder="País" class="border rounded px-3 py-2" required>
            <input type="text" name="codigo_postal" placeholder="Código postal" class="border rounded px-3 py-2">
            <input type="text" name="telefono" placeholder="Teléfono" class="border rounded px-3 py-2" required>
            <select name="tipo" class="border rounded px-3 py-2">
              <option value="envio">Envío</option>
              <option value="facturacion">Facturación</option>
            </select>
            <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-semibold">Guardar</button>
          </form>
        </div>
      `;
      document.body.appendChild(modal);
      modal.querySelector('#cerrar-modal-direccion').onclick = () => modal.remove();
      const form = modal.querySelector('#form-direccion');
      addDireccionValidation(form);
      form.onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        fetch('/profile/direcciones', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(data => {
          mostrarToast(data.message, data.success ? 'success' : 'error');
          if (data.success) {
            modal.remove();
            cargarDirecciones();
          }
        });
      };
    });

    // Editar dirección
    lista.addEventListener('click', function(e) {
      if (e.target.closest('.btn-edit-direccion')) {
        const btn = e.target.closest('.btn-edit-direccion');
        const id = btn.getAttribute('data-id');
        const card = btn.closest('div');
        const nombre = card.querySelector('.font-semibold').textContent;
        const datos = card.querySelectorAll('.text-sm, .text-xs');
        const direccion = datos[0].textContent.split(',')[0].trim();
        const ciudad = datos[0].textContent.split(',')[1]?.trim() || '';
        const departamento = datos[0].textContent.split(',')[2]?.trim() || '';
        const pais = datos[0].textContent.split(',')[3]?.trim() || '';
        const tipo = datos[1].textContent.includes('Facturación') ? 'facturacion' : 'envio';
        const telefono = datos[1].textContent.split('Tel: ')[1]?.split(' |')[0] || '';
        const codigo_postal = datos[1].textContent.split('CP: ')[1] || '';
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50';
        modal.innerHTML = `
          <div class="bg-white rounded-lg p-8 shadow-lg w-full max-w-sm relative">
            <button class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl" id="cerrar-modal-direccion">&times;</button>
            <h3 class="font-bold mb-4 text-lg">Editar dirección</h3>
            <form id="form-direccion-edit" class="flex flex-col gap-4">
              <input type="text" name="nombre" placeholder="Nombre de la dirección (ej: Casa, Oficina)" class="border rounded px-3 py-2" required value="${nombre}">
              <input type="text" name="direccion" placeholder="Dirección" class="border rounded px-3 py-2" required value="${direccion}">
              <input type="text" name="ciudad" placeholder="Ciudad" class="border rounded px-3 py-2" required value="${ciudad}">
              <input type="text" name="departamento" placeholder="Departamento/Estado" class="border rounded px-3 py-2" value="${departamento}">
              <input type="text" name="pais" placeholder="País" class="border rounded px-3 py-2" required value="${pais}">
              <input type="text" name="codigo_postal" placeholder="Código postal" class="border rounded px-3 py-2" value="${codigo_postal}">
              <input type="text" name="telefono" placeholder="Teléfono" class="border rounded px-3 py-2" required value="${telefono}">
              <select name="tipo" class="border rounded px-3 py-2">
                <option value="envio" ${tipo === 'envio' ? 'selected' : ''}>Envío</option>
                <option value="facturacion" ${tipo === 'facturacion' ? 'selected' : ''}>Facturación</option>
              </select>
              <button type="submit" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-semibold">Guardar cambios</button>
            </form>
          </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('#cerrar-modal-direccion').onclick = () => modal.remove();
        const form = modal.querySelector('#form-direccion-edit');
        addDireccionValidation(form);
        form.onsubmit = function(ev) {
          ev.preventDefault();
          const formData = new FormData(this);
          const data = Object.fromEntries(formData.entries());
          fetch(`/profile/direcciones/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(res => res.json())
          .then(data => {
            mostrarToast(data.message, data.success ? 'success' : 'error');
            if (data.success) {
              modal.remove();
              cargarDirecciones();
            }
          });
        };
      }
    });
  }

  // Navegación de secciones en el perfil
  const navLinks = document.querySelectorAll('aside nav a, aside nav button');
  const sections = {
    'Perfil': document.getElementById('perfil-section'),
    'Direcciones': document.getElementById('direcciones-section'),
    'Tarjetas de crédito': document.getElementById('tarjetas-section'),
    'Autenticación': document.getElementById('autenticacion-section')
  };
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      if (this.textContent.trim() === 'Salir') {
        e.preventDefault();
        window.location.href = '/';
        return;
      }
      e.preventDefault();
      Object.values(sections).forEach(sec => sec.classList.add('hidden'));
      const section = sections[this.textContent.trim()];
      if (section) section.classList.remove('hidden');
      navLinks.forEach(l => l.classList.remove('bg-red-50', 'font-semibold', 'text-red-700', 'border-l-4', 'border-red-500'));
      this.classList.add('bg-red-50', 'font-semibold', 'text-red-700', 'border-l-4', 'border-red-500');
    });
  });
}); 