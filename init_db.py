from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear las tablas en la base de datos
    db.create_all()

    # Crear un usuario de prueba
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password=generate_password_hash('admin123'))
        db.session.add(user)
        db.session.commit()

    print("Base de datos inicializada con éxito. Usuario creado: admin / Contraseña: admin123")
