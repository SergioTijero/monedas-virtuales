from flask import Blueprint, redirect, url_for, flash
from flask_login import logout_user, login_required

logout_blueprint = Blueprint('logout', __name__)

@logout_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login.login'))
