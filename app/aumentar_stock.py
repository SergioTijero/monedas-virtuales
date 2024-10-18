from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .models import Stock
from . import db

aumentar_stock_blueprint = Blueprint('aumentar_stock', __name__)

@aumentar_stock_blueprint.route('/aumentar_stock', methods=['GET', 'POST'])
@login_required
def aumentar_stock():
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        stock = Stock.query.first()
        if not stock:
            stock = Stock(quantity=cantidad)
            db.session.add(stock)
        else:
            stock.quantity += cantidad
        db.session.commit()
        flash("Stock actualizado correctamente", "success")
        return redirect(url_for('options'))

    return render_template('aumentar_stock.html')
