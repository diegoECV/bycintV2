#!/usr/bin/env python3
"""
Script para actualizar la base de datos con la nueva estructura de usuarios
"""

import os
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de conexión MySQL a Amazon RDS
app.config['MYSQL_HOST'] = 'pagianweb2.cbddj5emoatz.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'diego123456'
app.config['MYSQL_DB'] = 'bycint2'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

def update_database():
    """Actualizar la estructura de la base de datos"""
    try:
        cur = mysql.connection.cursor()
        
        # Verificar si las columnas ya existen
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'facebook_id'")
        facebook_exists = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'google_id'")
        google_exists = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'avatar_url'")
        avatar_exists = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'email_verificado'")
        email_verified_exists = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'ultimo_login'")
        last_login_exists = cur.fetchone()
        
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'apellido'")
        apellido_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'documento'")
        documento_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'genero'")
        genero_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'fecha_nacimiento'")
        fecha_nacimiento_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM usuarios LIKE 'boletin'")
        boletin_exists = cur.fetchone()
        
        # Agregar columnas que no existen
        if not facebook_exists:
            print("Agregando columna facebook_id...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN facebook_id VARCHAR(100) UNIQUE")
        
        if not google_exists:
            print("Agregando columna google_id...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN google_id VARCHAR(100) UNIQUE")
        
        if not avatar_exists:
            print("Agregando columna avatar_url...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN avatar_url VARCHAR(255)")
        
        if not email_verified_exists:
            print("Agregando columna email_verificado...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN email_verificado BOOLEAN DEFAULT FALSE")
        
        if not last_login_exists:
            print("Agregando columna ultimo_login...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN ultimo_login TIMESTAMP NULL")
        
        if not apellido_exists:
            print("Agregando columna apellido...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN apellido VARCHAR(100)")
        
        if not documento_exists:
            print("Agregando columna documento...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN documento VARCHAR(50)")
        
        if not genero_exists:
            print("Agregando columna genero...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN genero VARCHAR(20)")
        
        if not fecha_nacimiento_exists:
            print("Agregando columna fecha_nacimiento...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN fecha_nacimiento DATE")
        
        if not boletin_exists:
            print("Agregando columna boletin...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN boletin BOOLEAN DEFAULT FALSE")
        
        # Hacer la columna contrasena nullable para usuarios de redes sociales
        cur.execute("ALTER TABLE usuarios MODIFY COLUMN contrasena VARCHAR(255)")
        
        # --- PRODUCTOS ---
        cur.execute("SHOW COLUMNS FROM productos LIKE 'tipo'")
        tipo_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'acabado'")
        acabado_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'material'")
        material_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'genero'")
        genero_prod_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'precio_original'")
        precio_original_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'descuento'")
        descuento_exists = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM productos LIKE 'fecha_release'")
        fecha_release_exists = cur.fetchone()

        if not tipo_exists:
            print("Agregando columna tipo a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN tipo VARCHAR(50)")
        if not acabado_exists:
            print("Agregando columna acabado a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN acabado VARCHAR(50)")
        if not material_exists:
            print("Agregando columna material a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN material VARCHAR(50)")
        if not genero_prod_exists:
            print("Agregando columna genero a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN genero VARCHAR(20)")
        if not precio_original_exists:
            print("Agregando columna precio_original a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN precio_original DECIMAL(10,2)")
        if not descuento_exists:
            print("Agregando columna descuento a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN descuento INT")
        if not fecha_release_exists:
            print("Agregando columna fecha_release a productos...")
            cur.execute("ALTER TABLE productos ADD COLUMN fecha_release DATE")

        # --- FAVORITOS ---
        cur.execute("SHOW TABLES LIKE 'favoritos'")
        if not cur.fetchone():
            print("Creando tabla favoritos...")
            cur.execute('''CREATE TABLE favoritos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                producto_id INT NOT NULL,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_fav (usuario_id, producto_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
            )''')

        # --- WISHLIST ---
        cur.execute("SHOW TABLES LIKE 'wishlist'")
        if not cur.fetchone():
            print("Creando tabla wishlist...")
            cur.execute('''CREATE TABLE wishlist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                producto_id INT NOT NULL,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_wishlist (usuario_id, producto_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
            )''')

        # --- SUSCRIPTORES ---
        cur.execute("SHOW TABLES LIKE 'suscriptores'")
        if not cur.fetchone():
            print("Creando tabla suscriptores...")
            cur.execute('''CREATE TABLE suscriptores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                correo VARCHAR(150) NOT NULL UNIQUE,
                fecha_suscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

        # --- COMENTARIOS BLOG ---
        cur.execute("SHOW TABLES LIKE 'comentarios_blog'")
        if not cur.fetchone():
            print("Creando tabla comentarios_blog...")
            cur.execute('''CREATE TABLE comentarios_blog (
                id INT AUTO_INCREMENT PRIMARY KEY,
                blog_id INT NOT NULL,
                correo_suscriptor VARCHAR(150) NOT NULL,
                comentario TEXT NOT NULL,
                puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

        # --- CUPONES USADOS ---
        cur.execute("SHOW TABLES LIKE 'cupones_usados'")
        if not cur.fetchone():
            print("Creando tabla cupones_usados...")
            cur.execute('''CREATE TABLE cupones_usados (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                cupon VARCHAR(50) NOT NULL,
                fecha_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_coupon (usuario_id, cupon),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )''')
        
        mysql.connection.commit()
        cur.close()
        
        print("✅ Base de datos actualizada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        mysql.connection.rollback()

if __name__ == "__main__":
    with app.app_context():
        update_database() 