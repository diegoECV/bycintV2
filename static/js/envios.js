/**
 * Sistema de Envíos - bycint Cosméticos
 * Maneja el cálculo de costos de envío y selección de métodos
 */

class SistemaEnvios {
    constructor() {
        this.zonas = [];
        this.distritos = {};
        this.opcionesEnvio = [];
        this.envioSeleccionado = null;
        this.init();
    }

    async init() {
        await this.cargarZonas();
        this.setupEventListeners();
    }

    async cargarZonas() {
        try {
            const response = await fetch('/api/zonas-envio');
            const data = await response.json();
            
            if (data.success) {
                this.zonas = data.zonas;
                this.popularDepartamentos();
            }
        } catch (error) {
            console.error('Error al cargar zonas:', error);
        }
    }

    popularDepartamentos() {
        const selectDepartamento = document.getElementById('departamento-envio');
        if (!selectDepartamento) return;

        // Limpiar opciones existentes
        selectDepartamento.innerHTML = '<option value="">Selecciona un departamento</option>';

        // Agregar departamentos únicos
        const departamentos = [...new Set(this.zonas.map(zona => zona.departamento))];
        departamentos.forEach(departamento => {
            const option = document.createElement('option');
            option.value = departamento;
            option.textContent = departamento;
            selectDepartamento.appendChild(option);
        });
    }

    async cargarProvincias(departamento) {
        const selectProvincia = document.getElementById('provincia-envio');
        if (!selectProvincia) return;

        // Limpiar opciones existentes
        selectProvincia.innerHTML = '<option value="">Selecciona una provincia</option>';

        // Filtrar provincias del departamento seleccionado
        const provincias = this.zonas
            .filter(zona => zona.departamento === departamento)
            .map(zona => zona.provincia);

        const provinciasUnicas = [...new Set(provincias)];
        provinciasUnicas.forEach(provincia => {
            const option = document.createElement('option');
            option.value = provincia;
            option.textContent = provincia;
            selectProvincia.appendChild(option);
        });
    }

    async cargarDistritos(departamento, provincia) {
        try {
            const response = await fetch(`/api/distritos/${encodeURIComponent(departamento)}/${encodeURIComponent(provincia)}`);
            const data = await response.json();
            
            if (data.success) {
                this.distritos[`${departamento}-${provincia}`] = data.distritos;
                this.popularDistritos(departamento, provincia);
            }
        } catch (error) {
            console.error('Error al cargar distritos:', error);
        }
    }

    popularDistritos(departamento, provincia) {
        const selectDistrito = document.getElementById('distrito-envio');
        if (!selectDistrito) return;

        // Limpiar opciones existentes
        selectDistrito.innerHTML = '<option value="">Selecciona un distrito</option>';

        const distritos = this.distritos[`${departamento}-${provincia}`] || [];
        distritos.forEach(distrito => {
            const option = document.createElement('option');
            option.value = distrito.distrito;
            option.textContent = distrito.distrito;
            option.dataset.codigoPostal = distrito.codigo_postal;
            selectDistrito.appendChild(option);
        });
    }

    setupEventListeners() {
        // Event listener para cambio de departamento
        const selectDepartamento = document.getElementById('departamento-envio');
        if (selectDepartamento) {
            selectDepartamento.addEventListener('change', (e) => {
                const departamento = e.target.value;
                if (departamento) {
                    this.cargarProvincias(departamento);
                    // Limpiar distrito
                    const selectDistrito = document.getElementById('distrito-envio');
                    if (selectDistrito) {
                        selectDistrito.innerHTML = '<option value="">Selecciona un distrito</option>';
                    }
                }
            });
        }

        // Event listener para cambio de provincia
        const selectProvincia = document.getElementById('provincia-envio');
        if (selectProvincia) {
            selectProvincia.addEventListener('change', (e) => {
                const provincia = e.target.value;
                const departamento = document.getElementById('departamento-envio')?.value;
                
                if (provincia && departamento) {
                    this.cargarDistritos(departamento, provincia);
                }
            });
        }

        // Event listener para cambio de distrito
        const selectDistrito = document.getElementById('distrito-envio');
        if (selectDistrito) {
            selectDistrito.addEventListener('change', (e) => {
                const distrito = e.target.value;
                if (distrito) {
                    // Actualizar código postal
                    const codigoPostal = e.target.selectedOptions[0].dataset.codigoPostal;
                    const inputCodigoPostal = document.getElementById('codigo-postal-envio');
                    if (inputCodigoPostal) {
                        inputCodigoPostal.value = codigoPostal || '';
                    }
                    
                    // Calcular envío automáticamente
                    this.calcularEnvio();
                }
            });
        }

        // Botón para calcular envío
        const btnCalcularEnvio = document.getElementById('btn-calcular-envio');
        if (btnCalcularEnvio) {
            btnCalcularEnvio.addEventListener('click', () => {
                this.calcularEnvio();
            });
        }
    }

