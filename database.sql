-- Estructura completa para tienda de cosméticos (MySQL)

-- TABLAS PRINCIPALES

CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    precio_original DECIMAL(10,2),
    descuento INT,
    stock INT NOT NULL,
    imagen VARCHAR(255),
    categoria_id INT,
    destacado BOOLEAN DEFAULT FALSE,
    tipo VARCHAR(50),
    acabado VARCHAR(50),
    material VARCHAR(50),
    genero VARCHAR(20),
    fecha_release DATE,
    peso DECIMAL(8,2) DEFAULT 0.00, -- Peso en gramos
    dimensiones VARCHAR(50), -- Formato: "LxAxH" en cm
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255),
    documento VARCHAR(50),
    genero VARCHAR(20),
    fecha_nacimiento DATE,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    tipo_usuario ENUM('cliente','admin') DEFAULT 'cliente',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    facebook_id VARCHAR(100) UNIQUE,
    google_id VARCHAR(100) UNIQUE,
    avatar_url VARCHAR(255),
    email_verificado BOOLEAN DEFAULT FALSE,
    ultimo_login TIMESTAMP NULL,
    boletin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS carrito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    costo_envio DECIMAL(10,2) DEFAULT 0.00,
    metodo_envio VARCHAR(50),
    tiempo_entrega VARCHAR(50),
    tracking_number VARCHAR(100),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE TABLE IF NOT EXISTS favoritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    producto_id INT NOT NULL,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_fav (usuario_id, producto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    producto_id INT NOT NULL,
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_wishlist (usuario_id, producto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS suscriptores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(150) NOT NULL UNIQUE,
    fecha_suscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comentarios_blog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    blog_id INT NOT NULL,
    correo_suscriptor VARCHAR(150) NOT NULL,
    comentario TEXT NOT NULL,
    puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cupones_usados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    cupon VARCHAR(50) NOT NULL,
    fecha_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_coupon (usuario_id, cupon),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tarjetas_credito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titular VARCHAR(100) NOT NULL,
    numero VARCHAR(25) NOT NULL,
    vencimiento VARCHAR(7) NOT NULL, -- MM/AAAA
    cvv VARCHAR(5) NOT NULL,
    marca VARCHAR(20),
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS direcciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100),
    pais VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(20),
    telefono VARCHAR(20),
    tipo ENUM('envio','facturacion') DEFAULT 'envio',
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- TABLAS PARA SISTEMA DE ENVÍOS

CREATE TABLE IF NOT EXISTS zonas_envio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    provincia VARCHAR(100),
    distrito VARCHAR(100),
    codigo_postal VARCHAR(20),
    costo_base DECIMAL(10,2) NOT NULL,
    tiempo_entrega_min INT NOT NULL, -- días
    tiempo_entrega_max INT NOT NULL, -- días
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS metodos_envio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo_base DECIMAL(10,2) NOT NULL,
    costo_por_kg DECIMAL(10,2) DEFAULT 0.00,
    tiempo_entrega_min INT NOT NULL, -- días
    tiempo_entrega_max INT NOT NULL, -- días
    activo BOOLEAN DEFAULT TRUE,
    prioridad INT DEFAULT 0 -- Para ordenar opciones
);

CREATE TABLE IF NOT EXISTS tarifas_envio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zona_id INT NOT NULL,
    metodo_id INT NOT NULL,
    peso_min DECIMAL(8,2) NOT NULL, -- en gramos
    peso_max DECIMAL(8,2) NOT NULL, -- en gramos
    costo DECIMAL(10,2) NOT NULL,
    tiempo_entrega_min INT NOT NULL,
    tiempo_entrega_max INT NOT NULL,
    FOREIGN KEY (zona_id) REFERENCES zonas_envio(id),
    FOREIGN KEY (metodo_id) REFERENCES metodos_envio(id)
);

-- Insertar datos de ejemplo

INSERT INTO categorias (nombre, descripcion) VALUES
('sets', 'Conjuntos y kits de productos de belleza'),
('maquillaje', 'Productos para maquillaje facial, ojos y labios'),
('joyeria', 'Joyas y accesorios elegantes'),
('perfumes', 'Fragancias y perfumes de alta calidad'),
('pintalabios', 'Labiales y productos para los labios'),
('cuidado de la piel', 'Productos para el cuidado facial y corporal'),
('accesorios', 'Accesorios de belleza y moda');

