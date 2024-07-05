from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: user.email' in str(e):
            return jsonify({'message': 'Email already exists'}), 400
        if 'UNIQUE constraint failed: user.username' in str(e):
            return jsonify({'message': 'Username already exists'}), 400
        return jsonify({'message': 'An error occurred'}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200
