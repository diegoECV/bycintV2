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
    
    if (!termsCheckbox.checked) {
      alert('Debes aceptar los términos y condiciones');
      return;
    }
    
    if (selectedPaymentOption === 'yape') {
      showYapeModal();
      return;
    } else if (selectedPaymentOption === 'credit-card') {
      // Procesar pago con PayPal o Stripe
      procesarPagoTarjeta();
      return;
    }
    
    if (validateForm()) {
      showReceipt();
    }
  });

  // --- Procesar pago con tarjeta (PayPal/Stripe) ---
  async function procesarPagoTarjeta() {
    try {
      // Obtener datos del carrito
      const carritoItems = await obtenerCarritoItems();
      const total = parseFloat(document.getElementById('total').textContent.replace('S/', '').trim());
      
      if (!carritoItems || carritoItems.length === 0) {
        alert('El carrito está vacío');
        return;
      }
      
      // Mostrar loading
      placeOrderButton.disabled = true;
      placeOrderButton.textContent = 'Procesando pago...';
      
      // Intentar primero con PayPal
      const paypalResult = await procesarPagoPayPal(carritoItems, total);
      
      if (paypalResult.success) {
        // Redirigir a PayPal
        window.location.href = paypalResult.approval_url;
      } else {
        // Si PayPal falla, intentar con Stripe
        const stripeResult = await procesarPagoStripe(carritoItems, total);
        
        if (stripeResult.success) {
          if (stripeResult.requires_action) {
            // Manejar autenticación 3D Secure
            await manejarStripe3DS(stripeResult.payment_intent_client_secret);
          } else {
            // Pago exitoso
            mostrarExitoPago(stripeResult.pedido_id);
          }
        } else {
          alert('Error al procesar el pago: ' + stripeResult.message);
        }
      }
      
    } catch (error) {
      console.error('Error al procesar pago:', error);
      alert('Error al procesar el pago. Inténtalo de nuevo.');
    } finally {
      // Restaurar botón
      placeOrderButton.disabled = false;
      placeOrderButton.textContent = 'REALIZAR PEDIDO';
    }
  }

  // --- Procesar pago con PayPal ---
  async function procesarPagoPayPal(items, total) {
    try {
      const response = await fetch('/api/crear-pago-paypal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: items,
          total: total
        })
      });
      
      const result = await response.json();
      return result;
      
    } catch (error) {
      console.error('Error PayPal:', error);
      return { success: false, message: 'Error al conectar con PayPal' };
    }
  }

  // --- Procesar pago con Stripe ---
  async function procesarPagoStripe(items, total) {
    try {
      // Crear método de pago con Stripe
      const paymentMethod = await stripe.createPaymentMethod({
        type: 'card',
        card: {
          number: cardNumberInput.value.replace(/\s/g, ''),
          exp_month: parseInt(expiryMonth.value),
          exp_year: parseInt(expiryYear.value),
          cvc: securityCode.value,
        },
        billing_details: {
          name: document.getElementById('first-name').value + ' ' + document.getElementById('last-name').value,
          email: document.getElementById('email').value,
        },
      });
      
      if (paymentMethod.error) {
        return { success: false, message: paymentMethod.error.message };
      }
      
      // Enviar al servidor
      const response = await fetch('/api/crear-pago-stripe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: items,
          total: total,
          payment_method_id: paymentMethod.paymentMethod.id
        })
      });
      
      const result = await response.json();
      return result;
      
    } catch (error) {
      console.error('Error Stripe:', error);
      return { success: false, message: 'Error al procesar la tarjeta' };
    }
  }

  // --- Manejar autenticación 3D Secure de Stripe ---
  async function manejarStripe3DS(clientSecret) {
    try {
      const result = await stripe.confirmCardPayment(clientSecret);
      
      if (result.error) {
        alert('Error en la autenticación: ' + result.error.message);
      } else if (result.paymentIntent.status === 'succeeded') {
        // Pago exitoso después de 3D Secure
        mostrarExitoPago();
      }
    } catch (error) {
      console.error('Error 3DS:', error);
      alert('Error en la autenticación de la tarjeta');
    }
  }

  // --- Obtener items del carrito ---
  async function obtenerCarritoItems() {
    try {
      const response = await fetch('/api/carrito');
      const data = await response.json();
      
      if (data.success) {
        return data.items.map(item => ({
          id: item.producto_id,
          nombre: item.nombre,
          precio: parseFloat(item.precio),
          cantidad: item.cantidad
        }));
      }
      return [];
    } catch (error) {
      console.error('Error al obtener carrito:', error);
      return [];
    }
  }

  // --- Mostrar éxito del pago ---
  function mostrarExitoPago(pedidoId = null) {
    closeModal();
    if (pedidoId) {
      window.location.href = `/pedido/${pedidoId}`;
    } else {
      window.location.href = '/mis-pedidos';
    }
  }

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
    document.getElementById('receipt-subtotal').textContent = formData.subtotal;
    document.getElementById('receipt-descuento').textContent = document.getElementById('descuento').textContent;
    document.getElementById('receipt-envio').textContent = document.getElementById('envio').textContent;
    document.getElementById('receipt-total-detail').textContent = formData.total;
    document.getElementById('receipt-billing-address').textContent = `${formData.address}, ${formData.city}, ${formData.country}`;
    document.getElementById('receipt-phone').textContent = formData.phone;
    // Mostrar modal
    receiptModal.classList.remove('hidden');
  }
  closeReceiptBtns.forEach(btn => btn.addEventListener('click', () => receiptModal.classList.add('hidden')));
  receiptModal.addEventListener('click', function(e) {
    if (e.target === receiptModal) receiptModal.classList.add('hidden');
  });
  printReceiptButton.addEventListener('click', function() {
    window.print();
  });

  // --- Funciones auxiliares ---
  function loadProducts() {
    const productList = document.getElementById('product-list');
    if (!productList) return;
    
    // Obtener productos del carrito (esto debería venir del backend)
    const carritoItems = window.carritoItems || [];
    
    productList.innerHTML = '';
    carritoItems.forEach(item => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'flex justify-between py-2 border-b';
      itemDiv.innerHTML = `
        <span class="text-sm">${item.nombre} x${item.cantidad}</span>
        <span class="text-sm font-semibold">S/${(item.precio * item.cantidad).toFixed(2)}</span>
      `;
      productList.appendChild(itemDiv);
    });
    
    calculateTotals();
  }

  function calculateTotals() {
    // Los totales ya están calculados en el carrito
    // Esta función se puede usar para recalcular si es necesario
  }

  function generateYapeQR() {
    const yapeQR = document.getElementById('yape-qr');
    if (!yapeQR) return;
    
    // Generar QR para Yape (en producción, usar una librería real)
    const total = document.getElementById('total').textContent;
    const qrText = `yape://pay?phone=${yapeNumber}&amount=${total.replace('S/', '').trim()}`;
    
    // Usar QR Server API para generar el código QR
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrText)}`;
    yapeQR.innerHTML = `<img src="${qrUrl}" alt="QR Yape" class="w-full h-full object-contain" />`;
  }

  function validateForm() {
    let isValid = true;
    const selectedPaymentOption = document.querySelector('input[name="payment-option"]:checked').value;
    
    // Validar campos obligatorios
    const requiredFields = ['first-name', 'last-name', 'email', 'phone', 'address', 'country', 'city'];
    requiredFields.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (!field.value.trim()) {
        showValidationError(field, 'Este campo es obligatorio');
        isValid = false;
      } else {
        clearValidationError(field);
      }
    });
    
    // Validar email
    const email = document.getElementById('email').value;
    if (email && !isValidEmail(email)) {
      showValidationError(document.getElementById('email'), 'Email inválido');
      isValid = false;
    }
    
    // Validar tarjeta si es método de pago
    if (selectedPaymentOption === 'credit-card') {
      if (!cardNumberInput.value.trim()) {
        showValidationError(cardNumberInput, 'Número de tarjeta requerido');
        isValid = false;
      }
      if (!expiryMonth.value || !expiryYear.value) {
        showValidationError(expiryMonth, 'Fecha de vencimiento requerida');
        isValid = false;
      }
      if (!securityCode.value.trim()) {
        showValidationError(securityCode, 'Código de seguridad requerido');
        isValid = false;
      }
    }
    
    return isValid;
  }

  function showValidationError(element, message) {
    element.classList.add('border-red-500');
    element.classList.remove('border-blue-200');
    
    // Remover mensaje de error anterior
    const existingError = element.parentNode.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }
    
    // Agregar nuevo mensaje
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message text-red-500 text-xs mt-1';
    errorDiv.textContent = message;
    element.parentNode.appendChild(errorDiv);
    
    // Limpiar error al escribir
    element.addEventListener('input', function handler() {
      clearValidationError(element);
      element.removeEventListener('input', handler);
    });
  }

  function clearValidationError(element) {
    element.classList.remove('border-red-500');
    element.classList.add('border-blue-200');
    
    const errorMessage = element.parentNode.querySelector('.error-message');
    if (errorMessage) {
      errorMessage.remove();
    }
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function getPaymentMethodName(method) {
    const methods = {
      'credit-card': 'Tarjeta de crédito/débito',
      'bank-transfer': 'Transferencia bancaria',
      'yape': 'Yape'
    };
    return methods[method] || method;
  }
}); 