INSERT INTO usuarios (nombre, email, contrasena, direccion, telefono, tipo_usuario) VALUES
('Admin', 'admin@bycint.com', 'admin123', 'Calle Principal 123', '010-420-0340', 'admin'),
('María López', 'maria@example.com', 'maria123', 'Av. Belleza 456', '010-111-2233', 'cliente');

-- ===== DATOS DE ENVÍO =====

-- Métodos de envío
INSERT INTO metodos_envio (nombre, descripcion, costo_base, costo_por_kg, tiempo_entrega_min, tiempo_entrega_max, activo, prioridad) VALUES
('Envío Estándar', 'Entrega en 3-5 días hábiles', 8.00, 2.00, 3, 5, TRUE, 1),
('Envío Express', 'Entrega en 1-2 días hábiles', 15.00, 3.50, 1, 2, TRUE, 2),
('Envío Gratis', 'Gratis en compras mayores a S/ 100', 0.00, 0.00, 5, 7, TRUE, 0),
('Retiro en Tienda', 'Recoge en nuestro local', 0.00, 0.00, 0, 0, TRUE, 3);

-- Zonas de envío (Lima y principales ciudades)
INSERT INTO zonas_envio (nombre, departamento, provincia, distrito, codigo_postal, costo_base, tiempo_entrega_min, tiempo_entrega_max, activo) VALUES
('Lima Centro', 'Lima', 'Lima', 'Lima', '15001', 5.00, 1, 2, TRUE),
('Lima Norte', 'Lima', 'Lima', 'San Martín de Porres', '15301', 6.00, 1, 3, TRUE),
('Lima Sur', 'Lima', 'Lima', 'Chorrillos', '15063', 6.00, 1, 3, TRUE),
('Lima Este', 'Lima', 'Lima', 'Ate', '15003', 7.00, 2, 3, TRUE),
('Callao', 'Callao', 'Callao', 'Callao', '07001', 8.00, 2, 3, TRUE),
('Arequipa', 'Arequipa', 'Arequipa', 'Arequipa', '04001', 12.00, 3, 5, TRUE),
('Trujillo', 'La Libertad', 'Trujillo', 'Trujillo', '13001', 12.00, 3, 5, TRUE),
('Piura', 'Piura', 'Piura', 'Piura', '20001', 15.00, 4, 6, TRUE),
('Chiclayo', 'Lambayeque', 'Chiclayo', 'Chiclayo', '14001', 14.00, 4, 6, TRUE),
('Cusco', 'Cusco', 'Cusco', 'Cusco', '08001', 18.00, 5, 7, TRUE);

-- Tarifas de envío (ejemplos para Lima Centro)
INSERT INTO tarifas_envio (zona_id, metodo_id, peso_min, peso_max, costo, tiempo_entrega_min, tiempo_entrega_max) VALUES
-- Lima Centro - Estándar
(1, 1, 0, 500, 5.00, 1, 2),
(1, 1, 500, 1000, 7.00, 1, 2),
(1, 1, 1000, 2000, 9.00, 1, 2),
-- Lima Centro - Express
(1, 2, 0, 500, 15.00, 1, 1),
(1, 2, 500, 1000, 18.00, 1, 1),
(1, 2, 1000, 2000, 22.00, 1, 1),
-- Lima Centro - Gratis (solo para compras > S/ 100)
(1, 3, 0, 2000, 0.00, 3, 5);

-- ===== PRODUCTOS DE EJEMPLO (30 por categoría) =====

