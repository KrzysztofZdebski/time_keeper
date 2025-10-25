from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, db, SessionEntry
from werkzeug.security import check_password_hash
import datetime


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email,password=password).first()

        if user :
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))
        else:
            flash('Nieprawidłowy email lub hasło', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    projects = [
        {'id': 1, 'name': 'Projekt A'},
        {'id': 2, 'name': 'Projekt B'},
        {'id': 3, 'name': 'Projekt C'}
    ]

    return render_template('dashboard.html', projects=projects)


@main.route('/start_session', methods=['POST'])
def start_session():
    user_id = session.get('user_id')
    if not user_id:
        flash("Musisz się zalogować", "error")
        return redirect(url_for('main.login'))

    project_id = request.form.get('project_id')  # jeśli będziesz potrzebował projektu

    new_session = SessionEntry(
        user_id=user_id,
        start_time=datetime.datetime.now(),
        end_time=None
    )
    db.session.add(new_session)
    db.session.commit()
    flash("Sesja rozpoczęta!", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/stop_session', methods=['POST'])
def stop_session():
    user_id = session.get('user_id')
    if not user_id:
        flash("Musisz się zalogować", "error")
        return redirect(url_for('main.login'))

    # Pobieramy ostatnią sesję bez end_time dla tego użytkownika
    last_session = SessionEntry.query.filter_by(user_id=user_id, end_time=None).order_by(SessionEntry.start_time.desc()).first()

    if not last_session:
        flash("Brak aktywnej sesji do zakończenia", "error")
        return redirect(url_for('main.dashboard'))

    last_session.end_time = datetime.datetime.now()
    db.session.commit()
    flash("Sesja zakończona!", "success")
    return redirect(url_for('main.dashboard'))