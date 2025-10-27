from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, db, SessionEntry
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from sqlalchemy import and_
import pandas as pd


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

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Sprawdź czy hasła się zgadzają
        if password != confirm_password:
            flash('Hasła nie są zgodne', 'error')
            return redirect(url_for('main.register'))

        # Sprawdź czy użytkownik już istnieje
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email już jest zarejestrowany', 'error')
            return redirect(url_for('main.register'))

        # Utwórz nowego użytkownika
        new_user = User(
            email=email,
            password=password  # Uwaga: dla bezpieczeństwa powinieneś użyć generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Konto zostało utworzone! Możesz się teraz zalogować.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

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
        end_time=None,
        project_id = project_id
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

@main.route('/generate_report', methods=['POST'])
def generate_report():
    user_id = session.get('user_id')
    if not user_id:
        flash("Musisz się zalogować", "error")
        return redirect(url_for('main.login'))
    
    start_str = request.form.get('start')
    end_str = request.form.get('end')

    # Parsowanie na obiekt datetime (z formatu Y-m-d H:i)
    fmt = "%Y-%m-%d %H:%M"
    start_dt = datetime.datetime.strptime(start_str, fmt)
    end_dt = datetime.datetime.strptime(end_str, fmt)

    results = SessionEntry.query.filter(
    and_(
        SessionEntry.user_id == user_id,
        SessionEntry.start_time >= start_dt,
        SessionEntry.end_time <= end_dt
    )
    ).order_by(SessionEntry.start_time).all()
    if not results:
        return redirect(url_for("main.dashboard"))
    df = pd.DataFrame([{
        "project_id": r.project_id,
        "start": r.start_time,
        "end": r.end_time
    } for r in results])
    
    # Oblicz długość sesji w godzinach
    df["duration"] = (df["end"] - df["start"]).dt.total_seconds() / 3600.0
    df["day"] = df["start"].dt.date

    # Grupowanie po dniu i projekcie
    grouped = df.groupby(["day", "project_id"])["duration"].sum().reset_index()

    # Pivot – każdy projekt osobno jako kolumna
    pivot = grouped.pivot(index="day", columns="project_id", values="duration").fillna(0)

    # Konwersja do list do przekazania do Chart.js
    labels = pivot.index.astype(str).tolist()
    datasets = []
    for project_id in pivot.columns:
        datasets.append({
            "label": f"Projekt {project_id}",
            "data": pivot[project_id].round(2).tolist(),
        })

    user = User.query.filter_by(id=user_id).all()
    user_name = str(user).removeprefix('[<').removesuffix('>]').removeprefix('User')
    chart_data = {"labels": labels, "datasets": datasets}
    return render_template("report.html", chart_data=chart_data, user_name=user_name, date=datetime.datetime.now(), start_str=start_str, end_str=end_str )