-- 30 productos para SETS (categoria_id = 1)
INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, imagen, categoria_id, destacado) VALUES
('Set Especial 1', 'Set de productos de belleza edición especial.', 49.90, 59.90, 17, 50, 'producto_destacado.png', 1, FALSE),
('Set Especial 2', 'Set de productos de belleza edición especial.', 50.90, 60.90, 16, 40, 'producto_destacado.png', 1, FALSE),
('Set Especial 3', 'Set de productos de belleza edición especial.', 51.90, 61.90, 16, 35, 'producto_destacado.png', 1, FALSE),
('Set Especial 4', 'Set de productos de belleza edición especial.', 52.90, 62.90, 16, 60, 'producto_destacado.png', 1, FALSE),
('Set Especial 5', 'Set de productos de belleza edición especial.', 53.90, 63.90, 16, 45, 'producto_destacado.png', 1, FALSE),
('Set Especial 6', 'Set de productos de belleza edición especial.', 54.90, 64.90, 15, 55, 'producto_destacado.png', 1, FALSE),
('Set Especial 7', 'Set de productos de belleza edición especial.', 55.90, 65.90, 15, 38, 'producto_destacado.png', 1, FALSE),
('Set Especial 8', 'Set de productos de belleza edición especial.', 56.90, 66.90, 15, 42, 'producto_destacado.png', 1, FALSE),
('Set Especial 9', 'Set de productos de belleza edición especial.', 57.90, 67.90, 15, 47, 'producto_destacado.png', 1, FALSE),
('Set Especial 10', 'Set de productos de belleza edición especial.', 58.90, 68.90, 15, 53, 'producto_destacado.png', 1, FALSE),
('Set Especial 11', 'Set de productos de belleza edición especial.', 59.90, 69.90, 14, 50, 'producto_destacado.png', 1, FALSE),
('Set Especial 12', 'Set de productos de belleza edición especial.', 60.90, 70.90, 14, 40, 'producto_destacado.png', 1, FALSE),
('Set Especial 13', 'Set de productos de belleza edición especial.', 61.90, 71.90, 14, 35, 'producto_destacado.png', 1, FALSE),
('Set Especial 14', 'Set de productos de belleza edición especial.', 62.90, 72.90, 14, 60, 'producto_destacado.png', 1, FALSE),
('Set Especial 15', 'Set de productos de belleza edición especial.', 63.90, 73.90, 14, 45, 'producto_destacado.png', 1, FALSE),
('Set Especial 16', 'Set de productos de belleza edición especial.', 64.90, 74.90, 13, 55, 'producto_destacado.png', 1, FALSE),
('Set Especial 17', 'Set de productos de belleza edición especial.', 65.90, 75.90, 13, 38, 'producto_destacado.png', 1, FALSE),
('Set Especial 18', 'Set de productos de belleza edición especial.', 66.90, 76.90, 13, 42, 'producto_destacado.png', 1, FALSE),
('Set Especial 19', 'Set de productos de belleza edición especial.', 67.90, 77.90, 13, 47, 'producto_destacado.png', 1, FALSE),
('Set Especial 20', 'Set de productos de belleza edición especial.', 68.90, 78.90, 13, 53, 'producto_destacado.png', 1, FALSE),
('Set Especial 21', 'Set de productos de belleza edición especial.', 69.90, 79.90, 13, 50, 'producto_destacado.png', 1, FALSE),
('Set Especial 22', 'Set de productos de belleza edición especial.', 70.90, 80.90, 12, 40, 'producto_destacado.png', 1, FALSE),
('Set Especial 23', 'Set de productos de belleza edición especial.', 71.90, 81.90, 12, 35, 'producto_destacado.png', 1, FALSE),
('Set Especial 24', 'Set de productos de belleza edición especial.', 72.90, 82.90, 12, 60, 'producto_destacado.png', 1, FALSE),
('Set Especial 25', 'Set de productos de belleza edición especial.', 73.90, 83.90, 12, 45, 'producto_destacado.png', 1, FALSE),
('Set Especial 26', 'Set de productos de belleza edición especial.', 74.90, 84.90, 12, 55, 'producto_destacado.png', 1, FALSE),
('Set Especial 27', 'Set de productos de belleza edición especial.', 75.90, 85.90, 12, 38, 'producto_destacado.png', 1, FALSE),
('Set Especial 28', 'Set de productos de belleza edición especial.', 76.90, 86.90, 11, 42, 'producto_destacado.png', 1, FALSE),
('Set Especial 29', 'Set de productos de belleza edición especial.', 77.90, 87.90, 11, 47, 'producto_destacado.png', 1, FALSE),
('Set Especial 30', 'Set de productos de belleza edición especial.', 78.90, 88.90, 11, 53, 'producto_destacado.png', 1, FALSE);

