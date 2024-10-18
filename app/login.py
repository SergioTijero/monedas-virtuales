from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from .models import User

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.options'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html')  # Aquí debe estar bien ubicado el template 'login.html'

@login_blueprint.route('/test')
def test():
        return "Página de prueba funcionando correctamente"
