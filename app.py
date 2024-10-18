from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.login import login_blueprint
from app.registrar_venta import registrar_venta_blueprint
from app.aumentar_stock import aumentar_stock_blueprint
from app.logout import logout_blueprint

# Inicialización de Flask y configuraciones
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lan_center.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'

# Registrar blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(registrar_venta_blueprint)
app.register_blueprint(aumentar_stock_blueprint)
app.register_blueprint(logout_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
