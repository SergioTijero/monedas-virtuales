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

# Funciones auxiliares para estadísticas
def obtener_estadisticas_dashboard():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Total de tipos de monedas
    cursor.execute("SELECT COUNT(*) FROM monedas WHERE activo = 1")
    total_monedas = cursor.fetchone()[0]
    
    # Total stock
    cursor.execute("SELECT SUM(stock) FROM monedas WHERE activo = 1")
    total_stock = cursor.fetchone()[0] or 0
    
    # Ventas del mes actual
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(total), 0) 
        FROM ventas 
        WHERE date(fecha) >= date('now', 'start of month')
    """)
    ventas_mes = cursor.fetchone()
    
    # Monedas con stock bajo
    cursor.execute("SELECT COUNT(*) FROM monedas WHERE stock <= stock_minimo AND activo = 1")
    stock_bajo = cursor.fetchone()[0]
    
    # Top 5 monedas más vendidas
    cursor.execute("""
        SELECT tipo_moneda, SUM(cantidad) as total_vendido
        FROM ventas 
        WHERE date(fecha) >= date('now', '-7 days')
        GROUP BY tipo_moneda
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    top_monedas = cursor.fetchall()
    
    # Alertas de stock
    cursor.execute("""
        SELECT tipo, stock, stock_minimo
        FROM monedas 
        WHERE stock <= stock_minimo AND activo = 1
        ORDER BY stock ASC
    """)
    alertas_stock = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'total_monedas': total_monedas,
        'total_stock': total_stock,
        'ventas_mes_cantidad': ventas_mes[0],
        'ventas_mes_ingresos': ventas_mes[1],
        'stock_bajo': stock_bajo,
        'top_monedas': top_monedas,
        'alertas_stock': alertas_stock
    }

def obtener_ganancias_por_moneda():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.tipo, m.precio_compra, m.precio_venta,
               COALESCE(SUM(v.cantidad), 0) as total_vendido,
               COALESCE(SUM(v.ganancia), 0) as ganancia_total,
               ((m.precio_venta - m.precio_compra) / m.precio_compra * 100) as margen_porcentaje
        FROM monedas m
        LEFT JOIN ventas v ON m.tipo = v.tipo_moneda
        WHERE m.activo = 1
        GROUP BY m.tipo
        ORDER BY ganancia_total DESC
    """)
    
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return resultados

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
            precio_venta REAL,
            categoria TEXT DEFAULT 'Otros',
            stock_minimo INTEGER DEFAULT 10,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Agregar columnas si no existen (para bases de datos existentes)
    try:
        cursor.execute('ALTER TABLE monedas ADD COLUMN categoria TEXT DEFAULT "Otros"')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE monedas ADD COLUMN stock_minimo INTEGER DEFAULT 10')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE monedas ADD COLUMN activo BOOLEAN DEFAULT 1')
    except sqlite3.OperationalError:
        pass

    # Crear tabla de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            tipo_moneda TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            total REAL,
            ganancia REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Agregar columnas a ventas si no existen
    try:
        cursor.execute('ALTER TABLE ventas ADD COLUMN precio_unitario REAL')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE ventas ADD COLUMN total REAL')
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute('ALTER TABLE ventas ADD COLUMN ganancia REAL')
    except sqlite3.OperationalError:
        pass
    
    # Crear tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            total_compras REAL DEFAULT 0,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Crear tabla de compras/reabastecimiento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_moneda TEXT,
            cantidad INTEGER,
            precio_unitario REAL,
            total REAL,
            proveedor TEXT,
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

    # Obtener lista de monedas activas con precios
    cursor.execute("SELECT tipo, precio_venta, stock FROM monedas WHERE activo = 1 ORDER BY tipo")
    monedas = cursor.fetchall()

    if request.method == 'POST':
        usuario = request.form['usuario']
        cantidad = int(request.form['cantidad'])
        tipo_moneda = request.form['tipo_moneda']
        
        # Obtener información de la moneda
        cursor.execute("SELECT stock, precio_compra, precio_venta FROM monedas WHERE tipo = ?", (tipo_moneda,))
        resultado = cursor.fetchone()
        
        if resultado and cantidad <= resultado[0]:
            stock_actual, precio_compra, precio_venta = resultado
            total = cantidad * precio_venta
            ganancia = cantidad * (precio_venta - precio_compra)
            
            # Registrar la venta
            cursor.execute("""
                INSERT INTO ventas (usuario, tipo_moneda, cantidad, precio_unitario, total, ganancia) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (usuario, tipo_moneda, cantidad, precio_venta, total, ganancia))
            
            # Actualizar stock
            cursor.execute("UPDATE monedas SET stock = stock - ? WHERE tipo = ?", (cantidad, tipo_moneda))
            
            conn.commit()
            
            # Verificar si el stock quedó bajo
            nuevo_stock = stock_actual - cantidad
            cursor.execute("SELECT stock_minimo FROM monedas WHERE tipo = ?", (tipo_moneda,))
            stock_minimo = cursor.fetchone()[0]
            
            if nuevo_stock <= stock_minimo:
                flash(f"⚠️ ALERTA: {tipo_moneda} tiene stock bajo ({nuevo_stock} unidades)", "warning")
            
            flash(f"✅ Venta registrada: {cantidad} {tipo_moneda} - Total: ${total:.2f} - Ganancia: ${ganancia:.2f}", "success")
        else:
            flash("❌ Stock insuficiente", "danger")
            
        cursor.close()
        conn.close()
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
        categoria = request.form['categoria']
        stock_minimo = int(request.form.get('stock_minimo', 10))

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO monedas (tipo, stock, precio_compra, precio_venta, categoria, stock_minimo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, stock, precio_compra, precio_venta, categoria, stock_minimo))
            
            # Registrar como compra inicial
            total_compra = stock * precio_compra
            cursor.execute('''
                INSERT INTO compras (tipo_moneda, cantidad, precio_unitario, total, proveedor)
                VALUES (?, ?, ?, ?, ?)
            ''', (tipo, stock, precio_compra, total_compra, 'Stock Inicial'))
            
            conn.commit()
            flash(f"✅ Moneda {tipo} registrada exitosamente en categoría {categoria}", "success")
        except sqlite3.IntegrityError:
            flash("❌ La moneda ya existe", "danger")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('options'))

    # Categorías predefinidas para LAN Center
    categorias = [
        'League of Legends', 'Fortnite', 'Roblox', 'Valorant', 
        'Counter-Strike', 'Steam', 'Xbox', 'PlayStation', 
        'Mobile Games', 'Otros'
    ]
    
    return render_template('registrar_moneda.html', categorias=categorias)

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
    estadisticas = obtener_estadisticas_dashboard()
    return render_template('options.html', stats=estadisticas)

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

