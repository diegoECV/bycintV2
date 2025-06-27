from dotenv import load_dotenv
load_dotenv()
import os
print('GOOGLE_CLIENT_ID:', os.getenv('GOOGLE_CLIENT_ID'))
print('GOOGLE_CLIENT_SECRET:', os.getenv('GOOGLE_CLIENT_SECRET'))
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from functools import wraps
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_mail import Mail, Message
from flask import render_template_string

app = Flask(__name__)

# Secret key for sessions and flash messages (IMPORTANT)
app.secret_key = os.urandom(24)

# Configuración de conexión MySQL a Amazon RDS
app.config['MYSQL_HOST'] = 'pagianweb2.cbddj5emoatz.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'diego123456'  # Contraseña de RDS
app.config['MYSQL_DB'] = 'bycint2'
app.config['MYSQL_PORT'] = 3306  # Puerto por defecto de MySQL en RDS

mysql = MySQL(app)

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

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validar contraseña (mínimo 8 caracteres, al menos una letra y un número)"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Za-z]', password):
        return False, "La contraseña debe contener al menos una letra"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    return True, "Contraseña válida"

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, precio, imagen, precio_original, descuento FROM productos WHERE destacado = 1 LIMIT 10")
    productos_db = cur.fetchall()
    cur.close()
    productos_destacados = []
    for prod in productos_db:
        productos_destacados.append({
            'id': prod[0],
            'nombre': prod[1],
            'precio': float(prod[2]),
            'imagen_url': url_for('static', filename='img/' + (prod[3] or 'producto_destacado.png')),
            'precio_original': float(prod[4]) if prod[4] else None,
            'descuento': int(prod[5]) if prod[5] else None,
            'nuevo': bool(prod[5]),
        })
    return render_template('index.html', productos_destacados=productos_destacados)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = 'remember_me' in request.form
        
        if not email or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html')
        
        if not validate_email(email):
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('login.html')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, nombre, email, contrasena, tipo_usuario FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            
            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[2]
                session['user_type'] = user[4]
                
                # Actualizar último login
                cur = mysql.connection.cursor()
                cur.execute("UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s", (user[0],))
                mysql.connection.commit()
                cur.close()
                
                flash('¡Bienvenido de vuelta!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Email o contraseña incorrectos.', 'error')
                
        except Exception as e:
            flash('Error al iniciar sesión. Por favor intenta de nuevo.', 'error')
            print(f"Error en login: {e}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        telefono = request.form.get('telefono', '')
        
        # Validaciones
        if not all([nombre, email, password, confirm_password]):
            flash('Por favor completa todos los campos obligatorios.', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Por favor ingresa un email válido.', 'error')
            return render_template('register.html')
        
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')
        
        try:
            cur = mysql.connection.cursor()
            
            # Verificar si el email ya existe
            cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Este email ya está registrado.', 'error')
                cur.close()
                return render_template('register.html')
            
            # Crear nuevo usuario
            hashed_password = generate_password_hash(password)
            cur.execute("""
                INSERT INTO usuarios (nombre, email, contrasena, telefono, email_verificado) 
                VALUES (%s, %s, %s, %s, %s)
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
    
    return render_template('register.html')

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
    categorias = [{'id': row[0], 'nombre': row[1]} for row in cur.fetchall()]
    cur.execute('SELECT MIN(precio), MAX(precio) FROM productos')
    min_precio, max_precio = cur.fetchone()
    filtro_precio = {'min': int(min_precio or 0), 'max': int(max_precio or 0)}
    cur.close()
    return render_template('tienda.html', categorias=categorias, filtro_precio=filtro_precio)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/comunidad')
def comunidad():
    if not session.get('suscriptor_email'):
        flash('Debes suscribirte para acceder a la comunidad.', 'error')
        return redirect(url_for('home'))
    # Ejemplo de blogs/noticias
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
        }
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
    if not session.get('suscriptor_email'):
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
        'perfume': 'Perfume',
        'perfumes': 'Perfume',
        'joyeria': 'Joyería',
        'pintalabios': 'Pintalabios',
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
        'perfume': [
            {'nombre': 'Género', 'opciones': ['Mujer', 'Hombre', 'Unisex']},
            {'nombre': 'Concentración', 'opciones': ['Eau de Parfum', 'Eau de Toilette']},
        ],
        'joyeria': [
            {'nombre': 'Tipo', 'opciones': ['Collares', 'Pulseras', 'Anillos', 'Aretes']},
            {'nombre': 'Material', 'opciones': ['Plata', 'Oro', 'Acero', 'Fantasía']},
        ],
        'pintalabios': [
            {'nombre': 'Tipo', 'opciones': ['Líquidos', 'Barra', 'Gloss']},
            {'nombre': 'Acabado', 'opciones': ['Mate', 'Brillante']},
        ],
    }
    filtro_precio = {'min': 20, 'max': 200}

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre FROM categorias WHERE LOWER(nombre) = %s", (nombre_categoria_db.lower(),))
    categoria = cur.fetchone()
    if not categoria:
        cur.close()
        flash('Categoría no encontrada.', 'error')
        return redirect(url_for('home'))
    categoria_id = categoria[0]
    nombre_categoria_db = categoria[1]

    # Leer filtros de la URL
    tipo = request.args.get('tipo')
    genero = request.args.get('genero')
    material = request.args.get('material')

    # Consulta precisa por campos específicos
    query = "SELECT nombre, precio, imagen, id FROM productos WHERE categoria_id = %s"
    params = [categoria_id]
    if tipo:
        query += " AND tipo = %s"
        params.append(tipo)
    if genero:
        query += " AND genero = %s"
        params.append(genero)
    if material:
        query += " AND material = %s"
        params.append(material)

    cur.execute(query, tuple(params))
    productos_db = cur.fetchall()
    cur.close()
    productos = []
    for prod in productos_db:
        productos.append({
            'nombre': prod[0],
            'precio': prod[1],
            'precio_original': None,
            'descuento': None,
            'imagen': prod[2] or 'producto_destacado.png',
            'id': prod[3],
        })

    filtros = filtros_por_categoria.get(nombre_categoria.lower(), [])

    return render_template('categoria.html', categoria=nombre_categoria_db, productos=productos, filtros=filtros, filtro_precio=filtro_precio)

@app.route('/api/productos')
def api_productos():
    categorias = request.args.getlist('categoria')
    oferta = request.args.get('oferta')
    novedad = request.args.get('novedad')
    precio_max = request.args.get('precio', type=float)
    orden = request.args.get('orden', 'relevancia')

    query = "SELECT p.nombre, p.precio, p.imagen, p.id, p.precio_original, p.descuento, p.fecha_release FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE 1=1"
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
    productos = []
    for prod in productos_db:
        productos.append({
            'nombre': prod[0],
            'precio': float(prod[1]),
            'imagen': prod[2] or 'producto_destacado.png',
            'id': prod[3],
            'precio_original': float(prod[4]) if prod[4] else None,
            'descuento': int(prod[5]) if prod[5] else None,
            'fecha_release': prod[6].isoformat() if prod[6] else None,
        })
    return jsonify({'productos': productos})

@app.route('/api/productos_categoria')
def api_productos_categoria():
    categoria = request.args.get('categoria')
    tipo = request.args.get('tipo')
    acabado = request.args.get('acabado')
    material = request.args.get('material')
    genero = request.args.get('genero')
    precio_max = request.args.get('precio', type=float)

    query = "SELECT p.nombre, p.precio, p.imagen, p.id, p.precio_original, p.descuento FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE 1=1"
    params = []
    if categoria:
        query += " AND c.nombre = %s"
        params.append(categoria)
    if tipo:
        query += " AND p.tipo = %s"
        params.append(tipo)
    if acabado:
        query += " AND p.acabado = %s"
        params.append(acabado)
    if material:
        query += " AND p.material = %s"
        params.append(material)
    if genero:
        query += " AND p.genero = %s"
        params.append(genero)
    if precio_max:
        query += " AND p.precio <= %s"
        params.append(precio_max)

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    productos_db = cur.fetchall()
    cur.close()
    productos = []
    for prod in productos_db:
        productos.append({
            'nombre': prod[0],
            'precio': float(prod[1]),
            'imagen': prod[2] or 'producto_destacado.png',
            'id': prod[3],
            'precio_original': float(prod[4]) if prod[4] else None,
            'descuento': int(prod[5]) if prod[5] else None,
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
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para usar un cupón.'}), 401
    data = request.get_json()
    cupon = data.get('cupon', '').strip().upper()
    user_id = session['user_id']
    CUPON_VALIDO = 'LOOK2X1'
    DESCUENTO = 0.10  # 10%

    # Verificar si el cupón es válido
    if cupon != CUPON_VALIDO:
        return jsonify({'success': False, 'message': 'Cupón inválido.'}), 400

    # Verificar si el usuario ya usó el cupón
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM cupones_usados WHERE usuario_id = %s AND cupon = %s", (user_id, CUPON_VALIDO))
    if cur.fetchone():
        cur.close()
        return jsonify({'success': False, 'message': 'Ya usaste este cupón.'}), 400

    # Obtener el total actual del carrito
    cur.execute("SELECT SUM(p.precio * c.cantidad) FROM carrito c JOIN productos p ON c.producto_id = p.id WHERE c.usuario_id = %s", (user_id,))
    total = cur.fetchone()[0] or 0
    total = float(total)
    if total == 0:
        cur.close()
        return jsonify({'success': False, 'message': 'Tu carrito está vacío.'}), 400

    descuento = round(total * DESCUENTO, 2)
    total_con_descuento = round(total - descuento, 2)

    # Guardar que el usuario ya usó el cupón
    cur.execute("INSERT INTO cupones_usados (usuario_id, cupon) VALUES (%s, %s)", (user_id, CUPON_VALIDO))
    mysql.connection.commit()
    cur.close()

    return jsonify({
        'success': True,
        'descuento': descuento,
        'total': total_con_descuento,
        'message': f'Se aplicó un 10% de descuento. Ahorraste S/ {descuento:.2f}'
    })

@app.route('/api/calcular_envio', methods=['POST'])
def calcular_envio():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para calcular el envío.'}), 401
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT SUM(p.precio * c.cantidad) FROM carrito c JOIN productos p ON c.producto_id = p.id WHERE c.usuario_id = %s", (user_id,))
    total = cur.fetchone()[0] or 0
    opciones = []
    if total >= 100:
        opciones.append({
            'nombre': 'Gratis',
            'precio': 0.00,
            'descripcion': '3-5 días (Envío estándar)',
            'codigo': 'gratis'
        })
        opciones.append({
            'nombre': 'Express',
            'precio': 20.00,
            'descripcion': '1-2 días',
            'codigo': 'express'
        })
    else:
        opciones.append({
            'nombre': 'Estándar',
            'precio': 10.00,
            'descripcion': '3-5 días',
            'codigo': 'estandar'
        })
        opciones.append({
            'nombre': 'Express',
            'precio': 20.00,
            'descripcion': '1-2 días',
            'codigo': 'express'
        })
    cur.close()
    return jsonify({'success': True, 'opciones': opciones, 'total_carrito': total})

@app.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre, descripcion, precio, imagen, precio_original, descuento FROM productos WHERE id = %s", (producto_id,))
    prod = cur.fetchone()
    cur.close()
    if not prod:
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
    return render_template('producto_detalle.html', producto=producto)

@app.context_processor
def inject_current_year():
    from datetime import datetime
    return {'current_year': datetime.now().year}

@app.context_processor
def inject_products():
    return {'products': []}

@app.route('/profile', methods=['POST'])
@login_required
def profile_update():
    data = request.form
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    documento = data.get('documento')
    genero = data.get('genero')
    fecha_nacimiento = data.get('fecha_nacimiento')
    telefono = data.get('telefono')
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuarios SET nombre=%s, apellido=%s, documento=%s, genero=%s, fecha_nacimiento=%s, telefono=%s WHERE id=%s
        """, (nombre, apellido, documento, genero, fecha_nacimiento, telefono, session['user_id']))
        mysql.connection.commit()
        cur.close()
        session['user_name'] = nombre
        return jsonify({'success': True, 'message': 'Perfil actualizado correctamente.'})
    except Exception as e:
        print('Error al actualizar perfil:', e)
        return jsonify({'success': False, 'message': 'Error al actualizar perfil.'}), 500

@app.route('/profile/avatar', methods=['POST'])
@login_required
def profile_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió archivo.'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Archivo vacío.'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif']:
        return jsonify({'success': False, 'message': 'Formato no permitido.'}), 400
    filename = f"avatar_{session['user_id']}.{ext}"
    path = os.path.join('static', 'img', filename)
    file.save(path)
    # Actualizar en BD
    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuarios SET avatar_url=%s WHERE id=%s", (filename, session['user_id']))
    mysql.connection.commit()
    cur.close()
    session['user_avatar'] = url_for('static', filename='img/' + filename)
    return jsonify({'success': True, 'message': 'Avatar actualizado.', 'avatar_url': session['user_avatar']})

@app.route('/profile/boletin', methods=['POST'])
@login_required
def profile_boletin():
    boletin = bool(request.form.get('boletin'))
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE usuarios SET boletin=%s WHERE id=%s", (boletin, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Preferencia de boletín actualizada.'})
    except Exception as e:
        print('Error boletín:', e)
        return jsonify({'success': False, 'message': 'Error al actualizar preferencia.'}), 500

@app.route('/profile/cambiar_contrasena', methods=['POST'])
@login_required
def cambiar_contrasena():
    data = request.form
    actual = data.get('actual')
    nueva = data.get('nueva')
    confirmar = data.get('confirmar')
    if not all([actual, nueva, confirmar]):
        return jsonify({'success': False, 'message': 'Completa todos los campos.'})
    if nueva != confirmar:
        return jsonify({'success': False, 'message': 'Las contraseñas nuevas no coinciden.'})
    if len(nueva) < 8:
        return jsonify({'success': False, 'message': 'La nueva contraseña debe tener al menos 8 caracteres.'})
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT contrasena FROM usuarios WHERE id = %s', (session['user_id'],))
        row = cur.fetchone()
        if not row or not check_password_hash(row[0], actual):
            cur.close()
            return jsonify({'success': False, 'message': 'La contraseña actual es incorrecta.'})
        nuevo_hash = generate_password_hash(nueva)
        cur.execute('UPDATE usuarios SET contrasena = %s WHERE id = %s', (nuevo_hash, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente.'})
    except Exception as e:
        print('Error al cambiar contraseña:', e)
        return jsonify({'success': False, 'message': 'Error al cambiar la contraseña.'})

@app.route('/profile/tarjetas', methods=['GET'])
@login_required
def listar_tarjetas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, titular, numero, vencimiento, marca FROM tarjetas_credito WHERE usuario_id = %s', (session['user_id'],))
    tarjetas = [
        {
            'id': row[0],
            'titular': row[1],
            'numero': '**** **** **** ' + row[2][-4:],
            'vencimiento': row[3],
            'marca': row[4]
        } for row in cur.fetchall()
    ]
    cur.close()
    return jsonify({'tarjetas': tarjetas})

@app.route('/profile/tarjetas', methods=['POST'])
@login_required
def agregar_tarjeta():
    data = request.get_json()
    titular = data.get('titular')
    numero = data.get('numero')
    vencimiento = data.get('vencimiento')
    cvv = data.get('cvv')
    marca = data.get('marca')
    if not all([titular, numero, vencimiento, cvv]):
        return jsonify({'success': False, 'message': 'Completa todos los campos.'})
    try:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO tarjetas_credito (usuario_id, titular, numero, vencimiento, cvv, marca) VALUES (%s, %s, %s, %s, %s, %s)',
            (session['user_id'], titular, numero, vencimiento, cvv, marca))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Tarjeta agregada correctamente.'})
    except Exception as e:
        print('Error al agregar tarjeta:', e)
        return jsonify({'success': False, 'message': 'Error al agregar la tarjeta.'})

@app.route('/profile/tarjetas/<int:tarjeta_id>', methods=['DELETE'])
@login_required
def eliminar_tarjeta(tarjeta_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM tarjetas_credito WHERE id = %s AND usuario_id = %s', (tarjeta_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Tarjeta eliminada.'})
    except Exception as e:
        print('Error al eliminar tarjeta:', e)
        return jsonify({'success': False, 'message': 'Error al eliminar la tarjeta.'})

@app.route('/profile/tarjetas/<int:tarjeta_id>', methods=['PUT'])
@login_required
def editar_tarjeta(tarjeta_id):
    data = request.get_json()
    titular = data.get('titular')
    numero = data.get('numero')
    vencimiento = data.get('vencimiento')
    cvv = data.get('cvv')
    marca = data.get('marca')
    if not all([titular, numero, vencimiento, cvv]):
        return jsonify({'success': False, 'message': 'Completa todos los campos.'})
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE tarjetas_credito SET titular=%s, numero=%s, vencimiento=%s, cvv=%s, marca=%s WHERE id=%s AND usuario_id=%s',
            (titular, numero, vencimiento, cvv, marca, tarjeta_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Tarjeta actualizada correctamente.'})
    except Exception as e:
        print('Error al editar tarjeta:', e)
        return jsonify({'success': False, 'message': 'Error al editar la tarjeta.'})

@app.route('/profile/direcciones', methods=['GET'])
@login_required
def listar_direcciones():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, nombre, direccion, ciudad, departamento, pais, codigo_postal, telefono, tipo FROM direcciones WHERE usuario_id = %s', (session['user_id'],))
    direcciones = [
        {
            'id': row[0],
            'nombre': row[1],
            'direccion': row[2],
            'ciudad': row[3],
            'departamento': row[4],
            'pais': row[5],
            'codigo_postal': row[6],
            'telefono': row[7],
            'tipo': row[8]
        } for row in cur.fetchall()
    ]
    cur.close()
    return jsonify({'direcciones': direcciones})

@app.route('/profile/direcciones', methods=['POST'])
@login_required
def agregar_direccion():
    data = request.get_json()
    campos = ['nombre', 'direccion', 'ciudad', 'pais', 'telefono']
    if not all(data.get(c) for c in campos):
        return jsonify({'success': False, 'message': 'Completa todos los campos obligatorios.'})
    try:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO direcciones (usuario_id, nombre, direccion, ciudad, departamento, pais, codigo_postal, telefono, tipo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (session['user_id'], data['nombre'], data['direccion'], data['ciudad'], data.get('departamento',''), data['pais'], data.get('codigo_postal',''), data['telefono'], data.get('tipo','envio')))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Dirección agregada correctamente.'})
    except Exception as e:
        print('Error al agregar dirección:', e)
        return jsonify({'success': False, 'message': 'Error al agregar la dirección.'})

@app.route('/profile/direcciones/<int:direccion_id>', methods=['PUT'])
@login_required
def editar_direccion(direccion_id):
    data = request.get_json()
    campos = ['nombre', 'direccion', 'ciudad', 'pais', 'telefono']
    if not all(data.get(c) for c in campos):
        return jsonify({'success': False, 'message': 'Completa todos los campos obligatorios.'})
    try:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE direcciones SET nombre=%s, direccion=%s, ciudad=%s, departamento=%s, pais=%s, codigo_postal=%s, telefono=%s, tipo=%s WHERE id=%s AND usuario_id=%s',
            (data['nombre'], data['direccion'], data['ciudad'], data.get('departamento',''), data['pais'], data.get('codigo_postal',''), data['telefono'], data.get('tipo','envio'), direccion_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Dirección actualizada correctamente.'})
    except Exception as e:
        print('Error al editar dirección:', e)
        return jsonify({'success': False, 'message': 'Error al editar la dirección.'})

@app.route('/profile/direcciones/<int:direccion_id>', methods=['DELETE'])
@login_required
def eliminar_direccion(direccion_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM direcciones WHERE id = %s AND usuario_id = %s', (direccion_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Dirección eliminada.'})
    except Exception as e:
        print('Error al eliminar dirección:', e)
        return jsonify({'success': False, 'message': 'Error al eliminar la dirección.'})

@app.route('/marca/<nombre_marca>')
def marca_detalle(nombre_marca):
    # Diccionario de descripciones de marcas
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

if __name__ == '__main__':
    app.run(debug=True) 