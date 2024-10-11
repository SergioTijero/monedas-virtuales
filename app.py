from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necesario para manejar sesiones y mensajes flash

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Datos ficticios para autenticación (en adelane se reemplazará con una base de datos)
users = {'admin': {'password': 'password123'}}

# Modelo de usuario
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"{self.id}"

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Inicializar stock de monedas y lista de ventas
monedas_stock = 1000
ventas_registradas = []

@app.route('/')
@login_required
def index():
    return render_template('index.html', stock=monedas_stock, ventas=ventas_registradas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario y contraseña son correctos
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/registrar_venta', methods=['POST'])
@login_required
def registrar_venta():
    global monedas_stock
    usuario = request.form['usuario']
    cantidad = int(request.form['cantidad'])

    if cantidad <= monedas_stock:
        ventas_registradas.append({'usuario': usuario, 'cantidad': cantidad})
        monedas_stock -= cantidad
        flash("Venta registrada exitosamente", "success")
    else:
        flash("Stock insuficiente para realizar la venta", "danger")

    return redirect(url_for('index'))

@app.route('/aumentar_stock', methods=['POST'])
@login_required
def aumentar_stock():
    global monedas_stock
    cantidad = int(request.form['cantidad'])
    monedas_stock += cantidad
    flash("Stock actualizado correctamente", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
