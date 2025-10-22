from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, db
from werkzeug.security import check_password_hash

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return redirect(url_for('routes.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Nieprawidłowy email lub hasło', 'error')
            return redirect(url_for('routes.login'))

    return render_template('login.html')

@bp.route('/dashboard')
def dashboard():
    return "<h2>Witaj w panelu użytkownika!</h2>"
