from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from .models import User, Stock, Sale
from . import db

main = Blueprint('main', __name__)


# Ruta de inicio de sesión
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.menu'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')


# Ruta de cierre de sesión
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('main.login'))


# Menú principal
@main.route('/menu')
@login_required
def menu():
    return render_template('main_menu.html')


# Gestión de stock
@main.route('/gestionar_stock', methods=['GET', 'POST'])
@login_required
def gestionar_stock():
    if request.method == 'POST':
        currency_type = request.form['currency_type']
        quantity = int(request.form['quantity'])

        stock = Stock.query.filter_by(currency_type=currency_type).first()
        if stock:
            stock.quantity += quantity
        else:
            stock = Stock(currency_type=currency_type, quantity=quantity)
            db.session.add(stock)

        db.session.commit()
        flash('Stock actualizado con éxito', 'success')

    stocks = Stock.query.all()
    return render_template('gestionar_stock.html', stocks=stocks)


# Registrar una venta
@main.route('/registrar_venta', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    if request.method == 'POST':
        customer_nickname = request.form['customer_nickname']
        currency_type = request.form['currency_type']
        amount = int(request.form['amount'])

        stock = Stock.query.filter_by(currency_type=currency_type).first()
        if stock and stock.quantity >= amount:
            stock.quantity -= amount
            sale = Sale(customer_nickname=customer_nickname, currency_type=currency_type,
                        amount=amount, remaining_stock=stock.quantity)
            db.session.add(sale)
            db.session.commit()
            flash('Venta registrada con éxito', 'success')
        else:
            flash('Stock insuficiente', 'danger')

    sales = Sale.query.order_by(Sale.id.desc()).limit(5).all()  # Últimas 5 ventas
    return render_template('registrar_venta.html', sales=sales)
