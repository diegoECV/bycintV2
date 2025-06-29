from dotenv import load_dotenv
load_dotenv()
import os
print('MYSQL_HOST:', os.getenv('MYSQL_HOST'))
print('MYSQL_USER:', os.getenv('MYSQL_USER'))
print('MYSQL_PASSWORD:', os.getenv('MYSQL_PASSWORD'))
print('MYSQL_DATABASE:', os.getenv('MYSQL_DATABASE'))
print('MYSQL_PORT:', os.getenv('MYSQL_PORT'))
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from functools import wraps
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_mail import Mail, Message
from flask import render_template_string
import paypalrestsdk
import stripe
from apscheduler.schedulers.background import BackgroundScheduler
import random
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import hashlib
import time
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

app = Flask(__name__)

# Secret key for sessions and flash messages (IMPORTANT)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuración de conexión MySQL a Amazon RDS (hardcodeada)
app.config['MYSQL_HOST'] = 'pagianweb2.cbddj5emoatz.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'diego123456'
app.config['MYSQL_DB'] = 'bycint2'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Variables globales para rate limiting y seguridad
failed_attempts = {}
login_attempts = {}

# Configuración Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'tu_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'tu_password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'tu_email@gmail.com')

mail = Mail(app)

# Configuración PayPal
paypalrestsdk.configure({
    "mode": os.getenv('PAYPAL_MODE', 'sandbox'),  # 'sandbox' o 'live'
    "client_id": os.getenv('PAYPAL_CLIENT_ID', ''),
    "client_secret": os.getenv('PAYPAL_CLIENT_SECRET', '')
})

# Configuración Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

# Configuración para OAuth (Facebook y Google)
# En producción, estas claves deben estar en variables de entorno
FACEBOOK_APP_ID = 'your_facebook_app_id'
FACEBOOK_APP_SECRET = 'your_facebook_app_secret'
GOOGLE_CLIENT_ID = 'your_google_client_id'
GOOGLE_CLIENT_SECRET = 'your_google_client_secret'

# Configuración OAuth con Flask-Dance
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo para desarrollo

google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'tu_google_client_id'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'tu_google_client_secret'),
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

facebook_bp = make_facebook_blueprint(
    client_id=os.getenv('FACEBOOK_APP_ID', 'tu_facebook_app_id'),
    client_secret=os.getenv('FACEBOOK_APP_SECRET', 'tu_facebook_app_secret'),
    scope=["email"],
    redirect_url="/login/facebook/authorized"
)
app.register_blueprint(facebook_bp, url_prefix="/login")

# Simulación de blogs (debería venir de la base de datos en producción)
blogs_demo = [
    {
        'id': 1,
        'titulo': 'Tendencias de maquillaje 2024',
        'contenido': 'Descubre los colores y estilos que marcarán el año en el mundo de la belleza. ¡Atrévete a probarlos!',
        'imagen': 'blog1.jpg',
        'resumen': 'Descubre los colores y estilos que marcarán el año en el mundo de la belleza.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-01-10'
    },
    {
        'id': 2,
        'titulo': 'Rutina de cuidado facial para piel radiante',
        'contenido': 'Tips y productos recomendados para mantener tu piel saludable y luminosa. ¡Cuida tu piel cada día!',
        'imagen': 'blog2.jpg',
        'resumen': 'Tips y productos recomendados para mantener tu piel saludable y luminosa.',
        'categoria': 'Cuidado de la piel',
        'autor': 'Dra. Camila Torres',
        'fecha_publicacion': '2024-02-05'
    },
    {
        'id': 3,
        'titulo': 'Cosmética natural: ¿por qué elegirla?',
        'contenido': 'Beneficios de los productos naturales y cómo incorporarlos en tu rutina. ¡Elige lo mejor para ti y el planeta!',
        'imagen': 'blog3.jpg',
        'resumen': 'Beneficios de los productos naturales y cómo incorporarlos en tu rutina.',
        'categoria': 'Cosmética natural',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-03-01'
    },
    {
        'id': 4,
        'titulo': 'Errores comunes al desmaquillarse',
        'contenido': 'Evita estos errores y mantén tu piel sana cada noche.',
        'imagen': 'blog1.jpg',
        'resumen': 'Evita estos errores y mantén tu piel sana cada noche.',
        'categoria': 'Maquillaje',
        'autor': 'María López',
        'fecha_publicacion': '2024-03-15'
    },
    {
        'id': 5,
        'titulo': 'Perfumes: cómo elegir el ideal',
        'contenido': 'Guía para encontrar la fragancia perfecta para cada ocasión.',
        'imagen': 'perfume_mujer.png',
        'resumen': 'Guía para encontrar la fragancia perfecta para cada ocasión.',
        'categoria': 'Perfumería',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-04-01'
    },
    {
        'id': 6,
        'titulo': 'Joyería minimalista: tendencia 2024',
        'contenido': 'Descubre cómo combinar piezas sencillas para un look elegante.',
        'imagen': 'collar_plata.png',
        'resumen': 'Descubre cómo combinar piezas sencillas para un look elegante.',
        'categoria': 'Joyería',
        'autor': 'Ana Ruiz',
        'fecha_publicacion': '2024-04-10'
    },
    {
        'id': 7,
        'titulo': 'Labiales: tonos de moda',
        'contenido': 'Los colores que serán tendencia esta temporada.',
        'imagen': 'labial_liquido.png',
        'resumen': 'Los colores que serán tendencia esta temporada.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-04-20'
    },
    {
        'id': 8,
        'titulo': 'Set de brochas: ¿cómo usarlas?',
        'contenido': 'Aprende a sacar el máximo provecho a tu set de brochas.',
        'imagen': 'set_brochas.png',
        'resumen': 'Aprende a sacar el máximo provecho a tu set de brochas.',
        'categoria': 'Accesorios',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-05-01'
    },
    {
        'id': 9,
        'titulo': 'Top 5 labiales para este verano',
        'contenido': 'Colores y texturas que serán tendencia en la temporada.',
        'imagen': 'blog2.jpg',
        'resumen': 'Colores y texturas que serán tendencia en la temporada.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-05-01'
    },
    {
        'id': 10,
        'titulo': 'Cómo elegir tu perfume ideal',
        'contenido': 'Guía para encontrar la fragancia perfecta para ti.',
        'imagen': 'blog3.jpg',
        'resumen': 'Guía para encontrar la fragancia perfecta para ti.',
        'categoria': 'Perfume',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-06-01'
    },
    {
        'id': 11,
        'titulo': 'Accesorios que realzan tu look',
        'contenido': 'Descubre cómo los accesorios pueden transformar tu estilo.',
        'imagen': 'blog1.jpg',
        'resumen': 'Descubre cómo los accesorios pueden transformar tu estilo.',
        'categoria': 'Accesorios',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-07-01'
    },
    {
        'id': 12,
        'titulo': 'Cuidado de la piel en invierno',
        'contenido': 'Consejos para mantener tu piel hidratada y protegida.',
        'imagen': 'blog2.jpg',
        'resumen': 'Consejos para mantener tu piel hidratada y protegida.',
        'categoria': 'Cuidado de la piel',
        'autor': 'Dra. Camila Torres',
        'fecha_publicacion': '2024-08-01'
    },
    {
        'id': 13,
        'titulo': 'Maquillaje para eventos especiales',
        'contenido': 'Ideas y tips para lucir espectacular en cualquier ocasión.',
        'imagen': 'blog3.jpg',
        'resumen': 'Ideas y tips para lucir espectacular en cualquier ocasión.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-09-01'
    },
    {
        'id': 14,
        'titulo': 'Brochas imprescindibles en tu kit',
        'contenido': 'Las brochas que no pueden faltar para un maquillaje profesional.',
        'imagen': 'blog1.jpg',
        'resumen': 'Las brochas que no pueden faltar para un maquillaje profesional.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-10-01'
    },
    {
        'id': 15,
        'titulo': 'Cómo lograr un delineado perfecto',
        'contenido': 'Técnicas y productos recomendados para un delineado impecable.',
        'imagen': 'blog2.jpg',
        'resumen': 'Técnicas y productos recomendados para un delineado impecable.',
        'categoria': 'Maquillaje',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-11-01'
    },
    {
        'id': 16,
        'titulo': 'Tendencias en joyería 2024',
        'contenido': 'Las piezas y estilos que dominarán este año.',
        'imagen': 'blog3.jpg',
        'resumen': 'Las piezas y estilos que dominarán este año.',
        'categoria': 'Joyería',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-12-01'
    },
    {
        'id': 17,
        'titulo': 'Rutina express para la mañana',
        'contenido': 'Ahorra tiempo y luce radiante con estos pasos rápidos.',
        'imagen': 'blog1.jpg',
        'resumen': 'Ahorra tiempo y luce radiante con estos pasos rápidos.',
        'categoria': 'Cuidado de la piel',
        'autor': 'Equipo bycint',
        'fecha_publicacion': '2024-01-01'
    },
]

# Simulación de comentarios y puntuaciones (en producción, usar base de datos)
comentarios_demo = {
    1: [
        {'usuario': 'Ana', 'comentario': '¡Me encantó este artículo!', 'puntuacion': 5},
        {'usuario': 'Luisa', 'comentario': 'Muy útil, gracias.', 'puntuacion': 4}
    ],
    2: [],
    3: []
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        if session.get('user_type') != 'admin':
            flash('No tienes permisos para acceder a esta página.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validar contraseña con criterios de seguridad más estrictos"""
    if not password:
        return False, "La contraseña es obligatoria"
    
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*)"
    
    # Verificar contraseñas comunes
    common_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123', 
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ]
    if password.lower() in common_passwords:
        return False, "La contraseña es demasiado común, elige una más segura"
    
    return True, "Contraseña válida"

def clean_input(text):
    """Limpiar y sanitizar entrada de texto"""
    if not text:
        return ""
    # Remover caracteres peligrosos
    text = re.sub(r'[<>"\']', '', str(text))
    # Remover espacios extra
    text = ' '.join(text.split())
    return text.strip()

def validate_nombre(nombre):
    """Validar nombre completo"""
    if not nombre:
        return False, "El nombre es obligatorio"
    
    nombre = clean_input(nombre)
    
    if len(nombre) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre no puede exceder 100 caracteres"
    
    # Solo letras, espacios y algunos caracteres especiales
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
        return False, "El nombre solo puede contener letras y espacios"
    
    return True, "Nombre válido"

def validate_telefono(telefono):
    """Validar número de teléfono"""
    if not telefono:
        return True, "Teléfono válido (opcional)"  # Es opcional
    
    telefono = clean_input(telefono)
    
    # Patrón para teléfonos peruanos
    if re.match(r'^(\+51\s?)?[9]\d{8}$', telefono):
        return True, "Teléfono válido"
    
    # Patrón internacional básico
    if re.match(r'^\+?[\d\s\-\(\)]{7,15}$', telefono):
        return True, "Teléfono válido"
    
    return False, "Formato de teléfono inválido"

def check_rate_limit(ip, action, max_attempts=5, window_minutes=15):
    """Verificar límite de intentos por IP"""
    current_time = time.time()
    window_seconds = window_minutes * 60
    
    if ip not in failed_attempts:
        failed_attempts[ip] = {}
    
    if action not in failed_attempts[ip]:
        failed_attempts[ip][action] = []
    
    # Limpiar intentos antiguos
    failed_attempts[ip][action] = [
        attempt_time for attempt_time in failed_attempts[ip][action]
        if current_time - attempt_time < window_seconds
    ]
    
    # Verificar si excede el límite
    if len(failed_attempts[ip][action]) >= max_attempts:
        return False
    
    return True