-- 30 productos para MAQUILLAJE (categoria_id = 2)
INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, imagen, categoria_id, destacado) VALUES
('Maquillaje Pro 1', 'Producto de maquillaje profesional.', 19.90, 24.90, 20, 50, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 2', 'Producto de maquillaje profesional.', 20.90, 25.90, 19, 40, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 3', 'Producto de maquillaje profesional.', 21.90, 26.90, 19, 35, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 4', 'Producto de maquillaje profesional.', 22.90, 27.90, 18, 60, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 5', 'Producto de maquillaje profesional.', 23.90, 28.90, 17, 45, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 6', 'Producto de maquillaje profesional.', 24.90, 29.90, 17, 55, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 7', 'Producto de maquillaje profesional.', 25.90, 30.90, 16, 38, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 8', 'Producto de maquillaje profesional.', 26.90, 31.90, 16, 42, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 9', 'Producto de maquillaje profesional.', 27.90, 32.90, 15, 47, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 10', 'Producto de maquillaje profesional.', 28.90, 33.90, 15, 53, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 11', 'Producto de maquillaje profesional.', 29.90, 34.90, 14, 50, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 12', 'Producto de maquillaje profesional.', 30.90, 35.90, 14, 40, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 13', 'Producto de maquillaje profesional.', 31.90, 36.90, 14, 35, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 14', 'Producto de maquillaje profesional.', 32.90, 37.90, 13, 60, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 15', 'Producto de maquillaje profesional.', 33.90, 38.90, 13, 45, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 16', 'Producto de maquillaje profesional.', 34.90, 39.90, 13, 55, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 17', 'Producto de maquillaje profesional.', 35.90, 40.90, 12, 38, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 18', 'Producto de maquillaje profesional.', 36.90, 41.90, 12, 42, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 19', 'Producto de maquillaje profesional.', 37.90, 42.90, 12, 47, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 20', 'Producto de maquillaje profesional.', 38.90, 43.90, 11, 53, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 21', 'Producto de maquillaje profesional.', 39.90, 44.90, 11, 50, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 22', 'Producto de maquillaje profesional.', 40.90, 45.90, 11, 40, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 23', 'Producto de maquillaje profesional.', 41.90, 46.90, 10, 35, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 24', 'Producto de maquillaje profesional.', 42.90, 47.90, 10, 60, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 25', 'Producto de maquillaje profesional.', 43.90, 48.90, 10, 45, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 26', 'Producto de maquillaje profesional.', 44.90, 49.90, 10, 55, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 27', 'Producto de maquillaje profesional.', 45.90, 50.90, 9, 38, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 28', 'Producto de maquillaje profesional.', 46.90, 51.90, 9, 42, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 29', 'Producto de maquillaje profesional.', 47.90, 52.90, 9, 47, 'producto_destacado.png', 2, FALSE),
('Maquillaje Pro 30', 'Producto de maquillaje profesional.', 48.90, 53.90, 9, 53, 'producto_destacado.png', 2, FALSE);