    async calcularEnvio() {
        try {
            // Obtener datos de dirección
            const direccion = this.obtenerDatosDireccion();
            if (!this.validarDireccion(direccion)) {
                this.mostrarError('Por favor, completa todos los campos de dirección');
                return;
            }

            // Obtener items del carrito
            const carritoItems = await this.obtenerCarritoItems();
            if (!carritoItems || carritoItems.length === 0) {
                this.mostrarError('El carrito está vacío');
                return;
            }

            // Mostrar loading
            this.mostrarLoading();

            // Enviar solicitud al servidor
            const response = await fetch('/api/calcular-envio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    direccion: direccion,
                    items: carritoItems
                })
            });

            const data = await response.json();

            if (data.success) {
                this.opcionesEnvio = data.opciones;
                this.mostrarOpcionesEnvio(data.opciones, data.peso_total);
            } else {
                this.mostrarError(data.message || 'Error al calcular envío');
            }

        } catch (error) {
            console.error('Error al calcular envío:', error);
            this.mostrarError('Error de conexión al calcular envío');
        } finally {
            this.ocultarLoading();
        }
    }

    obtenerDatosDireccion() {
        return {
            departamento: document.getElementById('departamento-envio')?.value || '',
            provincia: document.getElementById('provincia-envio')?.value || '',
            distrito: document.getElementById('distrito-envio')?.value || '',
            codigo_postal: document.getElementById('codigo-postal-envio')?.value || ''
        };
    }

    validarDireccion(direccion) {
        return direccion.departamento && direccion.provincia && direccion.distrito;
    }

    async obtenerCarritoItems() {
        try {
            const response = await fetch('/api/carrito');
            const data = await response.json();
            
            if (data.success) {
                return data.items.map(item => ({
                    id: item.producto_id,
                    cantidad: item.cantidad
                }));
            }
            return [];
        } catch (error) {
            console.error('Error al obtener carrito:', error);
            return [];
        }
    }

    mostrarOpcionesEnvio(opciones, pesoTotal) {
        const container = document.getElementById('opciones-envio');
        if (!container) return;

        if (opciones.length === 0) {
            container.innerHTML = '<p class="text-red-500">No hay opciones de envío disponibles para esta ubicación</p>';
            return;
        }

        let html = `
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
                <h3 class="font-bold text-lg mb-3">Opciones de Envío</h3>
                <p class="text-sm text-gray-600 mb-3">Peso total: ${(pesoTotal / 1000).toFixed(2)} kg</p>
        `;

        opciones.forEach((opcion, index) => {
            const isGratis = opcion.costo === 0;
            const isRecomendado = opcion.nombre.includes('Estándar');
            
            html += `
                <div class="border rounded-lg p-3 mb-2 cursor-pointer hover:bg-blue-50 transition ${isRecomendado ? 'border-blue-300 bg-blue-50' : 'border-gray-200'}" 
                     onclick="sistemaEnvios.seleccionarEnvio(${index})">
                    <div class="flex justify-between items-center">
                        <div class="flex-1">
                            <div class="flex items-center gap-2">
                                <input type="radio" name="opcion-envio" value="${index}" ${index === 0 ? 'checked' : ''} 
                                       class="accent-blue-500">
                                <span class="font-semibold">${opcion.nombre}</span>
                                ${isRecomendado ? '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Recomendado</span>' : ''}
                            </div>
                            <p class="text-sm text-gray-600 mt-1">${opcion.descripcion}</p>
                            <p class="text-sm text-gray-500">Entrega: ${opcion.tiempo_entrega}</p>
                        </div>
                        <div class="text-right">
                            <span class="text-lg font-bold ${isGratis ? 'text-green-600' : 'text-gray-800'}">
                                ${isGratis ? 'GRATIS' : `S/ ${opcion.costo.toFixed(2)}`}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';

        // Agregar botón para confirmar envío
        html += `
            <button id="btn-confirmar-envio" 
                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition"
                    onclick="sistemaEnvios.confirmarEnvio()">
                Confirmar Envío
            </button>
        `;

        container.innerHTML = html;
    }

    seleccionarEnvio(index) {
        // Actualizar radio button
        const radios = document.querySelectorAll('input[name="opcion-envio"]');
        radios.forEach((radio, i) => {
            radio.checked = i === index;
        });

        // Actualizar selección visual
        const opciones = document.querySelectorAll('#opciones-envio > div > div');
        opciones.forEach((opcion, i) => {
            opcion.classList.remove('border-blue-300', 'bg-blue-50');
            if (i === index) {
                opcion.classList.add('border-blue-300', 'bg-blue-50');
            }
        });

        this.envioSeleccionado = this.opcionesEnvio[index];
    }

    async confirmarEnvio() {
        if (!this.envioSeleccionado) {
            this.mostrarError('Por favor, selecciona una opción de envío');
            return;
        }

        try {
            // Actualizar el costo de envío en la página
            this.actualizarCostoEnvio(this.envioSeleccionado);
            
            // Guardar en localStorage para usar en el checkout
            localStorage.setItem('envio_seleccionado', JSON.stringify(this.envioSeleccionado));
            
            this.mostrarExito('Envío configurado correctamente');
            
            // Cerrar modal si existe
            const modal = document.getElementById('envio-modal');
            if (modal) {
                modal.classList.add('hidden');
            }

        } catch (error) {
            console.error('Error al confirmar envío:', error);
            this.mostrarError('Error al confirmar envío');
        }
    }

    actualizarCostoEnvio(opcionEnvio) {
        // Actualizar en el resumen del carrito
        const elementoEnvio = document.getElementById('carrito-envio');
        if (elementoEnvio) {
            elementoEnvio.textContent = opcionEnvio.costo === 0 ? 'GRATIS' : `S/ ${opcionEnvio.costo.toFixed(2)}`;
        }

        // Actualizar total
        this.actualizarTotal();
    }

    actualizarTotal() {
        const subtotal = parseFloat(document.getElementById('carrito-subtotal')?.textContent.replace('S/', '').trim() || 0);
        const descuento = parseFloat(document.getElementById('carrito-descuento')?.textContent.replace('-S/', '').replace('S/', '').trim() || 0);
        const envio = this.envioSeleccionado ? this.envioSeleccionado.costo : 0;
        
        const total = subtotal - descuento + envio;
        
        const elementoTotal = document.getElementById('carrito-total');
        if (elementoTotal) {
            elementoTotal.textContent = `S/ ${total.toFixed(2)}`;
        }
    }

    mostrarLoading() {
        const btn = document.getElementById('btn-calcular-envio');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Calculando...';
        }
    }

    ocultarLoading() {
        const btn = document.getElementById('btn-calcular-envio');
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Calcular Envío';
        }
    }

    mostrarError(mensaje) {
        // Crear o actualizar mensaje de error
        let errorDiv = document.getElementById('error-envio');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'error-envio';
            errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
            
            const container = document.getElementById('opciones-envio') || document.querySelector('.envio-container');
            if (container) {
                container.insertBefore(errorDiv, container.firstChild);
            }
        }
        
        errorDiv.textContent = mensaje;
        errorDiv.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    mostrarExito(mensaje) {
        // Crear mensaje de éxito
        const successDiv = document.createElement('div');
        successDiv.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4';
        successDiv.textContent = mensaje;
        
        const container = document.getElementById('opciones-envio') || document.querySelector('.envio-container');
        if (container) {
            container.insertBefore(successDiv, container.firstChild);
        }
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    // Método para obtener envío seleccionado (usado en checkout)
    getEnvioSeleccionado() {
        return this.envioSeleccionado || JSON.parse(localStorage.getItem('envio_seleccionado') || 'null');
    }

    // Método para limpiar envío seleccionado
    limpiarEnvio() {
        this.envioSeleccionado = null;
        localStorage.removeItem('envio_seleccionado');
    }
}

// Inicializar sistema de envíos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.sistemaEnvios = new SistemaEnvios();
}); 