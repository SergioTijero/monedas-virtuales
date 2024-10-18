from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulamos una lista de usuarios (sin base de datos)
usuarios = {'admin': {'password': '1234'}}

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in usuarios:
        return User(user_id)
    return None

# Inicializar stock de monedas y lista de ventas
monedas_stock = {
    'pavos': {'stock': 1000, 'precio_compra': 0.5, 'precio_venta': 1.0},
    'robux': {'stock': 1000, 'precio_compra': 1.0, 'precio_venta': 2.0},
    'riot_points': {'stock': 1000, 'precio_compra': 1.5, 'precio_venta': 3.0},
    'minecraft': {'stock': 1000, 'precio_compra': 2.0, 'precio_venta': 4.0},
}
ventas = []
compras_registradas = []

@app.route('/')
@login_required
def home():
    return redirect(url_for('options'))

# Ruta de inicio (con inicio de sesión)
@app.route('/index')
def index():
    return render_template('index.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar credenciales
        if username in usuarios and usuarios[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Inicio de sesión exitoso')
            return redirect(url_for('options'))
        else:
            flash('Nombre de usuario o contraseña incorrectos')
            return redirect(url_for('login'))

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente')
    return redirect(url_for('login'))

# Página para registrar ventas (protegida por login)
@app.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    if request.method == 'POST':
        tipo_moneda = request.form['tipo_moneda']
        cantidad_monedas = request.form['cantidad_monedas']
        precio_final = request.form['precio_final']
        cliente = request.form['cliente']

        # Añadir venta a la lista de ventas (sin base de datos)
        ventas.append({
            'tipo_moneda': tipo_moneda,
            'cantidad_monedas': cantidad_monedas,
            'precio_final': precio_final,
            'cliente': cliente
        })

        flash('Venta registrada exitosamente')
        return redirect(url_for('ultimas_ventas'))

    return render_template('ventas.html')

# Página para ver las últimas ventas (protegida por login)
@app.route('/ultimas-ventas')
@login_required
def ultimas_ventas():
    return render_template('ultimas_ventas.html', ventas=ventas)

@app.route('/aumentar_stock', methods=['GET', 'POST'])
@login_required
def aumentar_stock():
    global monedas_stock, compras_registradas
    if request.method == 'POST':
        tipo_moneda = request.form['tipo_moneda']
        cantidad = int(request.form['cantidad'])
        precio_compra = float(request.form['precio_compra'])
        saldo_proveedor = float(request.form['saldo_proveedor'])

        if tipo_moneda in monedas_stock:
            monedas_stock[tipo_moneda]['stock'] += cantidad
            monedas_stock[tipo_moneda]['precio_compra'] = precio_compra
            
            # Registrar la compra
            compras_registradas.append({
                'tipo_moneda': tipo_moneda,
                'cantidad': cantidad,
                'precio_compra': precio_compra,
                'saldo_proveedor': saldo_proveedor
            })

            flash("Stock actualizado correctamente", "success")
        else:
            flash("Tipo de moneda no encontrado", "danger")

        return redirect(url_for('options'))

    return render_template('aumentar_stock.html', monedas=list(monedas_stock.keys()))

@app.route('/options')
@login_required
def options():
    return render_template('options.html')

if __name__ == '__main__':
    app.run(debug=True)
