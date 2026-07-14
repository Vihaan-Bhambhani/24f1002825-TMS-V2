from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def admin_required(fn):
    """Decorator that checks if the logged-in user is an admin."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def staff_required(fn):
    """Decorator that checks if the logged-in user is staff."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'staff':
            return jsonify({'error': 'Staff access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def login_required(fn):
    """Decorator that checks if user is logged in (any role)."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
