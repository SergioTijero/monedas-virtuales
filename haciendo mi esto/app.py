from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Cambia esto por una clave secreta más segura

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Conexión a MySQL
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",  # Cambia esto si usas otro usuario
        password="root",  # Cambia esto por tu contraseña
        database="sistema_monedas"  # Asegúrate de tener esta base de datos configurada
    )

# Inicializar base de datos
def inicializar_base_de_datos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    
    # Crear tabla de monedas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monedas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) UNIQUE NOT NULL,
            stock INT NOT NULL,
            precio_compra DECIMAL(10, 2),
            precio_venta DECIMAL(10, 2)
        )
    """)
    
    # Crear tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50),
            tipo_moneda VARCHAR(50),
            cantidad INT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear un usuario admin con contraseña cifrada
    hashed_password = generate_password_hash("admin123")
    cursor.execute("""
        INSERT INTO usuarios (username, password)
        VALUES ('admin', %s)
        ON DUPLICATE KEY UPDATE password = %s
    """, (hashed_password, hashed_password))
    
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return User(user['id']) if user else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            login_user(User(user['id']))
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
        cursor.execute("SELECT stock FROM monedas WHERE tipo = %s", (tipo_moneda,))
        resultado = cursor.fetchone()
        if resultado and cantidad <= resultado[0]:
            cursor.execute("INSERT INTO ventas (usuario, tipo_moneda, cantidad) VALUES (%s, %s, %s)", (usuario, tipo_moneda, cantidad))
            cursor.execute("UPDATE monedas SET stock = stock - %s WHERE tipo = %s", (cantidad, tipo_moneda))
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

        cursor.execute("""
            INSERT INTO monedas (tipo, stock, precio_compra, precio_venta)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            stock = stock + VALUES(stock), 
            precio_compra = VALUES(precio_compra), 
            precio_venta = VALUES(precio_venta)
        """, (tipo_moneda, cantidad, precio_compra, precio_venta))

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

@app.route('/')
@login_required
def home():
    return redirect(url_for('options'))

@app.route('/options')
@login_required
def options():
    return render_template('options.html')

# Nueva ruta para el historial de ventas
@app.route('/historial_ventas')
@login_required
def historial_ventas():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener historial de ventas
    cursor.execute("SELECT * FROM ventas ORDER BY fecha DESC")
    ventas = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('historial_ventas.html', ventas=ventas)

if __name__ == '__main__':
    inicializar_base_de_datos()
    app.run(debug=True)