# Nuevas rutas para funcionalidades avanzadas

@app.route('/dashboard_analytics')
@login_required
def dashboard_analytics():
    estadisticas = obtener_estadisticas_dashboard()
    ganancias = obtener_ganancias_por_moneda()
    return render_template('dashboard_analytics.html', stats=estadisticas, ganancias=ganancias)

@app.route('/clientes')
@login_required
def gestionar_clientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, COUNT(v.id) as total_compras_num
        FROM clientes c
        LEFT JOIN ventas v ON c.nombre = v.usuario
        WHERE c.activo = 1
        GROUP BY c.id
        ORDER BY c.total_compras DESC
    """)
    clientes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('clientes.html', clientes=clientes)

@app.route('/reportes')
@login_required
def reportes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Reporte de ventas por categoría
    cursor.execute("""
        SELECT m.categoria, COUNT(v.id) as total_ventas, SUM(v.total) as ingresos_total
        FROM ventas v
        JOIN monedas m ON v.tipo_moneda = m.tipo
        WHERE date(v.fecha) >= date('now', '-30 days')
        GROUP BY m.categoria
        ORDER BY ingresos_total DESC
    """)
    ventas_categoria = cursor.fetchall()
    
    # Reporte diario de la semana
    cursor.execute("""
        SELECT date(fecha) as dia, COUNT(*) as ventas, SUM(total) as ingresos
        FROM ventas
        WHERE date(fecha) >= date('now', '-7 days')
        GROUP BY date(fecha)
        ORDER BY fecha DESC
    """)
    ventas_semana = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reportes.html', 
                         ventas_categoria=ventas_categoria,
                         ventas_semana=ventas_semana)

@app.route('/alertas')
@login_required
def alertas():
    estadisticas = obtener_estadisticas_dashboard()
    return render_template('alertas.html', alertas=estadisticas['alertas_stock'])

@app.route('/api/actualizar_stock_minimo', methods=['POST'])
@login_required
def actualizar_stock_minimo():
    tipo_moneda = request.form['tipo_moneda']
    nuevo_minimo = int(request.form['stock_minimo'])
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE monedas SET stock_minimo = ? WHERE tipo = ?", (nuevo_minimo, tipo_moneda))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f"Stock mínimo de {tipo_moneda} actualizado a {nuevo_minimo}", "success")
    return redirect(url_for('ver_stock'))

if __name__ == '__main__':
    inicializar_base_de_datos()
    # Configurar para EC2: host='0.0.0.0' permite acceso externo
    app.run(debug=True, host='0.0.0.0', port=8080)
