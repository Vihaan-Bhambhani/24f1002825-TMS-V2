from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/api/login', methods=['POST'])
def login():
    """Login for all roles. Returns JWT token."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.is_blacklisted:
        return jsonify({'error': 'Your account has been suspended'}), 403

    if not user.is_active:
        return jsonify({'error': 'Your account is inactive'}), 403

    # Create JWT token with user identity and role
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    }), 200


@auth.route('/api/register', methods=['POST'])
def register():
    """Register a new trekker account. Staff/Admin cannot self-register."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    # Validation
    if not all([name, email, password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Create trekker user (only role allowed for self-registration)
    new_user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role='trekker'
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201