def record_failed_attempt(ip, action):
    """Registrar intento fallido"""
    current_time = time.time()
    
    if ip not in failed_attempts:
        failed_attempts[ip] = {}
    
    if action not in failed_attempts[ip]:
        failed_attempts[ip][action] = []
    
    failed_attempts[ip][action].append(current_time)

def get_client_ip():
    """Obtener IP real del cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def validate_csrf_token():
    """Validar token CSRF"""
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            return False
    return True

def generate_csrf_token():
    """Generar token CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = hashlib.sha256(os.urandom(32)).hexdigest()
    return session['csrf_token']

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id, p.nombre, p.precio, p.imagen, p.precio_original, p.descuento, 
               p.destacado, p.fecha_release, c.nombre as categoria_nombre
        FROM productos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        WHERE p.destacado = 1 
        LIMIT 10
    """)
    productos_db = cur.fetchall()
    cur.close()
    
    # Calcular fecha límite para productos nuevos (30 días)
    fecha_limite_nuevo = datetime.now() - timedelta(days=30)
    
    productos_destacados = []
    for prod in productos_db:
        # Determinar si es nuevo
        es_nuevo = False
        if prod['fecha_release']:
            es_nuevo = prod['fecha_release'] >= fecha_limite_nuevo.date()
        
        productos_destacados.append({
            'id': prod['id'],
            'nombre': prod['nombre'],
            'precio': float(prod['precio']),
            'imagen_url': url_for('static', filename='img/' + (prod['imagen'] or 'producto_destacado.png')),
            'precio_original': float(prod['precio_original']) if prod['precio_original'] else None,
            'descuento': int(prod['descuento']) if prod['descuento'] else None,
            'categoria': prod['categoria_nombre'] or 'Sin categoría',
            'es_nuevo': es_nuevo,
            'es_top_seller': bool(prod['destacado'])
        })
    return render_template('index.html', productos_destacados=productos_destacados)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener IP del cliente para rate limiting
        client_ip = get_client_ip()
        
        # Verificar rate limiting
        if not check_rate_limit(client_ip, 'login', max_attempts=5, window_minutes=15):
            flash('Demasiados intentos fallidos. Por favor espera 15 minutos antes de intentar de nuevo.', 'error')
            return render_template('Auth/login.html')
        
        # Validar CSRF token
        if not validate_csrf_token():
            flash('Error de seguridad. Por favor recarga la página e intenta de nuevo.', 'error')
            return render_template('Auth/login.html')
        
        email = clean_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        remember_me = 'remember_me' in request.form
        
        # Validaciones básicas
        if not email or not password:
            record_failed_attempt(client_ip, 'login')
            flash('Por favor completa todos los campos.', 'error')
            return render_template('Auth/login.html')
        
        if not validate_email(email):
            record_failed_attempt(client_ip, 'login')
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('Auth/login.html')
        
        # Validar longitud de contraseña
        if len(password) < 1 or len(password) > 128:
            record_failed_attempt(client_ip, 'login')
            flash('Credenciales inválidas.', 'error')
            return render_template('Auth/login.html')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, nombre, email, contrasena, tipo_usuario FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user and check_password_hash(user[3], password):
                # Configurar sesión
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[2]
                session['user_type'] = user[4]
                session['login_time'] = time.time()
                
                # Configurar sesión permanente si "recordarme" está marcado
                if remember_me:
                    session.permanent = True
                
                # Actualizar último login
                cur = mysql.connection.cursor()
                cur.execute("UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s", (user[0],))
                mysql.connection.commit()
                cur.close()
                
                # Limpiar intentos fallidos para esta IP
                if client_ip in failed_attempts and 'login' in failed_attempts[client_ip]:
                    del failed_attempts[client_ip]['login']
                
                flash('¡Bienvenido de vuelta!', 'success')
                if user[4] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('profile'))
            else:
                record_failed_attempt(client_ip, 'login')
                flash('Email o contraseña incorrectos.', 'error')
                
        except Exception as e:
            record_failed_attempt(client_ip, 'login')
            flash('Error al iniciar sesión. Por favor intenta de nuevo.', 'error')
            print(f"Error en login: {e}")
    
    # Generar nuevo token CSRF para el formulario
    csrf_token = generate_csrf_token()
    return render_template('Auth/login.html', csrf_token=csrf_token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener IP del cliente para rate limiting
        client_ip = get_client_ip()
        
        # Verificar rate limiting
        if not check_rate_limit(client_ip, 'register', max_attempts=3, window_minutes=60):
            flash('Demasiados intentos de registro. Por favor espera 1 hora antes de intentar de nuevo.', 'error')
            return render_template('Auth/register.html')
        
        # Validar CSRF token
        if not validate_csrf_token():
            flash('Error de seguridad. Por favor recarga la página e intenta de nuevo.', 'error')
            return render_template('Auth/register.html')
        
        nombre = clean_input(request.form.get('nombre', ''))
        email = clean_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        telefono = clean_input(request.form.get('telefono', ''))
        terms_accepted = 'terms' in request.form
        
        # Validaciones completas
        if not all([nombre, email, password, confirm_password]):
            record_failed_attempt(client_ip, 'register')
            flash('Por favor completa todos los campos obligatorios.', 'error')
            return render_template('Auth/register.html')
        
        # Validar nombre
        is_valid_nombre, nombre_message = validate_nombre(nombre)
        if not is_valid_nombre:
            record_failed_attempt(client_ip, 'register')
            flash(nombre_message, 'error')
            return render_template('Auth/register.html')
        
        # Validar email
        if not validate_email(email):
            record_failed_attempt(client_ip, 'register')
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('Auth/register.html')
        
        # Validar contraseña
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            record_failed_attempt(client_ip, 'register')
            flash(password_message, 'error')
            return render_template('Auth/register.html')
        
        # Verificar confirmación de contraseña
        if password != confirm_password:
            record_failed_attempt(client_ip, 'register')
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('Auth/register.html')
        
        # Validar teléfono si se proporciona
        if telefono:
            is_valid_telefono, telefono_message = validate_telefono(telefono)
            if not is_valid_telefono:
                record_failed_attempt(client_ip, 'register')
                flash(telefono_message, 'error')
                return render_template('Auth/register.html')
        
        # Verificar términos y condiciones
        if not terms_accepted:
            record_failed_attempt(client_ip, 'register')
            flash('Debes aceptar los términos y condiciones.', 'error')
            return render_template('Auth/register.html')
        
        try:
            cur = mysql.connection.cursor()
            
            # Verificar si el email ya existe
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cur.fetchone():
                record_failed_attempt(client_ip, 'register')
                flash('Este email ya está registrado.', 'error')
                cur.close()
                return render_template('Auth/register.html')
            
            # Crear nuevo usuario con validaciones adicionales
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256:260000')
            cur.execute("""
                INSERT INTO usuarios (nombre, email, contrasena, telefono, email_verificado, fecha_registro) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (nombre, email, hashed_password, telefono, True))
            mysql.connection.commit()
            
            user_id = cur.lastrowid
            cur.close()
            
            # Iniciar sesión automáticamente
            session['user_id'] = user_id
            session['user_name'] = nombre
            session['user_email'] = email
            session['user_type'] = 'cliente'
            
            flash('¡Cuenta creada exitosamente!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            flash('Error al crear la cuenta. Por favor intenta de nuevo.', 'error')
            print(f"Error en registro: {e}")
    
    return render_template('Auth/register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('home'))

@app.route('/login/google/authorized')
def google_login():
    if not google.authorized:
        flash('No se pudo autenticar con Google.', 'error')
        return redirect(url_for('login'))
    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Error al obtener datos de Google.', 'error')
        return redirect(url_for('login'))
    info = resp.json()
    # Aquí puedes buscar o crear el usuario en tu BD
    session['user_id'] = info['id']
    session['user_email'] = info['email']
    session['user_name'] = info.get('name', '')
    session['user_avatar'] = info.get('picture', '')
    flash('¡Bienvenido, has iniciado sesión con Google!', 'success')
    return redirect(url_for('index'))

@app.route('/login/facebook/authorized')
def facebook_login():
    if not facebook.authorized:
        flash('No se pudo autenticar con Facebook.', 'error')
        return redirect(url_for('login'))
    resp = facebook.get('/me?fields=id,name,email,picture')
    if not resp.ok:
        flash('Error al obtener datos de Facebook.', 'error')
        return redirect(url_for('login'))
    info = resp.json()
    session['user_id'] = info['id']
    session['user_email'] = info.get('email', '')
    session['user_name'] = info.get('name', '')
    session['user_avatar'] = info.get('picture', {}).get('data', {}).get('url', '')
    flash('¡Bienvenido, has iniciado sesión con Facebook!', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """Página del perfil del usuario"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nombre, email, direccion, telefono, tipo_usuario, fecha_registro, ultimo_login 
            FROM usuarios WHERE id = %s
        """, (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        
        if user:
            user_data = {
                'id': user[0],
                'nombre': user[1],
                'email': user[2],
                'direccion': user[3],
                'telefono': user[4],
                'tipo_usuario': user[5],
                'fecha_registro': user[6],
                'ultimo_login': user[7]
            }
            return render_template('profile.html', user=user_data)
        else:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('home'))
            
    except Exception as e:
        flash('Error al cargar el perfil.', 'error')
        print(f"Error en profile: {e}")
        return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperar contraseña"""
    if request.method == 'POST':
        email = request.form['email']
        
        if not validate_email(email):
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('forgot_password.html')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                # En producción, aquí se enviaría un email con un enlace para resetear la contraseña
                flash('Se ha enviado un enlace de recuperación a tu email.', 'success')
            else:
                flash('No se encontró una cuenta con este email.', 'error')
                
        except Exception as e:
            flash('Error al procesar la solicitud.', 'error')
            print(f"Error en forgot_password: {e}")
    
    return render_template('forgot_password.html')

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').strip()
    resultados = []
    if query:
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, nombre, descripcion, precio, imagen FROM productos
                WHERE nombre LIKE %s OR descripcion LIKE %s
            """, (f"%{query}%", f"%{query}%"))
            resultados = cur.fetchall()
            cur.close()
        except Exception as e:
            flash('Error al buscar productos.', 'error')
            print(f"Error en búsqueda: {e}")
    return render_template('buscar.html', query=query, resultados=resultados)

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/tienda')
def tienda():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, nombre FROM categorias')
    categorias = [{'id': row['id'], 'nombre': row['nombre']} for row in cur.fetchall()]
    cur.execute('SELECT MIN(precio) as min_precio, MAX(precio) as max_precio FROM productos')
    precio_data = cur.fetchone()
    filtro_precio = {'min': int(precio_data['min_precio'] or 0), 'max': int(precio_data['max_precio'] or 0)}

    # Obtener productos con categoría y banderas
    cur.execute("""
        SELECT p.id, p.nombre, p.precio, p.imagen, p.precio_original, p.descuento, 
               p.destacado, p.fecha_release, c.nombre as categoria_nombre
        FROM productos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    productos_db = cur.fetchall()
    cur.close()
    
    # Calcular fecha límite para productos nuevos (30 días)
    fecha_limite_nuevo = datetime.now() - timedelta(days=30)
    
    products = []
    for prod in productos_db:
        # Determinar si es nuevo
        es_nuevo = False
        if prod['fecha_release']:
            es_nuevo = prod['fecha_release'] >= fecha_limite_nuevo.date()
        
        products.append({
            'id': prod['id'],
            'nombre': prod['nombre'],
            'precio': float(prod['precio']),
            'imagen': prod['imagen'] or 'producto_destacado.png',
            'precio_original': float(prod['precio_original']) if prod['precio_original'] else None,
            'descuento': int(prod['descuento']) if prod['descuento'] else None,
            'categoria': prod['categoria_nombre'] or 'Sin categoría',
            'es_nuevo': es_nuevo,
            'es_top_seller': bool(prod['destacado'])
        })
    return render_template('tienda.html', categorias=categorias, filtro_precio=filtro_precio, products=products)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        asunto = request.form.get('asunto', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        
        # Validaciones
        if not all([nombre, apellido, email, asunto, mensaje]):
            flash('Por favor completa todos los campos.', 'error')
            return render_template('contacto.html')
        
        if not validate_email(email):
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('contacto.html')
        
        try:
            # Guardar mensaje en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO mensajes_contacto (nombre, apellido, email, asunto, mensaje, fecha_envio)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (nombre, apellido, email, asunto, mensaje))
            mysql.connection.commit()
            mensaje_id = cur.lastrowid
            cur.close()
            
            # Enviar email de confirmación al usuario
            html_body_usuario = render_template_string("""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #22c55e;">¡Gracias por contactarnos, {{ nombre }} {{ apellido }}!</h2>
                <p>Hemos recibido tu mensaje y nos pondremos en contacto contigo pronto.</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Detalles de tu mensaje:</h3>
                    <p><strong>Asunto:</strong> {{ asunto }}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p style="background: white; padding: 15px; border-radius: 5px;">{{ mensaje }}</p>
                </div>
                <p>Número de referencia: <strong>#{{ mensaje_id }}</strong></p>
                <p>Te responderemos a: <strong>{{ email }}</strong></p>
                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Este es un mensaje automático. Por favor no respondas a este email.
                </p>
            </div>
            """, nombre=nombre, apellido=apellido, asunto=asunto, mensaje=mensaje, mensaje_id=mensaje_id, email=email)
            
            msg_usuario = Message(
                subject=f"Confirmación de mensaje - {asunto}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                html=html_body_usuario
            )
            mail.send(msg_usuario)
            
            # Enviar notificación al administrador
            html_body_admin = render_template_string("""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #dc2626;">Nuevo mensaje de contacto</h2>
                <div style="background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626;">
                    <p><strong>De:</strong> {{ nombre }} {{ apellido }}</p>
                    <p><strong>Email:</strong> {{ email }}</p>
                    <p><strong>Asunto:</strong> {{ asunto }}</p>
                    <p><strong>Mensaje:</strong></p>
                    <p style="background: white; padding: 15px; border-radius: 5px;">{{ mensaje }}</p>
                    <p><strong>ID:</strong> #{{ mensaje_id }}</p>
                    <p><strong>Fecha:</strong> {{ fecha }}</p>
                </div>
            </div>
            """, nombre=nombre, apellido=apellido, email=email, asunto=asunto, mensaje=mensaje, mensaje_id=mensaje_id, fecha=datetime.now().strftime('%d/%m/%Y %H:%M'))
            
            msg_admin = Message(
                subject=f"Nuevo mensaje de contacto: {asunto}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['MAIL_USERNAME']],  # Enviar al email del admin
                html=html_body_admin
            )
            mail.send(msg_admin)
            
            flash('¡Mensaje enviado exitosamente! Te hemos enviado una confirmación por email.', 'success')
            return redirect(url_for('contacto'))
            
        except Exception as e:
            flash('Error al enviar el mensaje. Por favor intenta de nuevo.', 'error')
            print(f"Error en contacto: {e}")
    
    return render_template('contacto.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

def verificar_suscripcion(correo):
    """Verifica si un correo está suscrito en la base de datos"""
    if not correo:
        return False
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM suscriptores WHERE correo = %s', (correo,))
        existe = cur.fetchone()
        cur.close()
        return existe is not None
    except Exception as e:
        print(f"Error verificando suscripción: {e}")
        return False

@app.route('/comunidad')
def comunidad():
    # Verificar si hay correo en sesión y si está suscrito
    correo_sesion = session.get('suscriptor_email')
    if not correo_sesion or not verificar_suscripcion(correo_sesion):
        flash('Debes suscribirte para acceder a la comunidad.', 'error')
        return redirect(url_for('home'))
    blogs = [
        {
            'id': 1,
            'titulo': 'Tendencias de maquillaje 2024',
            'resumen': 'Descubre los colores y estilos que marcarán el año en el mundo de la belleza.',
            'imagen': 'blog1.jpg',
            'categoria': 'Maquillaje',
            'autor': 'Equipo bycint',
            'fecha_publicacion': '2024-01-10'
        },
        {
            'id': 2,
            'titulo': 'Rutina de cuidado facial para piel radiante',
            'resumen': 'Tips y productos recomendados para mantener tu piel saludable y luminosa.',
            'imagen': 'blog2.jpg',
            'categoria': 'Cuidado de la piel',
            'autor': 'Dra. Camila Torres',
            'fecha_publicacion': '2024-02-05'
        },
        {
            'id': 3,
            'titulo': 'Cosmética natural: ¿por qué elegirla?',
            'resumen': 'Beneficios de los productos naturales y cómo incorporarlos en tu rutina.',
            'imagen': 'blog3.jpg',
            'categoria': 'Cosmética natural',
            'autor': 'Equipo bycint',
            'fecha_publicacion': '2024-03-01'
        },
        {
            'id': 4,
            'titulo': 'Guía de perfumes para cada ocasión',
            'resumen': 'Elige la fragancia perfecta para cada momento especial.',
            'imagen': 'perfume_mujer.png',
            'categoria': 'Perfumes',
            'autor': 'Ana Fragancia',
            'fecha_publicacion': '2024-03-15'
        },
        {
            'id': 5,
            'titulo': 'Cómo elegir la joyería ideal para tu look',
            'resumen': 'Consejos para combinar joyas y resaltar tu estilo.',
            'imagen': 'collar_plata.png',
            'categoria': 'Joyería',
            'autor': 'Estilo bycint',
            'fecha_publicacion': '2024-04-01'
        },
        {
            'id': 6,
            'titulo': 'Accesorios imprescindibles para tu rutina de belleza',
            'resumen': 'Descubre los accesorios que no pueden faltar en tu tocador.',
            'imagen': 'set_brochas.png',
            'categoria': 'Accesorios',
            'autor': 'Equipo bycint',
            'fecha_publicacion': '2024-04-10'
        },
        {
            'id': 7,
            'titulo': 'Labios perfectos: guía de pintalabios',
            'resumen': 'Cómo elegir el pintalabios ideal según tu tono de piel.',
            'imagen': 'labial_liquido.png',
            'categoria': 'Pintalabios',
            'autor': 'Makeup Pro',
            'fecha_publicacion': '2024-04-20'
        },
        {
            'id': 8,
            'titulo': 'Sets de maquillaje: ¿cuál es el mejor para ti?',
            'resumen': 'Comparativa de los sets más populares y sus ventajas.',
            'imagen': 'set_esenciales.png',
            'categoria': 'Sets',
            'autor': 'Equipo bycint',
            'fecha_publicacion': '2024-05-01'
        },
        {
            'id': 9,
            'titulo': 'Errores comunes en el cuidado de la piel',
            'resumen': 'Evita estos errores y mejora tu rutina facial.',
            'imagen': 'crema_dia.png',
            'categoria': 'Cuidado de la piel',
            'autor': 'Dra. Camila Torres',
            'fecha_publicacion': '2024-05-10'
        },
        {
            'id': 10,
            'titulo': 'Tendencias en accesorios 2024',
            'resumen': 'Lo último en accesorios de belleza y moda.',
            'imagen': 'categoria_accesorios.png',
            'categoria': 'Accesorios',
            'autor': 'Estilo bycint',
            'fecha_publicacion': '2024-05-15'
        },
        {
            'id': 11,
            'titulo': 'Maquillaje para eventos especiales',
            'resumen': 'Tips para un look impactante en fiestas y celebraciones.',
            'imagen': 'paleta_sombras.png',
            'categoria': 'Maquillaje',
            'autor': 'Makeup Pro',
            'fecha_publicacion': '2024-05-20'
        },
        {
            'id': 12,
            'titulo': 'Perfumes unisex: los favoritos del año',
            'resumen': 'Fragancias que conquistan a todos.',
            'imagen': 'perfume_mujer.png',
            'categoria': 'Perfumes',
            'autor': 'Ana Fragancia',
            'fecha_publicacion': '2024-05-25'
        },
        {
            'id': 13,
            'titulo': 'Joyería minimalista: menos es más',
            'resumen': 'La tendencia minimalista en joyas y cómo llevarla.',
            'imagen': 'collar_plata.png',
            'categoria': 'Joyería',
            'autor': 'Estilo bycint',
            'fecha_publicacion': '2024-06-01'
        },
        {
            'id': 14,
            'titulo': 'Brochas y esponjas: ¿cómo elegirlas?',
            'resumen': 'Guía para seleccionar los mejores accesorios de aplicación.',
            'imagen': 'set_brochas.png',
            'categoria': 'Accesorios',
            'autor': 'Equipo bycint',
            'fecha_publicacion': '2024-06-05'
        },
        {
            'id': 15,
            'titulo': 'Pintalabios mate vs. brillante',
            'resumen': 'Ventajas y desventajas de cada acabado.',
            'imagen': 'labial_liquido.png',
            'categoria': 'Pintalabios',
            'autor': 'Makeup Pro',
            'fecha_publicacion': '2024-06-10'
        },
    ]
    return render_template('comunidad.html', blogs=blogs)

@app.route('/suscribirse', methods=['POST'])
def suscribirse():
    correo = request.form.get('correo', '').strip().lower()
    if not correo:
        flash('Por favor ingresa un correo electrónico válido.', 'error')
        return redirect(url_for('home'))
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM suscriptores WHERE correo = %s', (correo,))
        existe = cur.fetchone()
        if existe:
            flash('Este correo ya está suscrito a la comunidad.', 'info')
        else:
            cur.execute('INSERT INTO suscriptores (correo) VALUES (%s)', (correo,))
            mysql.connection.commit()
            flash('¡Te has suscrito exitosamente a la comunidad!', 'success')
        cur.close()
        # Guardar el correo en sesión para acceso a la comunidad
        session['suscriptor_email'] = correo
    except Exception as e:
        flash('Ocurrió un error al suscribirte. Intenta nuevamente.', 'error')
        print(f"Error en suscripción: {e}")
    return redirect(url_for('home'))

@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
def blog_detalle(blog_id):
    # Verificar si hay correo en sesión y si está suscrito
    correo_sesion = session.get('suscriptor_email')
    if not correo_sesion or not verificar_suscripcion(correo_sesion):
        flash('Debes suscribirte para acceder a la comunidad.', 'error')
        return redirect(url_for('home'))
    
    blog = next((b for b in blogs_demo if b['id'] == blog_id), None)
    if not blog:
        flash('El blog no existe.', 'error')
        return redirect(url_for('comunidad'))
    comentarios = comentarios_demo.get(blog_id, [])
    if request.method == 'POST':
        comentario = request.form.get('comentario', '').strip()
        puntuacion = int(request.form.get('puntuacion', 0))
        usuario = session.get('suscriptor_email', 'Anónimo')
        if comentario and 1 <= puntuacion <= 5:
            comentarios_demo.setdefault(blog_id, []).append({
                'usuario': usuario,
                'comentario': comentario,
                'puntuacion': puntuacion
            })
            flash('¡Comentario enviado!', 'success')
        else:
            flash('Debes escribir un comentario y seleccionar una puntuación.', 'error')
        return redirect(url_for('blog_detalle', blog_id=blog_id))
    return render_template('blog_detalle.html', blog=blog, comentarios=comentarios)

@app.route('/categoria/<nombre_categoria>')
def catalogo_categoria(nombre_categoria):
    mapeo_categorias = {
        'sets': 'Sets',
        'maquillaje': 'Maquillaje',
        'perfume': 'Perfumes',
        'perfumes': 'Perfumes',
        'joyeria': 'Joyería',
        'pintalabios': 'Pintalabios',
        'cuidado_de_la_piel': 'Cuidado de la piel',
        'cuidado-piel': 'Cuidado de la piel',
        'accesorios': 'Accesorios',
    }
    nombre_categoria_db = mapeo_categorias.get(nombre_categoria.lower(), nombre_categoria.capitalize())

    filtros_por_categoria = {
        'sets': [
            {'nombre': 'Acabado', 'opciones': ['Mate', 'Brillante', 'Satinado']},
            {'nombre': 'Líneas', 'opciones': ['Línea 1', 'Línea 2']},
            {'nombre': 'Lugar Aplicación', 'opciones': ['Rostro', 'Ojos', 'Labios']},
        ],
        'maquillaje': [
            {'nombre': 'Tipo', 'opciones': ['Bases', 'Sombras', 'Rubores', 'Delineadores', 'Labiales']},
            {'nombre': 'Acabado', 'opciones': ['Mate', 'Brillante', 'Satinado']},
            {'nombre': 'Tonos', 'opciones': ['Claros', 'Medios', 'Oscuros']},
        ],
        'perfumes': [
            {'nombre': 'Género', 'opciones': ['Mujer', 'Hombre', 'Unisex']},
            {'nombre': 'Concentración', 'opciones': ['Eau de Parfum', 'Eau de Toilette', 'Perfume']},
            {'nombre': 'Familia Olfativa', 'opciones': ['Floral', 'Cítrica', 'Oriental', 'Amaderada']},
        ],
        'joyeria': [
            {'nombre': 'Tipo', 'opciones': ['Collares', 'Pulseras', 'Anillos', 'Aretes']},
            {'nombre': 'Material', 'opciones': ['Plata', 'Oro', 'Acero', 'Fantasía']},
            {'nombre': 'Estilo', 'opciones': ['Elegante', 'Casual', 'Vintage', 'Moderno']},
        ],
        'pintalabios': [
            {'nombre': 'Tipo', 'opciones': ['Líquidos', 'Barra', 'Gloss']},
            {'nombre': 'Acabado', 'opciones': ['Mate', 'Brillante', 'Satinado']},
            {'nombre': 'Duración', 'opciones': ['Larga duración', 'Media duración', 'Temporal']},
        ],
        'cuidado de la piel': [
            {'nombre': 'Tipo de Piel', 'opciones': ['Normal', 'Seca', 'Grasa', 'Mixta', 'Sensible']},
            {'nombre': 'Función', 'opciones': ['Hidratante', 'Antiedad', 'Antiacné', 'Iluminador', 'Protector']},
            {'nombre': 'Consistencia', 'opciones': ['Crema', 'Gel', 'Serum', 'Aceite', 'Mascarilla']},
        ],
        'accesorios': [
            {'nombre': 'Tipo', 'opciones': ['Brochas', 'Esponjas', 'Espejos', 'Organizadores', 'Bolsos']},
            {'nombre': 'Material', 'opciones': ['Sintético', 'Natural', 'Plástico', 'Metal', 'Tela']},
            {'nombre': 'Uso', 'opciones': ['Maquillaje', 'Cuidado facial', 'Organización', 'Viaje']},
        ],
    }
    filtro_precio = {'min': 20, 'max': 200}

    cur = mysql.connection.cursor()
    print(f"Buscando categoría: {nombre_categoria_db.lower()}")
    cur.execute("SELECT id, nombre FROM categorias WHERE LOWER(nombre) = %s", (nombre_categoria_db.lower(),))
    categoria = cur.fetchone()
    if not categoria:
        print(f"Categoría no encontrada en la base de datos: {nombre_categoria_db.lower()}")
        cur.close()
        flash(f'Categoría no encontrada: {nombre_categoria_db}', 'error')
        return redirect(url_for('home'))
    categoria_id = categoria['id']
    nombre_categoria_db = categoria['nombre']

    # Leer filtros de la URL
    tipo = request.args.get('tipo')
    genero = request.args.get('genero')
    material = request.args.get('material')

    # Consulta precisa por campos específicos
    query = """
        SELECT p.nombre, p.precio, p.imagen, p.id, p.precio_original, p.descuento,
               p.destacado, p.fecha_release, c.nombre as categoria_nombre
        FROM productos p 
        LEFT JOIN categorias c ON p.categoria_id = c.id 
        WHERE p.categoria_id = %s
    """
    params = [categoria_id]
    if tipo:
        query += " AND p.tipo = %s"
        params.append(tipo)
    if genero:
        query += " AND p.genero = %s"
        params.append(genero)
    if material:
        query += " AND p.material = %s"
        params.append(material)

    cur.execute(query, tuple(params))
    productos_db = cur.fetchall()
    cur.close()
    
    # Calcular fecha límite para productos nuevos (30 días)
    fecha_limite_nuevo = datetime.now() - timedelta(days=30)
    
    productos = []
    for prod in productos_db:
        # Determinar si es nuevo
        es_nuevo = False
        if prod['fecha_release']:
            es_nuevo = prod['fecha_release'] >= fecha_limite_nuevo.date()
        
        productos.append({
            'nombre': prod['nombre'],
            'precio': prod['precio'],
            'precio_original': float(prod['precio_original']) if prod['precio_original'] else None,
            'descuento': int(prod['descuento']) if prod['descuento'] else None,
            'imagen': prod['imagen'] or 'producto_destacado.png',
            'id': prod['id'],
            'categoria': prod['categoria_nombre'] or 'Sin categoría',
            'es_nuevo': es_nuevo,
            'es_top_seller': bool(prod['destacado'])
        })

    filtros = filtros_por_categoria.get(nombre_categoria_db.lower(), [])

    return render_template('categoria.html', categoria=nombre_categoria_db, productos=productos, filtros=filtros, filtro_precio=filtro_precio)

@app.route('/api/productos')
def api_productos():
    categorias = request.args.getlist('categoria')
    oferta = request.args.get('oferta')
    novedad = request.args.get('novedad')
    precio_max = request.args.get('precio', type=float)
    orden = request.args.get('orden', 'relevancia')

    query = """
        SELECT p.nombre, p.precio, p.imagen, p.id, p.precio_original, p.descuento, 
               p.fecha_release, p.destacado, c.nombre as categoria_nombre
        FROM productos p 
        JOIN categorias c ON p.categoria_id = c.id 
        WHERE 1=1
    """
    params = []
    if categorias:
        query += " AND c.nombre IN (%s)" % (', '.join(['%s'] * len(categorias)))
        params.extend(categorias)
    if oferta:
        query += " AND p.descuento IS NOT NULL AND p.descuento > 0"
    if novedad:
        query += " AND p.destacado = 1"
    if precio_max:
        query += " AND p.precio <= %s"
        params.append(precio_max)

    # Ordenamiento
    if orden == 'fecha':
        query += " ORDER BY p.fecha_release DESC"
    elif orden == 'descuento':
        query += " ORDER BY p.descuento DESC"
    elif orden == 'mayor':
        query += " ORDER BY p.precio DESC"
    elif orden == 'menor':
        query += " ORDER BY p.precio ASC"
    else:
        query += " ORDER BY p.id DESC"  # Relevancia por defecto

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    productos_db = cur.fetchall()
    cur.close()
    
    # Calcular fecha límite para productos nuevos (30 días)
    fecha_limite_nuevo = datetime.now() - timedelta(days=30)
    
    productos = []
    for prod in productos_db:
        # Determinar si es nuevo
        es_nuevo = False
        if prod['fecha_release']:
            es_nuevo = prod['fecha_release'] >= fecha_limite_nuevo.date()
        
        productos.append({
            'nombre': prod['nombre'],
            'precio': float(prod['precio']),
            'imagen': prod['imagen'] or 'producto_destacado.png',
            'id': prod['id'],
            'precio_original': float(prod['precio_original']) if prod['precio_original'] else None,
            'descuento': int(prod['descuento']) if prod['descuento'] else None,
            'fecha_release': prod['fecha_release'].isoformat() if prod['fecha_release'] else None,
            'categoria': prod['categoria_nombre'] or 'Sin categoría',
            'es_nuevo': es_nuevo,
            'es_top_seller': bool(prod['destacado'])
        })
    return jsonify({'productos': productos})

@app.route('/api/productos_categoria')
def api_productos_categoria():
    categoria = request.args.get('categoria')
    tipos = request.args.getlist('tipo')
    acabados = request.args.getlist('acabado')
    materiales = request.args.getlist('material')
    generos = request.args.getlist('genero')
    precio_max = request.args.get('precio', type=float)

    query = """
        SELECT p.nombre, p.precio, p.imagen, p.id, p.precio_original, p.descuento,
               p.destacado, p.fecha_release, c.nombre as categoria_nombre
        FROM productos p 
        JOIN categorias c ON p.categoria_id = c.id 
        WHERE 1=1
    """
    params = []
    if categoria:
        query += " AND c.nombre = %s"
        params.append(categoria)
    if tipos:
        if len(tipos) == 1:
            query += " AND p.tipo = %s"
            params.append(tipos[0])
        else:
            query += " AND p.tipo IN (%s)" % (', '.join(['%s'] * len(tipos)))
            params.extend(tipos)
    if acabados:
        if len(acabados) == 1:
            query += " AND p.acabado = %s"
            params.append(acabados[0])
        else:
            query += " AND p.acabado IN (%s)" % (', '.join(['%s'] * len(acabados)))
            params.extend(acabados)
    if materiales:
        if len(materiales) == 1:
            query += " AND p.material = %s"
            params.append(materiales[0])
        else:
            query += " AND p.material IN (%s)" % (', '.join(['%s'] * len(materiales)))
            params.extend(materiales)
    if generos:
        if len(generos) == 1:
            query += " AND p.genero = %s"
            params.append(generos[0])
        else:
            query += " AND p.genero IN (%s)" % (', '.join(['%s'] * len(generos)))
            params.extend(generos)
    if precio_max:
        query += " AND p.precio <= %s"
        params.append(precio_max)

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    productos_db = cur.fetchall()
    cur.close()
    
    # Calcular fecha límite para productos nuevos (30 días)
    fecha_limite_nuevo = datetime.now() - timedelta(days=30)
    
    productos = []
    for prod in productos_db:
        # Determinar si es nuevo
        es_nuevo = False
        if prod['fecha_release']:
            es_nuevo = prod['fecha_release'] >= fecha_limite_nuevo.date()
        
        productos.append({
            'nombre': prod['nombre'],
            'precio': float(prod['precio']),
            'imagen': prod['imagen'] or 'producto_destacado.png',
            'id': prod['id'],
            'precio_original': float(prod['precio_original']) if prod['precio_original'] else None,
            'descuento': int(prod['descuento']) if prod['descuento'] else None,
            'categoria': prod['categoria_nombre'] or 'Sin categoría',
            'es_nuevo': es_nuevo,
            'es_top_seller': bool(prod['destacado'])
        })
    return jsonify({'productos': productos})

@app.route('/legal/privacidad')
def legal_privacidad():
    return render_template('legal/privacidad.html')

@app.route('/legal/terminos')
def legal_terminos():
    return render_template('legal/terminos.html')

@app.route('/legal/envios')
def legal_envios():
    return render_template('legal/envios.html')

@app.route('/legal/cambios')
def legal_cambios():
    return render_template('legal/cambios.html')

@app.route('/mis-pedidos')
@login_required
def mis_pedidos():
    # Ejemplo de datos de pedidos
    pedidos = [
        {
            'id': 101,
            'fecha': '2024-06-26',
            'total': 210.50,
            'estado': 'Enviado',
            'puntos': 10,
            'progreso': 80,
            'seguimiento': 'En camino',
            'productos': [
                {'nombre': 'Set de Maquillaje', 'cantidad': 1, 'subtotal': 110.50, 'imagen': 'categoria_maquillaje.png'},
                {'nombre': 'Perfume Floral', 'cantidad': 2, 'subtotal': 100.00, 'imagen': 'categoria_cuidado.png'},
            ]
        },
        {
            'id': 102,
            'fecha': '2024-06-20',
            'total': 95.00,
            'estado': 'Entregado',
            'puntos': 0,
            'progreso': 100,
            'seguimiento': 'Entregado',
            'productos': [
                {'nombre': 'Set de Brochas', 'cantidad': 1, 'subtotal': 95.00, 'imagen': 'categoria_accesorios.png'},
            ]
        },
    ]
    puntos = sum(p['puntos'] for p in pedidos)
    return render_template('mis_pedidos.html', pedidos=pedidos, puntos=puntos)

@app.route('/api/guardar_pedido', methods=['POST'])
def guardar_pedido():
    data = request.json
    usuario_id = session.get('user_id') if 'user_id' in session else None
    total = float(data.get('total', 0))
    productos = data.get('products', [])

    cur = mysql.connection.cursor()
    # Guarda el pedido
    cur.execute(
        "INSERT INTO pedidos (usuario_id, total, estado) VALUES (%s, %s, %s)",
        (usuario_id, total, 'pendiente')
    )
    pedido_id = cur.lastrowid

    # Guarda el detalle de cada producto
    for prod in productos:
        cur.execute(
            "INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            (pedido_id, prod['id'], prod.get('cantidad', 1), prod['price'])
        )
    mysql.connection.commit()
    cur.close()

    # Enviar correo de confirmación en HTML
    html_body = render_template_string("""
    <h2 style="color:#4F46E5;">¡Gracias por tu compra, {{ nombre }}!</h2>
    <p>Hemos recibido tu pedido <b>#{{ pedido_id }}</b> por un total de <b>S/ {{ total }}</b>.</p>
    <h3>Resumen de tu pedido:</h3>
    <ul>
    {% for prod in productos %}
      <li>
        <b>{{ prod['name'] }}</b> x{{ prod.get('cantidad', 1) }} - S/ {{ '%.2f' % (prod['price'] * prod.get('cantidad', 1)) }}
      </li>
    {% endfor %}
    </ul>
    <p>Te avisaremos cuando tu pedido sea enviado.<br>
    ¡Gracias por confiar en nosotros!</p>
    """, nombre=data.get('firstName', ''), pedido_id=pedido_id, total=total, productos=productos)
    try:
        msg = Message(
            subject="¡Gracias por tu pedido!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[data.get('email')],
            html=html_body
        )
        mail.send(msg)
    except Exception as e:
        print('Error enviando correo:', e)

    return jsonify({'success': True, 'pedido_id': pedido_id})

@app.route('/pedido/<int:pedido_id>')
def detalle_pedido(pedido_id):
    usuario_id = session.get('user_id')
    cur = mysql.connection.cursor()
    # Trae el pedido solo si pertenece al usuario
    cur.execute("SELECT id, fecha, total, estado FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    pedido = cur.fetchone()
    if not pedido:
        return "Pedido no encontrado", 404
    # Trae los productos
    cur.execute("""
        SELECT p.nombre, dp.cantidad, dp.precio_unitario, p.imagen
        FROM detalle_pedido dp
        JOIN productos p ON dp.producto_id = p.id
        WHERE dp.pedido_id = %s
    """, (pedido_id,))
    productos = []
    for prod in cur.fetchall():
        productos.append({
            'nombre': prod[0],
            'cantidad': prod[1],
            'subtotal': float(prod[2]) * prod[1],
            'precio_unitario': float(prod[2]),
            'imagen': prod[3] or 'producto_destacado.png'
        })
    cur.close()
    return render_template('detalle_pedido.html', pedido={
        'id': pedido[0],
        'fecha': pedido[1].strftime('%Y-%m-%d'),
        'total': float(pedido[2]),
        'estado': pedido[3],
        'productos': productos
    })

@app.route('/api/agregar_carrito', methods=['POST'])
def api_agregar_carrito():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para agregar al carrito.'}), 401
    data = request.get_json()
    producto_id = data.get('producto_id')
    if not producto_id:
        return jsonify({'success': False, 'message': 'ID de producto faltante.'}), 400
    try:
        cur = mysql.connection.cursor()
        # Verificar que el producto existe
        cur.execute("SELECT id FROM productos WHERE id = %s", (producto_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'success': False, 'message': 'El producto no existe.'}), 404
        # Verificar si ya existe en el carrito
        cur.execute("SELECT cantidad FROM carrito WHERE usuario_id = %s AND producto_id = %s", (session['user_id'], producto_id))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE carrito SET cantidad = cantidad + 1 WHERE usuario_id = %s AND producto_id = %s", (session['user_id'], producto_id))
        else:
            cur.execute("INSERT INTO carrito (usuario_id, producto_id, cantidad) VALUES (%s, %s, %s)", (session['user_id'], producto_id, 1))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Producto agregado al carrito.'})
    except Exception as e:
        print('Error al agregar al carrito:', e)
        return jsonify({'success': False, 'message': 'Error al agregar al carrito.'}), 500

@app.route('/api/carrito')
def api_carrito():
    if 'user_id' not in session:
        return jsonify({'cantidad': 0, 'productos': []})
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT p.id, p.nombre, p.precio, p.imagen, c.cantidad
        FROM carrito c
        JOIN productos p ON c.producto_id = p.id
        WHERE c.usuario_id = %s
    ''', (session['user_id'],))
    productos = []
    cantidad_total = 0
    for row in cur.fetchall():
        subtotal = float(row[2]) * row[4]
        productos.append({
            'id': row[0],
            'nombre': row[1],
            'precio': float(row[2]),
            'imagen': row[3] or 'producto_destacado.png',
            'cantidad': row[4],
            'subtotal': subtotal
        })
        cantidad_total += row[4]
    cur.close()
    return jsonify({'cantidad': cantidad_total, 'productos': productos})

@app.route('/api/eliminar_carrito', methods=['POST'])
def api_eliminar_carrito():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión.'}), 401
    data = request.get_json()
    producto_id = data.get('producto_id')
    if not producto_id:
        return jsonify({'success': False, 'message': 'ID de producto faltante.'}), 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM carrito WHERE usuario_id = %s AND producto_id = %s", (session['user_id'], producto_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        print('Error al eliminar del carrito:', e)
        return jsonify({'success': False, 'message': 'Error al eliminar del carrito.'}), 500

@app.route('/api/cambiar_cantidad_carrito', methods=['POST'])
def api_cambiar_cantidad_carrito():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión.'}), 401
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad')
    if not producto_id or cantidad is None:
        return jsonify({'success': False, 'message': 'Datos faltantes.'}), 400
    try:
        cur = mysql.connection.cursor()
        if int(cantidad) <= 0:
            cur.execute("DELETE FROM carrito WHERE usuario_id = %s AND producto_id = %s", (session['user_id'], producto_id))
        else:
            cur.execute("UPDATE carrito SET cantidad = %s WHERE usuario_id = %s AND producto_id = %s", (cantidad, session['user_id'], producto_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        print('Error al cambiar cantidad en carrito:', e)
        return jsonify({'success': False, 'message': 'Error al cambiar cantidad.'}), 500

@app.route('/api/aplicar_cupon', methods=['POST'])
def aplicar_cupon():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para aplicar cupones.'}), 401
    
    data = request.get_json()
    cupon = data.get('cupon', '').strip().upper()
    
    if not cupon:
        return jsonify({'success': False, 'message': 'Código de cupón requerido.'})
    
    try:
        cur = mysql.connection.cursor()
        
        # Verificar si el cupón existe y está activo
        cur.execute("""
            SELECT id, descuento, tipo, uso_maximo, usos_actuales, fecha_expiracion 
            FROM cupones WHERE codigo = %s AND activo = TRUE
        """, (cupon,))
        cupon_data = cur.fetchone()
        
        if not cupon_data:
            cur.close()
            return jsonify({'success': False, 'message': 'Cupón inválido o inactivo.'})
        
        cupon_id, descuento, tipo, uso_maximo, usos_actuales, fecha_expiracion = cupon_data
        
        # Verificar fecha de expiración
        if fecha_expiracion and fecha_expiracion < datetime.now().date():
            cur.close()
            return jsonify({'success': False, 'message': 'Cupón expirado.'})
        
        # Verificar límite de usos
        if uso_maximo and usos_actuales >= uso_maximo:
            cur.close()
            return jsonify({'success': False, 'message': 'Cupón agotado.'})
        
        # Verificar si el usuario ya usó este cupón
        cur.execute("""
            SELECT COUNT(*) FROM cupones_usados 
            WHERE cupon_id = %s AND usuario_id = %s
        """, (cupon_id, session['user_id']))
        ya_usado = cur.fetchone()[0] > 0
        
        if ya_usado:
            cur.close()
            return jsonify({'success': False, 'message': 'Ya usaste este cupón anteriormente.'})
        
        # Obtener total del carrito
        cur.execute("""
            SELECT SUM(p.precio * c.cantidad) 
            FROM carrito c 
            JOIN productos p ON c.producto_id = p.id 
            WHERE c.usuario_id = %s
        """, (session['user_id'],))
        total_carrito = cur.fetchone()[0] or 0
        
        # Calcular descuento
        if tipo == 'porcentaje':
            monto_descuento = total_carrito * (descuento / 100)
        else:  # tipo == 'fijo'
            monto_descuento = descuento
        
        total_final = total_carrito - monto_descuento
        
        # Guardar uso del cupón
        cur.execute("""
            INSERT INTO cupones_usados (cupon_id, usuario_id, fecha_uso, monto_descuento)
            VALUES (%s, %s, %s, %s)
        """, (cupon_id, session['user_id'], datetime.now(), monto_descuento))
        
        # Actualizar contador de usos
        cur.execute("""
            UPDATE cupones SET usos_actuales = usos_actuales + 1 WHERE id = %s
        """, (cupon_id,))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': f'Cupón aplicado correctamente. Descuento: S/ {monto_descuento:.2f}',
            'descuento': monto_descuento,
            'total': total_final
        })
        
    except Exception as e:
        print('Error al aplicar cupón:', e)
        return jsonify({'success': False, 'message': 'Error al aplicar el cupón.'}), 500

@app.route('/api/calcular_envio', methods=['POST'])
def calcular_envio():
    """Calcular costo de envío basado en ubicación y productos"""
    try:
        data = request.get_json()
        carrito_items = data.get('items', [])
        direccion = data.get('direccion', {})
        
        if not carrito_items:
            return jsonify({'success': False, 'message': 'Carrito vacío'})
        
        # Calcular peso total del carrito
        peso_total = 0
        for item in carrito_items:
            cur = mysql.connection.cursor()
            cur.execute('SELECT peso FROM productos WHERE id = %s', (item['id'],))
            result = cur.fetchone()
            cur.close()
            
            if result:
                peso_producto = float(result[0] or 0)
                peso_total += peso_producto * item['cantidad']
        
        # Buscar zona de envío
        zona_id = buscar_zona_envio(direccion)
        if not zona_id:
            return jsonify({'success': False, 'message': 'Zona de envío no disponible'})
        
        # Obtener opciones de envío
        opciones_envio = obtener_opciones_envio(zona_id, peso_total)
        
        return jsonify({
            'success': True,
            'opciones': opciones_envio,
            'peso_total': peso_total
        })
        
    except Exception as e:
        print('Error al calcular envío:', e)
        return jsonify({'success': False, 'message': 'Error al calcular envío'})

def buscar_zona_envio(direccion):
    """Buscar zona de envío basada en la dirección"""
    try:
        departamento = direccion.get('departamento', '').strip()
        provincia = direccion.get('provincia', '').strip()
        distrito = direccion.get('distrito', '').strip()
        codigo_postal = direccion.get('codigo_postal', '').strip()
        
        cur = mysql.connection.cursor()
        
        # Buscar por código postal primero
        if codigo_postal:
            cur.execute('''
                SELECT id FROM zonas_envio 
                WHERE codigo_postal = %s AND activo = TRUE
            ''', (codigo_postal,))
            result = cur.fetchone()
            if result:
                cur.close()
                return result[0]
        
        # Buscar por departamento, provincia y distrito
        if departamento and provincia and distrito:
            cur.execute('''
                SELECT id FROM zonas_envio 
                WHERE departamento LIKE %s 
                AND provincia LIKE %s 
                AND distrito LIKE %s 
                AND activo = TRUE
            ''', (f'%{departamento}%', f'%{provincia}%', f'%{distrito}%'))
            result = cur.fetchone()
            if result:
                cur.close()
                return result[0]
        
        # Buscar solo por departamento
        if departamento:
            cur.execute('''
                SELECT id FROM zonas_envio 
                WHERE departamento LIKE %s AND activo = TRUE
                ORDER BY costo_base ASC LIMIT 1
            ''', (f'%{departamento}%',))
            result = cur.fetchone()
            if result:
                cur.close()
                return result[0]
        
        cur.close()
        return None
        
    except Exception as e:
        print('Error al buscar zona de envío:', e)
        return None

def obtener_opciones_envio(zona_id, peso_total):
    """Obtener opciones de envío para una zona y peso específicos"""
    try:
        cur = mysql.connection.cursor()
        
        # Obtener métodos de envío activos
        cur.execute('''
            SELECT m.id, m.nombre, m.descripcion, m.costo_base, m.costo_por_kg,
                   m.tiempo_entrega_min, m.tiempo_entrega_max, m.prioridad
            FROM metodos_envio m 
            WHERE m.activo = TRUE 
            ORDER BY m.prioridad ASC
        ''')
        metodos = cur.fetchall()
        
        opciones = []
        for metodo in metodos:
            metodo_id = metodo[0]
            
            # Buscar tarifa específica para esta zona y peso
            cur.execute('''
                SELECT costo, tiempo_entrega_min, tiempo_entrega_max
                FROM tarifas_envio 
                WHERE zona_id = %s AND metodo_id = %s 
                AND peso_min <= %s AND peso_max >= %s
            ''', (zona_id, metodo_id, peso_total, peso_total))
            
            tarifa = cur.fetchone()
            
            if tarifa:
                costo = float(tarifa[0])
                tiempo_min = tarifa[1]
                tiempo_max = tarifa[2]
            else:
                # Calcular costo basado en peso
                costo_base = float(metodo[3])
                costo_por_kg = float(metodo[4])
                costo = costo_base + (peso_total / 1000 * costo_por_kg)
                tiempo_min = metodo[5]
                tiempo_max = metodo[6]
            
            opciones.append({
                'id': metodo_id,
                'nombre': metodo[1],
                'descripcion': metodo[2],
                'costo': round(costo, 2),
                'tiempo_entrega': f"{tiempo_min}-{tiempo_max} días",
                'tiempo_min': tiempo_min,
                'tiempo_max': tiempo_max
            })
        
        cur.close()
        return opciones
        
    except Exception as e:
        print('Error al obtener opciones de envío:', e)
        return []

@app.route('/api/zonas-envio')
def obtener_zonas_envio():
    """Obtener lista de zonas de envío disponibles"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT DISTINCT departamento, provincia 
            FROM zonas_envio 
            WHERE activo = TRUE 
            ORDER BY departamento, provincia
        ''')
        zonas = cur.fetchall()
        cur.close()
        
        return jsonify({
            'success': True,
            'zonas': [
                {
                    'departamento': zona[0],
                    'provincia': zona[1]
                } for zona in zonas
            ]
        })
        
    except Exception as e:
        print('Error al obtener zonas de envío:', e)
        return jsonify({'success': False, 'message': 'Error al obtener zonas'})

@app.route('/api/distritos/<departamento>/<provincia>')
def obtener_distritos(departamento, provincia):
    """Obtener distritos de una provincia específica"""
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT DISTINCT distrito, codigo_postal
            FROM zonas_envio 
            WHERE departamento = %s AND provincia = %s AND activo = TRUE
            ORDER BY distrito
        ''', (departamento, provincia))
        distritos = cur.fetchall()
        cur.close()
        
        return jsonify({
            'success': True,
            'distritos': [
                {
                    'distrito': distrito[0],
                    'codigo_postal': distrito[1]
                } for distrito in distritos
            ]
        })
        
    except Exception as e:
        print('Error al obtener distritos:', e)
        return jsonify({'success': False, 'message': 'Error al obtener distritos'})

@app.route('/api/actualizar-envio-pedido', methods=['POST'])
@login_required
def actualizar_envio_pedido():
    """Actualizar información de envío en un pedido"""
    try:
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        metodo_envio = data.get('metodo_envio')
        costo_envio = data.get('costo_envio')
        tiempo_entrega = data.get('tiempo_entrega')
        
        cur = mysql.connection.cursor()
        cur.execute('''
            UPDATE pedidos 
            SET metodo_envio = %s, costo_envio = %s, tiempo_entrega = %s
            WHERE id = %s AND usuario_id = %s
        ''', (metodo_envio, costo_envio, tiempo_entrega, pedido_id, session['user_id']))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Envío actualizado'})
        
    except Exception as e:
        print('Error al actualizar envío:', e)
        return jsonify({'success': False, 'message': 'Error al actualizar envío'})

@app.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    cur = mysql.connection.cursor()
    # Obtener el producto principal y su categoria
    cur.execute("SELECT id, nombre, descripcion, precio, imagen, precio_original, descuento, categoria_id FROM productos WHERE id = %s", (producto_id,))
    prod = cur.fetchone()
    if not prod:
        cur.close()
        return "Producto no encontrado", 404
    producto = {
        'id': prod[0],
        'nombre': prod[1],
        'descripcion': prod[2],
        'precio': float(prod[3]),
        'imagen': prod[4] or 'producto_destacado.png',
        'precio_original': float(prod[5]) if prod[5] else None,
        'descuento': int(prod[6]) if prod[6] else None,
        'etiquetas': [],
        'calificacion': 5,
        'reviews': 12,
        'beneficios': [],
    }
    categoria_id = prod[7]
    # Obtener productos relacionados de la misma categoría (excluyendo el actual)
    cur.execute("SELECT id, nombre, precio, imagen, precio_original, descuento FROM productos WHERE categoria_id = %s AND id != %s LIMIT 8", (categoria_id, producto_id))
    relacionados_db = cur.fetchall()
    productos_relacionados = []
    for rel in relacionados_db:
        productos_relacionados.append({
            'id': rel[0],
            'nombre': rel[1],
            'precio': float(rel[2]),
            'imagen_url': url_for('static', filename='img/' + (rel[3] or 'producto_destacado.png')),
            'precio_original': float(rel[4]) if rel[4] else None,
            'descuento': int(rel[5]) if rel[5] else None,
        })
    cur.close()
    return render_template('producto_detalle.html', producto=producto, productos_relacionados=productos_relacionados)

@app.route('/marca/<nombre_marca>')
def marca_detalle(nombre_marca):
    descripciones = {
        'jabila': 'Jabila es sinónimo de innovación y calidad en cosmética.',
        'pandora': 'Pandora destaca por su elegancia y productos premium.',
        'flower-secret': 'Flower Secret: belleza natural y frescura en cada producto.',
        'gevl': 'Gevl, la marca de confianza para el cuidado diario.',
        'ybel': 'Ybel, expertos en color y tendencia.'
    }
    nombre_marca_db = nombre_marca.replace('-', ' ').title()
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, nombre, descripcion, precio, precio_original, descuento, imagen FROM productos WHERE LOWER(nombre) LIKE %s', (f'%{nombre_marca_db.lower()}%',))
    productos = [
        {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'precio': float(row[3]),
            'precio_original': float(row[4]) if row[4] else None,
            'descuento': int(row[5]) if row[5] else None,
            'imagen': row[6] or 'producto_destacado.png',
        } for row in cur.fetchall()
    ]
    cur.close()
    return render_template('marca_base.html', marca_nombre=nombre_marca.replace('-', ' ').title(), marca_descripcion=descripciones.get(nombre_marca.lower()), productos=productos)

@app.route('/recordar-suscripcion', methods=['POST'])
def recordar_suscripcion():
    correo = request.form.get('correo', '').strip().lower()
    if not correo:
        flash('Por favor ingresa un correo electrónico válido.', 'error')
        return redirect(url_for('home'))
    
    if verificar_suscripcion(correo):
        session['suscriptor_email'] = correo
        flash('¡Bienvenido de vuelta! Ya puedes acceder a la comunidad.', 'success')
    else:
        flash('Este correo no está suscrito. Por favor suscríbete primero.', 'error')
    
    return redirect(url_for('home'))

# --- Automatización de productos destacados ---
def actualizar_productos_destacados():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE productos SET destacado = 0")
    cur.execute("SELECT id FROM productos ORDER BY RAND() LIMIT 10")
    ids = [row['id'] for row in cur.fetchall()]
    if ids:
        cur.execute("UPDATE productos SET destacado = 1 WHERE id IN (%s)" % ','.join(str(i) for i in ids))
    cur.close()

# Programar la tarea para que se ejecute cada día
def iniciar_scheduler_destacados():
    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_productos_destacados, 'interval', days=1)
    scheduler.start()

with app.app_context():
    actualizar_productos_destacados()
    iniciar_scheduler_destacados()

# --- RUTAS DEL PANEL DE ADMINISTRACIÓN ---

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard principal del panel de administración"""
    try:
        cur = mysql.connection.cursor()
        
        # Estadísticas básicas
        cur.execute("SELECT COUNT(*) FROM productos")
        total_productos = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM categorias")
        total_categorias = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cur.fetchone()[0]
        
        # Calcular crecimientos (simulado por ahora)
        crecimiento_productos = 12.5
        crecimiento_categorias = 5.2
        crecimiento_usuarios = 8.7
        crecimiento_pedidos = 15.3
        
        # Estadísticas de ventas
        cur.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE estado = 'entregado'")
        ventas_totales = float(cur.fetchone()[0] or 0)
        
        cur.execute("SELECT COUNT(*) FROM pedidos WHERE DATE(fecha) = CURDATE()")
        pedidos_periodo = cur.fetchone()[0]
        
        promedio_pedido = ventas_totales / total_pedidos if total_pedidos > 0 else 0
        
        # Estado de pedidos
        cur.execute("SELECT estado, COUNT(*) FROM pedidos GROUP BY estado")
        estados_pedidos = dict(cur.fetchall())
        
        pedidos_pendientes = estados_pedidos.get('pendiente', 0)
        pedidos_confirmados = estados_pedidos.get('confirmado', 0)
        pedidos_preparacion = estados_pedidos.get('en preparación', 0)
        pedidos_enviados = estados_pedidos.get('enviado', 0)
        pedidos_entregados = estados_pedidos.get('entregado', 0)
        
        # Productos más vendidos
        cur.execute("""
            SELECT p.nombre, p.precio, p.imagen, c.nombre as categoria, 
                   COALESCE(SUM(di.cantidad), 0) as ventas
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN detalle_pedido di ON p.id = di.producto_id
            LEFT JOIN pedidos ped ON di.pedido_id = ped.id
            WHERE ped.estado = 'entregado' OR ped.estado IS NULL
            GROUP BY p.id, p.nombre, p.precio, p.imagen, c.nombre
            ORDER BY ventas DESC
            LIMIT 5
        """)
        productos_mas_vendidos = [
            {
                'nombre': row[0],
                'precio': float(row[1]),
                'imagen': row[2],
                'categoria': row[3] or 'Sin categoría',
                'ventas': int(row[4])
            } for row in cur.fetchall()
        ]
        
        # Categorías más populares
        cur.execute("""
            SELECT c.nombre, COUNT(p.id) as productos,
                   COALESCE(SUM(di.cantidad), 0) as ventas
            FROM categorias c
            LEFT JOIN productos p ON c.id = p.categoria_id
            LEFT JOIN detalle_pedido di ON p.id = di.producto_id
            LEFT JOIN pedidos ped ON di.pedido_id = ped.id
            WHERE ped.estado = 'entregado' OR ped.estado IS NULL
            GROUP BY c.id, c.nombre
            ORDER BY ventas DESC
            LIMIT 5
        """)
        categorias_populares = []
        total_ventas_categorias = sum(row[2] for row in cur.fetchall())
        cur.execute("""
            SELECT c.nombre, COUNT(p.id) as productos,
                   COALESCE(SUM(di.cantidad), 0) as ventas
            FROM categorias c
            LEFT JOIN productos p ON c.id = p.categoria_id
            LEFT JOIN detalle_pedido di ON p.id = di.producto_id
            LEFT JOIN pedidos ped ON di.pedido_id = ped.id
            WHERE ped.estado = 'entregado' OR ped.estado IS NULL
            GROUP BY c.id, c.nombre
            ORDER BY ventas DESC
            LIMIT 5
        """)
        for i, row in enumerate(cur.fetchall()):
            porcentaje = (row[2] / total_ventas_categorias * 100) if total_ventas_categorias > 0 else 0
            colores = ['blue', 'green', 'purple', 'orange', 'red']
            categorias_populares.append({
                'nombre': row[0],
                'productos': row[1],
                'ventas': int(row[2]),
                'porcentaje': porcentaje,
                'color': colores[i] if i < len(colores) else 'gray'
            })
        
        # Actividad reciente
        actividades_recientes = []
        
        # Últimos productos agregados
        cur.execute("""
            SELECT nombre, id 
            FROM productos 
            ORDER BY id DESC 
            LIMIT 3
        """)
        for row in cur.fetchall():
            actividades_recientes.append({
                'titulo': 'Nuevo producto agregado',
                'descripcion': row[0],
                'tiempo': 'Recientemente',
                'color': 'green',
                'icono': 'plus'
            })
        
        # Últimos usuarios registrados
        cur.execute("""
            SELECT nombre, fecha_registro 
            FROM usuarios 
            ORDER BY fecha_registro DESC 
            LIMIT 2
        """)
        for row in cur.fetchall():
            tiempo = calcular_tiempo_relativo(row[1]) if row[1] else 'Recientemente'
            actividades_recientes.append({
                'titulo': 'Nuevo usuario registrado',
                'descripcion': row[0],
                'tiempo': tiempo,
                'color': 'blue',
                'icono': 'user-plus'
            })
        
        # Últimos pedidos
        cur.execute("""
            SELECT id, total, fecha 
            FROM pedidos 
            ORDER BY fecha DESC 
            LIMIT 2
        """)
        for row in cur.fetchall():
            tiempo = calcular_tiempo_relativo(row[2]) if row[2] else 'Recientemente'
            actividades_recientes.append({
                'titulo': 'Nuevo pedido recibido',
                'descripcion': f'Pedido #{row[0]} - S/ {row[1]:.2f}',
                'tiempo': tiempo,
                'color': 'orange',
                'icono': 'shopping-cart'
            })
        
        # Ordenar actividades por tiempo
        actividades_recientes.sort(key=lambda x: x['tiempo'])
        
        cur.close()
        
        return render_template('admin/dashboard.html', 
                             total_productos=total_productos,
                             total_categorias=total_categorias,
                             total_usuarios=total_usuarios,
                             total_pedidos=total_pedidos,
                             crecimiento_productos=crecimiento_productos,
                             crecimiento_categorias=crecimiento_categorias,
                             crecimiento_usuarios=crecimiento_usuarios,
                             crecimiento_pedidos=crecimiento_pedidos,
                             ventas_totales=ventas_totales,
                             pedidos_periodo=pedidos_periodo,
                             promedio_pedido=promedio_pedido,
                             pedidos_pendientes=pedidos_pendientes,
                             pedidos_confirmados=pedidos_confirmados,
                             pedidos_preparacion=pedidos_preparacion,
                             pedidos_enviados=pedidos_enviados,
                             pedidos_entregados=pedidos_entregados,
                             productos_mas_vendidos=productos_mas_vendidos,
                             categorias_populares=categorias_populares,
                             actividades_recientes=actividades_recientes)
    except Exception as e:
        flash('Error al cargar el dashboard', 'error')
        print(f"Error en admin_dashboard: {e}")
        return redirect(url_for('home'))

def calcular_tiempo_relativo(fecha):
    """Calcula el tiempo relativo desde una fecha"""
    if not fecha:
        return 'Recientemente'
    
    from datetime import datetime
    ahora = datetime.now()
    diferencia = ahora - fecha
    
    if diferencia.days > 0:
        return f'{diferencia.days} día{"s" if diferencia.days != 1 else ""}'
    elif diferencia.seconds > 3600:
        horas = diferencia.seconds // 3600
        return f'{horas} hora{"s" if horas != 1 else ""}'
    elif diferencia.seconds > 60:
        minutos = diferencia.seconds // 60
        return f'{minutos} min'
    else:
        return 'Ahora'

@app.route('/admin/productos')
@admin_required
def admin_productos():
    """Gestión de productos con paginación"""
    try:
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page
        cur = mysql.connection.cursor()
        # Contar total de productos
        cur.execute("SELECT COUNT(*) FROM productos")
        total_productos = cur.fetchone()[0]
        # Traer productos paginados
        cur.execute("""
            SELECT p.id, p.nombre, p.precio, p.precio_original, p.descuento, p.stock, p.imagen, c.nombre as categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.id DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        productos = [
            {
                'id': row['id'],
                'nombre': row['nombre'],
                'precio': float(row['precio']),
                'precio_original': float(row['precio_original']) if row['precio_original'] else None,
                'descuento': int(row['descuento']) if row['descuento'] else None,
                'stock': row['stock'],
                'imagen': row['imagen'],
                'categoria': row['categoria'] or 'Sin categoría'
            } for row in cur.fetchall()
        ]
        cur.close()
        total_pages = (total_productos + per_page - 1) // per_page
        return render_template('admin/productos.html', productos=productos, page=page, total_pages=total_pages, total_productos=total_productos)
    except Exception as e:
        flash('Error al cargar productos', 'error')
        print(f"Error en admin_productos: {e}")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/producto/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_producto_nuevo():
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio'])
            precio_original = float(request.form['precio_original']) if request.form['precio_original'] else None
            descuento = int(request.form['descuento']) if request.form['descuento'] else None
            stock = int(request.form['stock'])
            categoria_id = int(request.form['categoria_id'])
            
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO productos (nombre, descripcion, precio, precio_original, descuento, stock, categoria_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, descripcion, precio, precio_original, descuento, stock, categoria_id))
            mysql.connection.commit()
            cur.close()
            
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('admin_productos'))
        except Exception as e:
            flash('Error al crear producto', 'error')
            print(f"Error en admin_producto_nuevo: {e}")
    
    # GET: mostrar formulario
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        categorias = [{'id': row['id'], 'nombre': row['nombre']} for row in cur.fetchall()]
        cur.close()
        return render_template('admin/producto_form.html', producto=None, categorias=categorias)
    except Exception as e:
        flash('Error al cargar categorías', 'error')
        return redirect(url_for('admin_productos'))