-- 30 productos para JOYERÍA (categoria_id = 3)
INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, imagen, categoria_id, destacado) VALUES
('Joya Elegante 1', 'Joya de alta calidad y diseño exclusivo.', 35.90, 45.90, 22, 50, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 2', 'Joya de alta calidad y diseño exclusivo.', 36.90, 46.90, 21, 40, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 3', 'Joya de alta calidad y diseño exclusivo.', 37.90, 47.90, 21, 35, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 4', 'Joya de alta calidad y diseño exclusivo.', 38.90, 48.90, 20, 60, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 5', 'Joya de alta calidad y diseño exclusivo.', 39.90, 49.90, 20, 45, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 6', 'Joya de alta calidad y diseño exclusivo.', 40.90, 50.90, 19, 55, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 7', 'Joya de alta calidad y diseño exclusivo.', 41.90, 51.90, 19, 38, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 8', 'Joya de alta calidad y diseño exclusivo.', 42.90, 52.90, 18, 42, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 9', 'Joya de alta calidad y diseño exclusivo.', 43.90, 53.90, 18, 47, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 10', 'Joya de alta calidad y diseño exclusivo.', 44.90, 54.90, 18, 53, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 11', 'Joya de alta calidad y diseño exclusivo.', 45.90, 55.90, 17, 50, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 12', 'Joya de alta calidad y diseño exclusivo.', 46.90, 56.90, 17, 40, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 13', 'Joya de alta calidad y diseño exclusivo.', 47.90, 57.90, 17, 35, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 14', 'Joya de alta calidad y diseño exclusivo.', 48.90, 58.90, 16, 60, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 15', 'Joya de alta calidad y diseño exclusivo.', 49.90, 59.90, 16, 45, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 16', 'Joya de alta calidad y diseño exclusivo.', 50.90, 60.90, 16, 55, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 17', 'Joya de alta calidad y diseño exclusivo.', 51.90, 61.90, 15, 38, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 18', 'Joya de alta calidad y diseño exclusivo.', 52.90, 62.90, 15, 42, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 19', 'Joya de alta calidad y diseño exclusivo.', 53.90, 63.90, 15, 47, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 20', 'Joya de alta calidad y diseño exclusivo.', 54.90, 64.90, 14, 53, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 21', 'Joya de alta calidad y diseño exclusivo.', 55.90, 65.90, 14, 50, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 22', 'Joya de alta calidad y diseño exclusivo.', 56.90, 66.90, 14, 40, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 23', 'Joya de alta calidad y diseño exclusivo.', 57.90, 67.90, 13, 35, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 24', 'Joya de alta calidad y diseño exclusivo.', 58.90, 68.90, 13, 60, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 25', 'Joya de alta calidad y diseño exclusivo.', 59.90, 69.90, 13, 45, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 26', 'Joya de alta calidad y diseño exclusivo.', 60.90, 70.90, 13, 55, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 27', 'Joya de alta calidad y diseño exclusivo.', 61.90, 71.90, 12, 38, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 28', 'Joya de alta calidad y diseño exclusivo.', 62.90, 72.90, 12, 42, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 29', 'Joya de alta calidad y diseño exclusivo.', 63.90, 73.90, 12, 47, 'producto_destacado.png', 3, FALSE),
('Joya Elegante 30', 'Joya de alta calidad y diseño exclusivo.', 64.90, 74.90, 12, 53, 'producto_destacado.png', 3, FALSE);

-- 30 productos para PERFUMES (categoria_id = 4)
INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, imagen, categoria_id, destacado) VALUES
('Perfume Deluxe 1', 'Perfume de alta calidad y fragancia duradera.', 59.90, 69.90, 14, 50, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 2', 'Perfume de alta calidad y fragancia duradera.', 60.90, 70.90, 14, 40, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 3', 'Perfume de alta calidad y fragancia duradera.', 61.90, 71.90, 14, 35, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 4', 'Perfume de alta calidad y fragancia duradera.', 62.90, 72.90, 14, 60, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 5', 'Perfume de alta calidad y fragancia duradera.', 63.90, 73.90, 13, 45, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 6', 'Perfume de alta calidad y fragancia duradera.', 64.90, 74.90, 13, 55, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 7', 'Perfume de alta calidad y fragancia duradera.', 65.90, 75.90, 13, 38, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 8', 'Perfume de alta calidad y fragancia duradera.', 66.90, 76.90, 13, 42, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 9', 'Perfume de alta calidad y fragancia duradera.', 67.90, 77.90, 13, 47, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 10', 'Perfume de alta calidad y fragancia duradera.', 68.90, 78.90, 13, 53, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 11', 'Perfume de alta calidad y fragancia duradera.', 69.90, 79.90, 12, 50, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 12', 'Perfume de alta calidad y fragancia duradera.', 70.90, 80.90, 12, 40, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 13', 'Perfume de alta calidad y fragancia duradera.', 71.90, 81.90, 12, 35, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 14', 'Perfume de alta calidad y fragancia duradera.', 72.90, 82.90, 12, 60, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 15', 'Perfume de alta calidad y fragancia duradera.', 73.90, 83.90, 12, 45, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 16', 'Perfume de alta calidad y fragancia duradera.', 74.90, 84.90, 12, 55, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 17', 'Perfume de alta calidad y fragancia duradera.', 75.90, 85.90, 11, 38, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 18', 'Perfume de alta calidad y fragancia duradera.', 76.90, 86.90, 11, 42, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 19', 'Perfume de alta calidad y fragancia duradera.', 77.90, 87.90, 11, 47, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 20', 'Perfume de alta calidad y fragancia duradera.', 78.90, 88.90, 11, 53, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 21', 'Perfume de alta calidad y fragancia duradera.', 79.90, 89.90, 10, 50, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 22', 'Perfume de alta calidad y fragancia duradera.', 80.90, 90.90, 10, 40, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 23', 'Perfume de alta calidad y fragancia duradera.', 81.90, 91.90, 10, 35, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 24', 'Perfume de alta calidad y fragancia duradera.', 82.90, 92.90, 9, 60, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 25', 'Perfume de alta calidad y fragancia duradera.', 83.90, 93.90, 9, 45, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 26', 'Perfume de alta calidad y fragancia duradera.', 84.90, 94.90, 9, 55, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 27', 'Perfume de alta calidad y fragancia duradera.', 85.90, 95.90, 8, 38, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 28', 'Perfume de alta calidad y fragancia duradera.', 86.90, 96.90, 8, 42, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 29', 'Perfume de alta calidad y fragancia duradera.', 87.90, 97.90, 8, 47, 'producto_destacado.png', 4, FALSE),
('Perfume Deluxe 30', 'Perfume de alta calidad y fragancia duradera.', 88.90, 98.90, 8, 53, 'producto_destacado.png', 4, FALSE);

