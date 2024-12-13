from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Cambia esto por una clave secreta más segura

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ruta de la base de datos SQLite
DATABASE = 'sistema_monedas.db'

# Conexión a SQLite
def obtener_conexion():
    return sqlite3.connect(DATABASE)

# Inicializar base de datos
def inicializar_base_de_datos():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Crear tabla de monedas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT UNIQUE NOT NULL,
            stock INTEGER NOT NULL,
            precio_compra REAL,
            precio_venta REAL
        )
    ''')

    # Crear tabla de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            tipo_moneda TEXT,
            cantidad INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Crear un usuario admin con contraseña cifrada
    hashed_password = generate_password_hash("admin123")
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (username, password)
        VALUES (?, ?)
    ''', ("admin", hashed_password))

    conn.commit()
    cursor.close()
    conn.close()

# Modelo de usuario
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return User(user[0]) if user else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            login_user(User(user[0]))
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('options'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
        cursor.close()
        conn.close()
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/registrar_venta', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Obtener lista de monedas
    cursor.execute("SELECT tipo FROM monedas")
    monedas = [fila[0] for fila in cursor.fetchall()]

    if request.method == 'POST':
        usuario = request.form['usuario']
        cantidad = int(request.form['cantidad'])
        tipo_moneda = request.form['tipo_moneda']
        cursor.execute("SELECT stock FROM monedas WHERE tipo = ?", (tipo_moneda,))
        resultado = cursor.fetchone()
        if resultado and cantidad <= resultado[0]:
            cursor.execute("INSERT INTO ventas (usuario, tipo_moneda, cantidad) VALUES (?, ?, ?)", (usuario, tipo_moneda, cantidad))
            cursor.execute("UPDATE monedas SET stock = stock - ? WHERE tipo = ?", (cantidad, tipo_moneda))
            conn.commit()
            flash("Venta registrada exitosamente", "success")
        else:
            flash("Stock insuficiente", "danger")
        return redirect(url_for('options'))

    cursor.close()
    conn.close()
    return render_template('registrar_venta.html', monedas=monedas)

@app.route('/aumentar_stock', methods=['GET', 'POST'])
@login_required
def aumentar_stock():
    if request.method == 'POST':
        tipo_moneda = request.form['tipo_moneda']
        cantidad = int(request.form['cantidad'])
        precio_compra = float(request.form['precio_compra'])

        # Verificar si 'precio_venta' está en el formulario
        if 'precio_venta' not in request.form:
            flash("El campo precio de venta es obligatorio.", "danger")
            return redirect(url_for('aumentar_stock'))

        precio_venta = float(request.form['precio_venta'])

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO monedas (tipo, stock, precio_compra, precio_venta)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tipo) DO UPDATE SET
            stock = stock + excluded.stock,
            precio_compra = excluded.precio_compra,
            precio_venta = excluded.precio_venta
        ''', (tipo_moneda, cantidad, precio_compra, precio_venta))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Stock actualizado correctamente", "success")
        return redirect(url_for('options'))

    # Obtener la lista de monedas de la base de datos
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM monedas")
    monedas = [fila[0] for fila in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('aumentar_stock.html', monedas=monedas)

@app.route('/registrar_moneda', methods=['GET', 'POST'])
@login_required
def registrar_moneda():
    if request.method == 'POST':
        tipo = request.form['tipo']
        stock = int(request.form['stock'])
        precio_compra = float(request.form['precio_compra'])
        precio_venta = float(request.form['precio_venta'])

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO monedas (tipo, stock, precio_compra, precio_venta)
                VALUES (?, ?, ?, ?)
            ''', (tipo, stock, precio_compra, precio_venta))
            conn.commit()
            flash("Moneda registrada exitosamente", "success")
        except sqlite3.IntegrityError:
            flash("La moneda ya existe", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('options'))

    return render_template('registrar_moneda.html')

@app.route('/ver_stock')
@login_required
def ver_stock():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, stock, precio_compra, precio_venta FROM monedas")
    stock = [{'tipo': row[0], 'stock': row[1], 'precio_compra': row[2], 'precio_venta': row[3]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template('ver_stock.html', stock=stock)

@app.route('/')
@login_required
def home():
    return redirect(url_for('options'))

@app.route('/options')
@login_required
def options():
    return render_template('options.html')

@app.route('/historial_ventas')
@login_required
def historial_ventas():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Obtener historial de ventas
    cursor.execute("SELECT usuario, tipo_moneda, cantidad, fecha FROM ventas ORDER BY fecha DESC")
    ventas = [{'usuario': row[0], 'tipo_moneda': row[1], 'cantidad': row[2], 'fecha': row[3]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('historial_ventas.html', ventas=ventas)

@app.route('/compras')
@login_required
def compras():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Obtener compras registradas
    cursor.execute("""
        SELECT stock, tipo, precio_compra, precio_venta
        FROM monedas
    """)
    compras = [{'cantidad': row[0], 'nombre': row[1], 'precio_compra': row[2], 'precio_venta': row[3]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('compras.html', compras=compras)

if __name__ == '__main__':
    inicializar_base_de_datos()
    app.run(debug=True)
