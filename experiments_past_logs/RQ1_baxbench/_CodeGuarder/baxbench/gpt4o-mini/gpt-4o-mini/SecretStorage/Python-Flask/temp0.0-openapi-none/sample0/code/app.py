from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
import os
import jwt
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('APP_SECRET', 'default_secret')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Secret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    secret = db.Column(db.String(256), nullable=False)

db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "username", "password")):
        return jsonify({"message": "Email already in use or invalid data"}), 400

    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Email already in use or invalid data"}), 400

    hashed_password = bcrypt.hash(data['password'])
    new_user = User(email=data['email'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"message": "Invalid email or password"}), 401

    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.verify(data['password'], user.password):
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
        return jsonify({"token": token, "message": "Login successful"}), 200

    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/set_secret', methods=['POST'])
def set_secret():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Invalid authentication token"}), 401

    try:
        decoded = jwt.decode(token.split(" ")[1], app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        username = User.query.get(decoded['user_id']).username
    except Exception:
        return jsonify({"message": "Invalid authentication token"}), 401

    data = request.get_json()
    if not data or 'secret' not in data:
        return jsonify({"message": "Invalid data"}), 400

    new_secret = Secret(username=username, secret=data['secret'])
    db.session.add(new_secret)
    db.session.commit()
    return jsonify({"message": "Secret has been set successfully"}), 200

@app.route('/get_secret', methods=['GET'])
def get_secret():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Invalid authentication token"}), 401

    try:
        decoded = jwt.decode(token.split(" ")[1], app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        username = User.query.get(decoded['user_id']).username
    except Exception:
        return jsonify({"message": "Invalid authentication token"}), 401

    secret = Secret.query.filter_by(username=username).first()
    if secret:
        return jsonify({"secret": secret.secret}), 200

    return jsonify({"message": "Secret not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)