@app.route('/admin/producto/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_producto_editar(id):
    """Editar producto existente"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio = float(request.form['precio'])
            precio_original = float(request.form['precio_original']) if request.form['precio_original'] else None
            descuento = int(request.form['descuento']) if request.form['descuento'] else None
            stock = int(request.form['stock'])
            categoria_id = int(request.form['categoria_id'])
            
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE productos 
                SET nombre = %s, descripcion = %s, precio = %s, precio_original = %s, 
                    descuento = %s, stock = %s, categoria_id = %s
                WHERE id = %s
            """, (nombre, descripcion, precio, precio_original, descuento, stock, categoria_id, id))
            mysql.connection.commit()
            cur.close()
            
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('admin_productos'))
        except Exception as e:
            flash('Error al actualizar producto', 'error')
            print(f"Error en admin_producto_editar: {e}")
    
    # GET: mostrar formulario con datos del producto
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre, descripcion, precio, precio_original, descuento, stock, categoria_id FROM productos WHERE id = %s", (id,))
        producto_data = cur.fetchone()
        if not producto_data:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('admin_productos'))
        
        producto = {
            'id': producto_data['id'],
            'nombre': producto_data['nombre'],
            'descripcion': producto_data['descripcion'],
            'precio': float(producto_data['precio']),
            'precio_original': float(producto_data['precio_original']) if producto_data['precio_original'] else None,
            'descuento': int(producto_data['descuento']) if producto_data['descuento'] else None,
            'stock': producto_data['stock'],
            'categoria_id': producto_data['categoria_id']
        }
        
        cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        categorias = [{'id': row['id'], 'nombre': row['nombre']} for row in cur.fetchall()]
        cur.close()
        
        return render_template('admin/producto_form.html', producto=producto, categorias=categorias)
    except Exception as e:
        flash('Error al cargar producto', 'error')
        return redirect(url_for('admin_productos'))