-- 30 productos para PINTALABIOS (categoria_id = 5)
INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, imagen, categoria_id, destacado) VALUES
('Pintalabios Glam 1', 'Pintalabios de larga duración y color intenso.', 12.90, 15.90, 19, 50, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 2', 'Pintalabios de larga duración y color intenso.', 13.90, 16.90, 18, 40, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 3', 'Pintalabios de larga duración y color intenso.', 14.90, 17.90, 17, 35, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 4', 'Pintalabios de larga duración y color intenso.', 15.90, 18.90, 16, 60, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 5', 'Pintalabios de larga duración y color intenso.', 16.90, 19.90, 15, 45, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 6', 'Pintalabios de larga duración y color intenso.', 17.90, 20.90, 15, 55, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 7', 'Pintalabios de larga duración y color intenso.', 18.90, 21.90, 14, 38, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 8', 'Pintalabios de larga duración y color intenso.', 19.90, 22.90, 14, 42, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 9', 'Pintalabios de larga duración y color intenso.', 20.90, 23.90, 13, 47, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 10', 'Pintalabios de larga duración y color intenso.', 21.90, 24.90, 13, 53, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 11', 'Pintalabios de larga duración y color intenso.', 22.90, 25.90, 12, 50, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 12', 'Pintalabios de larga duración y color intenso.', 23.90, 26.90, 12, 40, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 13', 'Pintalabios de larga duración y color intenso.', 24.90, 27.90, 12, 35, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 14', 'Pintalabios de larga duración y color intenso.', 25.90, 28.90, 11, 60, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 15', 'Pintalabios de larga duración y color intenso.', 26.90, 29.90, 11, 45, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 16', 'Pintalabios de larga duración y color intenso.', 27.90, 30.90, 11, 55, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 17', 'Pintalabios de larga duración y color intenso.', 28.90, 31.90, 10, 38, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 18', 'Pintalabios de larga duración y color intenso.', 29.90, 32.90, 10, 42, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 19', 'Pintalabios de larga duración y color intenso.', 30.90, 33.90, 10, 47, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 20', 'Pintalabios de larga duración y color intenso.', 31.90, 34.90, 9, 53, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 21', 'Pintalabios de larga duración y color intenso.', 32.90, 35.90, 9, 50, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 22', 'Pintalabios de larga duración y color intenso.', 33.90, 36.90, 9, 40, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 23', 'Pintalabios de larga duración y color intenso.', 34.90, 37.90, 8, 35, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 24', 'Pintalabios de larga duración y color intenso.', 35.90, 38.90, 8, 60, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 25', 'Pintalabios de larga duración y color intenso.', 36.90, 39.90, 8, 45, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 26', 'Pintalabios de larga duración y color intenso.', 37.90, 40.90, 8, 55, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 27', 'Pintalabios de larga duración y color intenso.', 38.90, 41.90, 7, 38, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 28', 'Pintalabios de larga duración y color intenso.', 39.90, 42.90, 7, 42, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 29', 'Pintalabios de larga duración y color intenso.', 40.90, 43.90, 7, 47, 'producto_destacado.png', 5, FALSE),
('Pintalabios Glam 30', 'Pintalabios de larga duración y color intenso.', 41.90, 44.90, 7, 53, 'producto_destacado.png', 5, FALSE); 