from app import create_app, db
from app.models import Stock, User

app = create_app()

with app.app_context():
    db.create_all()

    # Inicializa el stock si no existe
    if not Stock.query.first():
        stock_inicial = Stock(quantity=1000)  # Stock inicial
        db.session.add(stock_inicial)

    # Crea un usuario de prueba
    if not User.query.filter_by(username='admin').first():
        usuario_admin = User(username='admin', password='admin123')
        db.session.add(usuario_admin)

    db.session.commit()

print("Base de datos inicializada.")
