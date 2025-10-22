from flask import Blueprint, request, jsonify
from .models import User, db, SessionEntry
import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Hello, World!"

@main.route('/about')
def about():
    return "About Page"

@main.route('/add_session', methods=['POST'])
def add_session():
    data = request.get_json()
    new_session = SessionEntry(
        user_id=data.get('user_id'),
        start_time=datetime.datetime.strptime(data.get('start_time'), '%d-%m-%YT%H:%M:%S'),
        end_time=datetime.datetime.strptime(data.get('end_time'), '%d-%m-%YT%H:%M:%S')
    )

    db.session.add(new_session)
    db.session.commit()

    return jsonify({"message": "Session added successfully"}), 201

@main.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(
        email=data.get('email'),
        password=data.get('password')
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User added successfully"}), 201