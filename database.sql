-- Estructura completa para tienda de cosméticos (MySQL)

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

-- Insertar datos de ejemplo

INSERT INTO categorias (nombre, descripcion) VALUES
('Maquillaje', 'Productos para maquillaje facial, ojos y labios'),
('Cuidado de la piel', 'Cremas, serums y productos para el cuidado facial y corporal'),
('Accesorios', 'Brochas, esponjas y otros accesorios de belleza');

INSERT INTO productos (nombre, descripcion, precio, stock, imagen, categoria_id, destacado) VALUES
('Base Líquida Natural', 'Base de maquillaje de cobertura media para todo tipo de piel.', 19.99, 50, 'base_liquida.png', 1, TRUE),
('Paleta de Sombras Glam', 'Paleta con 12 tonos vibrantes y duraderos.', 24.99, 30, 'paleta_sombras.png', 1, FALSE),
('Crema Hidratante Día', 'Crema ligera con SPF 15 para uso diario.', 15.50, 40, 'crema_dia.png', 2, TRUE),
('Serum Antiedad', 'Serum facial con ácido hialurónico y vitamina C.', 29.99, 25, 'serum_antiedad.png', 2, FALSE),
('Set de Brochas Pro', 'Set de 10 brochas profesionales para maquillaje.', 22.00, 20, 'set_brochas.png', 3, TRUE),
('Set Esenciales de Belleza', 'Incluye base, rubor y labial.', 62.00, 20, 'set_esenciales.png', 4, TRUE),
('Perfume Mujer Elegance', 'Fragancia floral y fresca para mujer.', 120.00, 15, 'perfume_mujer.png', 5, TRUE),
('Collar de Plata Fina', 'Collar elegante de plata 925.', 85.00, 10, 'collar_plata.png', 6, TRUE),
('Labial Líquido Mate', 'Color intenso y larga duración.', 35.00, 30, 'labial_liquido.png', 7, TRUE),
('Paleta de Sombras Nude', 'Tonos neutros para looks naturales.', 21.99, 25, 'paleta_sombras.png', 1, FALSE),
('Base Compacta', 'Base en polvo para acabado mate.', 18.50, 40, 'base_liquida.png', 1, FALSE),
('Crema de Noche', 'Nutre y regenera la piel mientras duermes.', 27.00, 30, 'crema_dia.png', 2, FALSE),
('Serum Iluminador', 'Aporta luminosidad instantánea.', 32.00, 18, 'serum_antiedad.png', 2, TRUE),
('Set de Esponjas', 'Pack de 3 esponjas para maquillaje.', 12.00, 50, 'set_brochas.png', 3, FALSE),
('Set de Brochas Viaje', 'Brochas compactas para llevar.', 16.00, 25, 'set_brochas.png', 3, FALSE),
('Perfume Hombre Sport', 'Aroma fresco y masculino.', 110.00, 12, 'perfume_mujer.png', 5, FALSE),
('Pulsera de Acero', 'Pulsera elegante para toda ocasión.', 45.00, 20, 'collar_plata.png', 6, FALSE),
('Anillo de Fantasía', 'Anillo ajustable con piedras.', 28.00, 15, 'collar_plata.png', 6, FALSE),
('Labial Gloss', 'Brillo de labios con color.', 22.00, 35, 'labial_liquido.png', 7, FALSE),
('Labial Barra Rojo', 'Color clásico y elegante.', 25.00, 30, 'labial_liquido.png', 7, FALSE),
('Set de Maquillaje Completo', 'Incluye sombras, rubor y labial.', 75.00, 10, 'set_esenciales.png', 4, TRUE),
('Set de Cuidado Facial', 'Limpieza, tónico y crema.', 55.00, 15, 'set_esenciales.png', 4, FALSE),
('Perfume Unisex Fresh', 'Aroma fresco para todos.', 99.00, 18, 'perfume_mujer.png', 5, FALSE),
('Collar de Acero', 'Collar moderno y resistente.', 38.00, 22, 'collar_plata.png', 6, FALSE),
('Paleta de Sombras Color', 'Colores vibrantes para looks creativos.', 26.00, 20, 'paleta_sombras.png', 1, FALSE),
('Base Mousse', 'Textura ligera y acabado natural.', 20.00, 30, 'base_liquida.png', 1, FALSE),
('Crema Antiedad', 'Reduce líneas de expresión.', 34.00, 25, 'crema_dia.png', 2, FALSE),
('Serum Hidratante', 'Hidratación profunda para la piel.', 30.00, 20, 'serum_antiedad.png', 2, FALSE),
('Set de Accesorios', 'Incluye brochas y esponjas.', 29.00, 18, 'set_brochas.png', 3, FALSE),
('Perfume Mujer Glam', 'Aroma sofisticado y duradero.', 130.00, 10, 'perfume_mujer.png', 5, TRUE),
('Anillo de Plata', 'Anillo elegante de plata.', 50.00, 12, 'collar_plata.png', 6, FALSE),
('Labial Nude', 'Tono natural para uso diario.', 23.00, 28, 'labial_liquido.png', 7, FALSE),
('Labial Rosa', 'Color vibrante y femenino.', 24.00, 26, 'labial_liquido.png', 7, FALSE);

INSERT INTO usuarios (nombre, email, contrasena, direccion, telefono, tipo_usuario) VALUES
('Admin', 'admin@bycint.com', 'admin123', 'Calle Principal 123', '010-420-0340', 'admin'),
('María López', 'maria@example.com', 'maria123', 'Av. Belleza 456', '010-111-2233', 'cliente'); 