@app.route('/admin/producto/eliminar/<int:id>', methods=['POST'])
@admin_required
def admin_producto_eliminar(id):
    """Eliminar producto"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM productos WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        flash('Error al eliminar producto', 'error')
        print(f"Error en admin_producto_eliminar: {e}")
    
    return redirect(url_for('admin_productos'))

@app.route('/admin/categorias')
@admin_required
def admin_categorias():
    """Gestión de categorías"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
        categorias = [
            {
                'id': row['id'],
                'nombre': row['nombre'],
                'descripcion': row['descripcion']
            } for row in cur.fetchall()
        ]
        cur.close()
        return render_template('admin/categorias.html', categorias=categorias)
    except Exception as e:
        flash('Error al cargar categorías', 'error')
        print(f"Error en admin_categorias: {e}")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/categoria/nueva', methods=['GET', 'POST'])
@admin_required
def admin_categoria_nueva():
    """Crear nueva categoría"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
            mysql.connection.commit()
            cur.close()
            
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('admin_categorias'))
        except Exception as e:
            flash('Error al crear categoría', 'error')
            print(f"Error en admin_categoria_nueva: {e}")
    
    return render_template('admin/categoria_form.html', categoria=None)

@app.route('/admin/categoria/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_categoria_editar(id):
    """Editar categoría existente"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            
            cur = mysql.connection.cursor()
            cur.execute("UPDATE categorias SET nombre = %s, descripcion = %s WHERE id = %s", (nombre, descripcion, id))
            mysql.connection.commit()
            cur.close()
            
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('admin_categorias'))
        except Exception as e:
            flash('Error al actualizar categoría', 'error')
            print(f"Error en admin_categoria_editar: {e}")
    
    # GET: mostrar formulario con datos de la categoría
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM categorias WHERE id = %s", (id,))
        categoria_data = cur.fetchone()
        if not categoria_data:
            flash('Categoría no encontrada', 'error')
            return redirect(url_for('admin_categorias'))
        
        categoria = {
            'id': categoria_data['id'],
            'nombre': categoria_data['nombre'],
            'descripcion': categoria_data['descripcion']
        }
        cur.close()
        
        return render_template('admin/categoria_form.html', categoria=categoria)
    except Exception as e:
        flash('Error al cargar categoría', 'error')
        return redirect(url_for('admin_categorias'))

