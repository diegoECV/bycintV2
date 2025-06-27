from app import app, mysql

with app.app_context():
    cur = mysql.connection.cursor()
    # Crear tabla categorias
    cur.execute('''CREATE TABLE IF NOT EXISTS categorias (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT
    )''')
    # Crear tabla productos
    cur.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT,
        precio DECIMAL(10,2) NOT NULL,
        stock INT NOT NULL,
        imagen VARCHAR(255),
        categoria_id INT,
        destacado BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )''')
    # Crear tabla usuarios
    cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        contrasena VARCHAR(255) NOT NULL,
        direccion VARCHAR(255),
        telefono VARCHAR(20),
        tipo_usuario ENUM('cliente','admin') DEFAULT 'cliente',
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Crear tabla carrito
    cur.execute('''CREATE TABLE IF NOT EXISTS carrito (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        producto_id INT,
        cantidad INT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )''')
    # Crear tabla pedidos
    cur.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total DECIMAL(10,2) NOT NULL,
        estado VARCHAR(50) DEFAULT 'pendiente',
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')
    # Crear tabla detalle_pedido
    cur.execute('''CREATE TABLE IF NOT EXISTS detalle_pedido (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pedido_id INT,
        producto_id INT,
        cantidad INT NOT NULL,
        precio_unitario DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )''')
    mysql.connection.commit()
    cur.close()
    print('Tablas creadas exitosamente.') 