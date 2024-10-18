from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .models import Stock, Sale
from . import db

registrar_venta_blueprint = Blueprint('registrar_venta', __name__)

@registrar_venta_blueprint.route('/registrar_venta', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    if request.method == 'POST':
        usuario = request.form['usuario']
        cantidad = int(request.form['cantidad'])

        stock = Stock.query.first()
        if stock and cantidad <= stock.quantity:
            nueva_venta = Sale(user=usuario, quantity=cantidad)
            db.session.add(nueva_venta)
            stock.quantity -= cantidad
            db.session.commit()
            flash("Venta registrada exitosamente", "success")
        else:
            flash("Stock insuficiente para realizar la venta", "danger")

        return redirect(url_for('options'))

    return render_template('registrar_venta.html')
