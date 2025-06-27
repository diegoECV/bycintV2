// Espera a que el DOM esté listo
function ready(fn) {
  if (document.readyState !== 'loading') fn();
  else document.addEventListener('DOMContentLoaded', fn);
}

ready(function() {
  // Botón para abrir el modal (debe estar en tu página de carrito)
  const openBtn = document.getElementById('open-payment-modal');
  const overlay = document.getElementById('payment-modal-overlay');
  const closeBtn = document.getElementById('close-payment-modal');

  // Modales secundarios
  const yapeModal = document.getElementById('yape-modal');
  const receiptModal = document.getElementById('receipt-modal');
  const closeYapeBtns = document.querySelectorAll('.close-yape');
  const closeReceiptBtns = document.querySelectorAll('.close-receipt');

  // Formulario y campos
  const paymentMethodSelect = document.getElementById('payment-method');
  const cardDetailsSection = document.getElementById('card-details');
  const cardNumberLabel = document.getElementById('card-number-label');
  const cardNumberInput = document.getElementById('card-number');
  const expiryMonth = document.getElementById('expiry-month');
  const expiryYear = document.getElementById('expiry-year');
  const securityCode = document.getElementById('security-code');
  const paymentOptions = document.querySelectorAll('input[name="payment-option"]');
  const placeOrderButton = document.getElementById('place-order');
  const termsCheckbox = document.getElementById('terms');

  // Yape
  const yapeConfirmButton = document.getElementById('yape-confirm');
  const paymentScreenshotInput = document.getElementById('payment-screenshot');
  const imagePreviewDiv = document.getElementById('image-preview');
  const yapeNumber = '999-888-777';

  // Recibo
  const printReceiptButton = document.getElementById('print-receipt');

  // Productos de ejemplo (en producción, pásalos desde Flask)
  const products = window.products || [];

  // --- Abrir/Cerrar modal principal ---
  if (openBtn) {
    openBtn.addEventListener('click', () => {
      // Copiar valores del carrito al modal de pago
      const carritoSubtotal = document.getElementById('carrito-subtotal');
      const carritoTotal = document.getElementById('carrito-total');
      let carritoDescuento = null;
      let carritoEnvio = document.getElementById('carrito-envio');
      document.querySelectorAll('div.flex.justify-between.text-sm.mb-2 span').forEach(span => {
        if (span.textContent.includes('Descuento')) {
          carritoDescuento = span.nextElementSibling;
        }
      });
      // Subtotal
      if (carritoSubtotal && document.getElementById('subtotal')) {
        document.getElementById('subtotal').textContent = carritoSubtotal.textContent;
      }
      // Descuento
      if (carritoDescuento && document.getElementById('descuento')) {
        document.getElementById('descuento').textContent = carritoDescuento.textContent;
      }
      // Envío
      if (carritoEnvio && document.getElementById('envio')) {
        document.getElementById('envio').textContent = carritoEnvio.textContent;
      } else if (document.getElementById('envio')) {
        document.getElementById('envio').textContent = 'S/ 0.00';
      }
      // Total
      if (carritoTotal && document.getElementById('total')) {
        document.getElementById('total').textContent = carritoTotal.textContent;
      }
      overlay.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      loadProducts();
      // Asegura que el monto de Yape sea igual al total final
      document.getElementById('yape-amount').textContent = document.getElementById('total').textContent;
    });
  }
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) closeModal();
  });
  function closeModal() {
    overlay.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }

  // --- Abrir/Cerrar modal Yape ---
  paymentOptions.forEach(option => {
    option.addEventListener('change', function() {
      if (this.value === 'yape') {
        paymentMethodSelect.value = 'yape';
        updatePaymentFields();
      } else if (paymentMethodSelect.value === 'yape') {
        paymentMethodSelect.value = this.value === 'credit-card' ? 'visa' : 'bcp';
        updatePaymentFields();
      }
    });
  });
  paymentMethodSelect.addEventListener('change', function() {
    updatePaymentFields();
    if (this.value === 'yape') {
      document.querySelector('input[value="yape"]').checked = true;
    } else {
      document.querySelector('input[value="credit-card"]').checked = true;
    }
  });
  function updatePaymentFields() {
    if (paymentMethodSelect.value === 'yape') {
      cardNumberLabel.textContent = 'Número celular';
      cardNumberInput.maxLength = 9;
      cardNumberInput.value = '';
      expiryMonth.parentElement.parentElement.style.display = 'none';
      securityCode.parentElement.style.display = 'none';
    } else {
      cardNumberLabel.textContent = 'Número de Tarjeta';
      cardNumberInput.maxLength = 19;
      cardNumberInput.value = '';
      expiryMonth.parentElement.parentElement.style.display = '';
      securityCode.parentElement.style.display = '';
    }
  }

  // --- Validación y envío ---
  placeOrderButton.addEventListener('click', function(e) {
    e.preventDefault();
    const selectedPaymentOption = document.querySelector('input[name="payment-option"]:checked').value;
    if (selectedPaymentOption === 'yape') {
      showYapeModal();
      return;
    }
    if (validateForm()) {
      showReceipt();
    }
  });

  // --- Yape Modal ---
  function showYapeModal() {
    generateYapeQR();
    document.getElementById('yape-number').textContent = yapeNumber;
    // Siempre toma el total final mostrado en el resumen
    document.getElementById('yape-amount').textContent = document.getElementById('total').textContent;
    paymentScreenshotInput.value = '';
    imagePreviewDiv.innerHTML = '';
    yapeModal.classList.remove('hidden');
  }
  closeYapeBtns.forEach(btn => btn.addEventListener('click', () => yapeModal.classList.add('hidden')));
  yapeModal.addEventListener('click', function(e) {
    if (e.target === yapeModal) yapeModal.classList.add('hidden');
  });
  paymentScreenshotInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        imagePreviewDiv.innerHTML = `<img src="${e.target.result}" alt="Vista previa" class="max-h-40 mx-auto" />`;
      };
      reader.readAsDataURL(file);
    } else {
      imagePreviewDiv.innerHTML = '';
    }
  });
  yapeConfirmButton.addEventListener('click', function() {
    if (!paymentScreenshotInput.files || paymentScreenshotInput.files.length === 0) {
      alert('Por favor, sube una captura de tu pago con Yape');
      return;
    }
    yapeModal.classList.add('hidden');
    if (validateForm()) {
      showReceipt();
    }
  });

  // --- Recibo Modal ---
  function showReceipt() {
    // Datos del formulario
    const formData = {
      firstName: document.getElementById('first-name').value,
      lastName: document.getElementById('last-name').value,
      email: document.getElementById('email').value || 'admin@gmail.com',
      phone: document.getElementById('phone-prefix').value + ' ' + document.getElementById('phone').value,
      address: document.getElementById('address').value || 'Producto',
      country: document.getElementById('country').value || 'Perú',
      region: document.getElementById('region').value || 'Producto',
      city: document.getElementById('city').value || 'Producto',
      paymentMethod: document.querySelector('input[name="payment-option"]:checked').value,
      total: document.getElementById('total').textContent,
      subtotal: document.getElementById('subtotal').textContent
    };
    // Número de pedido aleatorio
    const orderNumber = Math.floor(1000 + Math.random() * 9000);
    // Fecha
    const now = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = now.toLocaleDateString('es-ES', options);
    // Actualizar recibo
    document.getElementById('receipt-order-number').textContent = orderNumber;
    document.getElementById('receipt-date').textContent = formattedDate;
    document.getElementById('receipt-email').textContent = formData.email;
    document.getElementById('receipt-total').textContent = formData.total;
    document.getElementById('receipt-payment-method').textContent = getPaymentMethodName(formData.paymentMethod);
    // Productos
    let productNames = '';
    products.forEach(product => {
      productNames += product.name + ', ';
    });
    productNames = productNames.slice(0, -2);
    document.getElementById('receipt-product-name').textContent = productNames;
    document.getElementById('receipt-subtotal').textContent = formData.subtotal;
    // Copiar descuento al recibo
    if (document.getElementById('descuento') && document.getElementById('receipt-descuento')) {
      document.getElementById('receipt-descuento').textContent = document.getElementById('descuento').textContent;
    }
    // Copiar envío al recibo
    if (document.getElementById('envio') && document.getElementById('receipt-envio')) {
      document.getElementById('receipt-envio').textContent = document.getElementById('envio').textContent;
    }
    document.getElementById('receipt-total-detail').textContent = formData.total;
    document.getElementById('receipt-billing-address').textContent = `${formData.address}, ${formData.city}, ${formData.region}, ${formData.country}`;
    document.getElementById('receipt-phone').textContent = formData.phone;
    fetch('/api/guardar_pedido', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        total: formData.total.replace('S/', '').replace(',', '.'),
        products: products
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        document.getElementById('receipt-order-number').textContent = data.pedido_id;
        // Vaciar el carrito (window.products) tras el pago exitoso
        window.products = [];
        // Actualizar el resumen del modal de pago
        loadProducts();
        calculateTotals();
      }
    });
    receiptModal.classList.remove('hidden');
  }
  closeReceiptBtns.forEach(btn => btn.addEventListener('click', () => receiptModal.classList.add('hidden')));
  receiptModal.addEventListener('click', function(e) {
    if (e.target === receiptModal) receiptModal.classList.add('hidden');
  });
  if (printReceiptButton) {
    printReceiptButton.addEventListener('click', function() {
      window.print();
    });
  }

  // --- Productos y totales ---
  function loadProducts() {
    const productList = document.getElementById('product-list');
    productList.innerHTML = '';
    if (products.length === 0) {
      productList.innerHTML = '<div class="text-center text-gray-400">No hay productos</div>';
    } else {
      products.forEach(product => {
        const cantidad = product.cantidad || 1;
        const div = document.createElement('div');
        div.className = 'flex justify-between border-b py-1';
        div.innerHTML = `<span>${product.name} x${cantidad}</span><span>S/${(product.price * cantidad).toFixed(2)}</span>`;
        productList.appendChild(div);
      });
    }
  }
  function calculateTotals() {
    const subtotal = products.reduce((sum, product) => sum + product.price * (product.cantidad || 1), 0);
    const total = subtotal;
    document.getElementById('subtotal').textContent = `S/${subtotal.toFixed(2)}`;
    document.getElementById('total').textContent = `S/${total.toFixed(2)}`;
    document.getElementById('yape-amount').textContent = `S/${total.toFixed(2)}`;
  }

  // --- QR para Yape ---
  function generateYapeQR() {
    const totalAmount = document.getElementById('total').textContent;
    const qrContent = `YAPE: ${yapeNumber} - Monto: ${totalAmount}`;
    const qrContainer = document.getElementById('yape-qr');
    qrContainer.innerHTML = '';
    if (window.qrcode) {
      const qr = window.qrcode(0, 'M');
      qr.addData(qrContent);
      qr.make();
      qrContainer.innerHTML = qr.createImgTag(5);
    }
  }

  // --- Validación ---
  function validateForm() {
    let isValid = true;
    // Eliminar errores previos
    document.querySelectorAll('.error-message').forEach(e => e.remove());
    document.querySelectorAll('.border-red-500').forEach(e => e.classList.remove('border-red-500'));
    const selectedPaymentOption = document.querySelector('input[name="payment-option"]:checked').value;
    if (selectedPaymentOption === 'credit-card') {
      if (!cardNumberInput.value.trim() || cardNumberInput.value.replace(/\s/g, '').length < 16) {
        showValidationError(cardNumberInput, 'Ingrese un número de tarjeta válido');
        isValid = false;
      }
      if (expiryMonth.value === '' || expiryYear.value === '') {
        showValidationError(expiryMonth, 'Seleccione una fecha de caducidad válida');
        isValid = false;
      }
      if (!securityCode.value.trim() || securityCode.value.length < 3) {
        showValidationError(securityCode, 'Ingrese un código de seguridad válido');
        isValid = false;
      }
    } else if (selectedPaymentOption === 'yape') {
      if (!cardNumberInput.value.trim() || cardNumberInput.value.length !== 9 || !/^\d+$/.test(cardNumberInput.value)) {
        showValidationError(cardNumberInput, 'Ingrese un número celular válido (9 dígitos)');
        isValid = false;
      }
    }
    // Facturación
    const requiredFields = [
      { id: 'first-name', message: 'Ingrese su nombre' },
      { id: 'last-name', message: 'Ingrese su apellido' },
      { id: 'id-document', message: 'Ingrese su documento de identidad' },
      { id: 'phone', message: 'Ingrese su número de teléfono' }
    ];
    requiredFields.forEach(field => {
      const el = document.getElementById(field.id);
      if (!el.value.trim()) {
        showValidationError(el, field.message);
        isValid = false;
      }
    });
    // Email
    const email = document.getElementById('email');
    if (email.value.trim() && !isValidEmail(email.value)) {
      showValidationError(email, 'Ingrese un correo electrónico válido');
      isValid = false;
    }
    // Términos
    if (!termsCheckbox.checked) {
      showValidationError(termsCheckbox, 'Debe aceptar los términos y condiciones');
      isValid = false;
    }
    return isValid;
  }
  function showValidationError(element, message) {
    element.classList.add('border-red-500');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message text-xs text-red-500 mt-1';
    errorDiv.textContent = message;
    if (element.type === 'checkbox') {
      element.parentElement.appendChild(errorDiv);
    } else {
      element.parentElement.appendChild(errorDiv);
    }
    element.addEventListener('input', function handler() {
      element.classList.remove('border-red-500');
      const err = element.parentElement.querySelector('.error-message');
      if (err) err.remove();
      element.removeEventListener('input', handler);
    });
  }
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  function getPaymentMethodName(method) {
    switch(method) {
      case 'credit-card': return 'Tarjeta de crédito/débito';
      case 'bank-transfer': return 'Transferencia bancaria';
      case 'yape': return 'Pago Off Yape';
      default: return 'Desconocido';
    }
  }

  // --- Formato de número de tarjeta ---
  cardNumberInput.addEventListener('input', function() {
    if (paymentMethodSelect.value === 'yape') return;
    let value = this.value.replace(/\D/g, '');
    if (value.length > 0) value = value.match(/.{1,4}/g).join(' ');
    this.value = value;
  });
}); 