@app.route('/admin/categoria/eliminar/<int:id>', methods=['POST'])
@admin_required
def admin_categoria_eliminar(id):
    """Eliminar categoría"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM categorias WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Categoría eliminada exitosamente', 'success')
    except Exception as e:
        flash('Error al eliminar categoría', 'error')
        print(f"Error en admin_categoria_eliminar: {e}")
    
    return redirect(url_for('admin_categorias'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Gestión de usuarios"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nombre, email, tipo_usuario, email_verificado, ultimo_login, fecha_registro
            FROM usuarios 
            ORDER BY id DESC
        """)
        usuarios = [
            {
                'id': row['id'],
                'nombre': row['nombre'],
                'email': row['email'],
                'tipo_usuario': row['tipo_usuario'],
                'email_verificado': bool(row['email_verificado']),
                'ultimo_login': row['ultimo_login'],
                'fecha_registro': row['fecha_registro']
            } for row in cur.fetchall()
        ]
        cur.close()
        return render_template('admin/usuarios.html', usuarios=usuarios)
    except Exception as e:
        flash('Error al cargar usuarios', 'error')
        print(f"Error en admin_usuarios: {e}")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/usuario/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_usuario_editar(id):
    """Editar usuario existente"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            tipo_usuario = request.form['tipo_usuario']
            email_verificado = 'email_verificado' in request.form
            
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE usuarios 
                SET nombre = %s, email = %s, tipo_usuario = %s, email_verificado = %s
                WHERE id = %s
            """, (nombre, email, tipo_usuario, email_verificado, id))
            mysql.connection.commit()
            cur.close()
            
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('admin_usuarios'))
        except Exception as e:
            flash('Error al actualizar usuario', 'error')
            print(f"Error en admin_usuario_editar: {e}")
    
    # GET: mostrar formulario con datos del usuario
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nombre, email, tipo_usuario, email_verificado, fecha_registro
            FROM usuarios WHERE id = %s
        """, (id,))
        usuario_data = cur.fetchone()
        if not usuario_data:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin_usuarios'))
        
        usuario = {
            'id': usuario_data['id'],
            'nombre': usuario_data['nombre'],
            'email': usuario_data['email'],
            'tipo_usuario': usuario_data['tipo_usuario'],
            'email_verificado': bool(usuario_data['email_verificado']),
            'fecha_registro': usuario_data['fecha_registro']
        }
        cur.close()
        
        return render_template('admin/usuario_form.html', usuario=usuario)
    except Exception as e:
        flash('Error al cargar usuario', 'error')
        return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuario/eliminar/<int:id>', methods=['POST'])
@admin_required
def admin_usuario_eliminar(id):
    """Eliminar usuario"""
    try:
        # Verificar que no se elimine a sí mismo
        if id == session.get('user_id'):
            flash('No puedes eliminar tu propia cuenta', 'error')
            return redirect(url_for('admin_usuarios'))
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        flash('Error al eliminar usuario', 'error')
        print(f"Error en admin_usuario_eliminar: {e}")
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT p.id, u.nombre as usuario_nombre, p.fecha, p.total, p.estado
            FROM pedidos p
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            ORDER BY p.fecha DESC
        ''')
        pedidos = []
        for row in cur.fetchall():
            # Contar reclamos asociados
            cur2 = mysql.connection.cursor()
            cur2.execute("SELECT COUNT(*) FROM reclamos WHERE pedido_id = %s", (row['id'],))
            reclamos_count = cur2.fetchone()[0]
            cur2.close()
            pedidos.append({
                'id': row['id'],
                'usuario_nombre': row['usuario_nombre'] or 'Usuario no registrado',
                'fecha': row['fecha'].strftime('%d/%m/%Y') if row['fecha'] else 'N/A',
                'total': float(row['total']),
                'estado': row['estado'],
                'reclamos': reclamos_count
            })
        cur.close()
        return render_template('admin/pedidos.html', pedidos=pedidos)
    except Exception as e:
        flash('Error al cargar pedidos', 'error')
        print(f"Error en admin_pedidos: {e}")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/pedido/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_pedido_detalle(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            SELECT p.id, u.nombre as usuario_nombre, p.fecha, p.total, p.estado
            FROM pedidos p
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.id = %s
        ''', (id,))
        pedido_data = cur.fetchone()
        if not pedido_data:
            flash('Pedido no encontrado', 'error')
            return redirect(url_for('admin_pedidos'))
        pedido = {
            'id': pedido_data['id'],
            'usuario_nombre': pedido_data['usuario_nombre'] or 'Usuario no registrado',
            'fecha': pedido_data['fecha'].strftime('%d/%m/%Y') if pedido_data['fecha'] else 'N/A',
            'total': float(pedido_data['total']),
            'estado': pedido_data['estado']
        }
        # Obtener items del pedido
        cur.execute('''
            SELECT p.nombre, dp.cantidad, dp.precio_unitario
            FROM detalle_pedido dp
            JOIN productos p ON dp.producto_id = p.id
            WHERE dp.pedido_id = %s
        ''', (id,))
        items = [
            {
                'nombre': row['nombre'],
                'cantidad': row['cantidad'],
                'precio_unitario': float(row['precio_unitario'])
            } for row in cur.fetchall()
        ]
        pedido['items'] = items
        # Reclamos asociados
        cur.execute("SELECT motivo, descripcion, fecha FROM reclamos WHERE pedido_id = %s", (id,))
        reclamos = [
            {'motivo': r['motivo'], 'descripcion': r['descripcion'], 'fecha': r['fecha'].strftime('%d/%m/%Y %H:%M')} for r in cur.fetchall()
        ]
        cur.close()
        # Cambiar estado del pedido
        if request.method == 'POST':
            nuevo_estado = request.form.get('nuevo_estado')
            if nuevo_estado and nuevo_estado in ['Pendiente', 'Enviado', 'Entregado', 'Cancelado']:
                cur2 = mysql.connection.cursor()
                cur2.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, id))
                mysql.connection.commit()
                cur2.close()
                flash('Estado actualizado.', 'success')
                return redirect(url_for('admin_pedido_detalle', id=id))
        return render_template('admin/pedido_detalle.html', pedido=pedido, reclamos=reclamos)
    except Exception as e:
        flash('Error al cargar pedido', 'error')
        print(f"Error en admin_pedido_detalle: {e}")
        return redirect(url_for('admin_pedidos'))

@app.route('/marcas')
def marcas():
    return render_template('marcas.html')

@app.route('/descargar_pedido_pdf/<int:pedido_id>')
@login_required
def descargar_pedido_pdf(pedido_id):
    usuario_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, fecha, total, estado FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    pedido = cur.fetchone()
    if not pedido:
        return "Pedido no encontrado", 404
    cur.execute("""
        SELECT p.nombre, dp.cantidad, dp.precio_unitario
        FROM detalle_pedido dp
        JOIN productos p ON dp.producto_id = p.id
        WHERE dp.pedido_id = %s
    """, (pedido_id,))
    productos = cur.fetchall()
    cur.close()

    # Crear PDF en memoria
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, f"Comprobante de Pedido #{pedido['id']}")
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, f"Fecha: {pedido['fecha'].strftime('%Y-%m-%d')}")
    p.drawString(50, 710, f"Estado: {pedido['estado']}")
    p.drawString(50, 690, f"Total: S/ {pedido['total']:.2f}")
    p.drawString(50, 670, "Productos:")

    y = 650
    for prod in productos:
        p.drawString(60, y, f"{prod['nombre']} x{prod['cantidad']} - S/ {prod['precio_unitario']:.2f} c/u")
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'pedido_{pedido_id}.pdf', mimetype='application/pdf')

@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def cancelar_pedido(pedido_id):
    usuario_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT estado FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    pedido = cur.fetchone()
    if not pedido or pedido['estado'] in ['Entregado', 'Cancelado']:
        cur.close()
        flash('No se puede cancelar este pedido.', 'error')
        return redirect(url_for('mis_pedidos'))
    cur.execute("UPDATE pedidos SET estado = 'Cancelado' WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    mysql.connection.commit()
    cur.close()
    flash('Pedido cancelado correctamente.', 'success')
    return redirect(url_for('mis_pedidos'))

@app.route('/reclamo_pedido/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def reclamo_pedido(pedido_id):
    usuario_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    pedido = cur.fetchone()
    if not pedido:
        cur.close()
        flash('Pedido no encontrado.', 'error')
        return redirect(url_for('mis_pedidos'))
    if request.method == 'POST':
        motivo = request.form.get('motivo')
        descripcion = request.form.get('descripcion')
        cur.execute("INSERT INTO reclamos (pedido_id, usuario_id, motivo, descripcion, fecha) VALUES (%s, %s, %s, %s, NOW())", (pedido_id, usuario_id, motivo, descripcion))
        mysql.connection.commit()
        cur.close()
        flash('Reclamo enviado correctamente.', 'success')
        return redirect(url_for('mis_pedidos'))
    cur.close()
    return render_template('reclamo_pedido.html', pedido_id=pedido_id)

@app.route('/recibo/<int:pedido_id>')
@login_required
def recibo_virtual(pedido_id):
    usuario_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, fecha, total, estado, metodo_pago FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, usuario_id))
    pedido = cur.fetchone()
    if not pedido:
        cur.close()
        flash('Pedido no encontrado.', 'error')
        return redirect(url_for('mis_pedidos'))
    cur.execute("""
        SELECT p.nombre, dp.cantidad, dp.precio_unitario, p.imagen
        FROM detalle_pedido dp
        JOIN productos p ON dp.producto_id = p.id
        WHERE dp.pedido_id = %s
    """, (pedido_id,))
    productos = cur.fetchall()
    cur.close()
    return render_template('recibo.html', pedido={
        'id': pedido['id'],
        'fecha': pedido['fecha'].strftime('%Y-%m-%d %H:%M'),
        'total': float(pedido['total']),
        'estado': pedido['estado'],
        'metodo_pago': pedido['metodo_pago'] or 'No especificado',
        'productos': [
            {
                'nombre': prod['nombre'],
                'cantidad': prod['cantidad'],
                'precio_unitario': float(prod['precio_unitario']),
                'subtotal': float(prod['precio_unitario']) * prod['cantidad'],
                'imagen': prod['imagen'] or 'producto_destacado.png'
            } for prod in productos
        ]
    })

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000) 