
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.aumentar_stock import aumentar_stock_blueprint
from app.logout import logout_blueprint
from app.registrar_venta import registrar_venta_blueprint

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key"

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monedas_virtuales.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login.login'

    # Register blueprints
    from .login import login_blueprint
    app.register_blueprint(login_blueprint)
    app.register_blueprint(registrar_venta_blueprint)
    app.register_blueprint(aumentar_stock_blueprint)
    app.register_blueprint(logout_blueprint)

    # Importar modelos después de inicializar la app
    from .models import User

    # Definir user_loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Return the user object for the given user_id
        return User.query.get(int(user_id))

    return app
