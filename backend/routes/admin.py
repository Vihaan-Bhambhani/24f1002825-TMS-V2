from datetime import datetime, date
import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User, StaffProfile, Trek, Booking
from utils.auth_helpers import admin_required
from utils.cache import cache_get, cache_set, cache_delete

admin = Blueprint('admin', __name__)


def parse_date(date_str):
    """Parse a date string (yyyy-mm-dd) to a Python date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


# ──────────────── Dashboard Stats ────────────────

@admin.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    """Dashboard summary stats (cached)."""
    cached = cache_get('admin:stats')
    if cached:
        return jsonify(cached)

    stats = {
        'total_treks': Trek.query.count(),
        'total_users': User.query.filter_by(role='trekker').count(),
        'total_staff': User.query.filter_by(role='staff').count(),
        'total_bookings': Booking.query.count()
    }
    cache_set('admin:stats', stats, ttl=60)
    return jsonify(stats)


# ──────────────── Trek Management ────────────────

@admin.route('/api/admin/treks', methods=['GET'])
@admin_required
def get_treks():
    """List all treks (cached)."""
    cached = cache_get('admin:treks')
    if cached:
        return jsonify(cached)

    treks = Trek.query.all()
    result = []
    for t in treks:
        staff_name = None
        if t.assigned_staff:
            staff_user = User.query.get(t.assigned_staff)
            if staff_user:
                staff_name = staff_user.name
        result.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'duration': t.duration,
            'available_slots': t.available_slots,
            'description': t.description,
            'status': t.status,
            'start_date': str(t.start_date) if t.start_date else None,
            'end_date': str(t.end_date) if t.end_date else None,
            'assigned_staff': t.assigned_staff,
            'staff_name': staff_name
        })
    cache_set('admin:treks', result, ttl=120)
    return jsonify(result)


@admin.route('/api/admin/treks', methods=['POST'])
@admin_required
def create_trek():
    """Create a new trek."""
    data = request.get_json()

    # Validation
    required = ['name', 'location', 'difficulty', 'duration', 'available_slots']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if data['difficulty'] not in ['easy', 'moderate', 'hard']:
        return jsonify({'error': 'Difficulty must be easy, moderate, or hard'}), 400

    trek = Trek(
        name=data['name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration=int(data['duration']),
        available_slots=int(data['available_slots']),
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date'))
    )
    db.session.add(trek)
    db.session.commit()
    cache_delete('admin:*')  # Invalidate admin cache

    return jsonify({'message': 'Trek created', 'id': trek.id}), 201


@admin.route('/api/admin/treks/<int:trek_id>', methods=['PUT'])
@admin_required
def update_trek(trek_id):
    """Update an existing trek."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    data = request.get_json()
    trek.name = data.get('name', trek.name)
    trek.location = data.get('location', trek.location)
    trek.difficulty = data.get('difficulty', trek.difficulty)
    trek.duration = data.get('duration', trek.duration)
    trek.available_slots = data.get('available_slots', trek.available_slots)
    trek.description = data.get('description', trek.description)
    trek.status = data.get('status', trek.status)
    if 'start_date' in data:
        trek.start_date = parse_date(data['start_date'])
    if 'end_date' in data:
        trek.end_date = parse_date(data['end_date'])

    db.session.commit()
    cache_delete('admin:*')
    return jsonify({'message': 'Trek updated'})


@admin.route('/api/admin/treks/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):
    """Delete a trek."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Delete related bookings first
    Booking.query.filter_by(trek_id=trek_id).delete()
    db.session.delete(trek)
    db.session.commit()
    cache_delete('admin:*')
    return jsonify({'message': 'Trek deleted'})


@admin.route('/api/admin/treks/<int:trek_id>/assign', methods=['PUT'])
@admin_required
def assign_staff(trek_id):
    """Assign a staff member to a trek."""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    data = request.get_json()
    staff_id = data.get('staff_id')

    if staff_id:
        staff_user = User.query.filter_by(id=staff_id, role='staff').first()
        if not staff_user:
            return jsonify({'error': 'Staff member not found'}), 404
        trek.assigned_staff = staff_id
    else:
        trek.assigned_staff = None

    db.session.commit()
    return jsonify({'message': 'Staff assigned to trek'})


# ──────────────── Staff Management ────────────────

@admin.route('/api/admin/staff', methods=['GET'])
@admin_required
def get_staff():
    """List all staff members."""
    staff_users = User.query.filter_by(role='staff').all()
    result = []
    for u in staff_users:
        profile = StaffProfile.query.filter_by(user_id=u.id).first()
        result.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'is_active': u.is_active,
            'is_blacklisted': u.is_blacklisted,
            'phone': profile.phone if profile else '',
            'bio': profile.bio if profile else '',
            'created_at': str(u.created_at)
        })
    return jsonify(result)


@admin.route('/api/admin/staff', methods=['POST'])
@admin_required
def create_staff():
    """Create a new staff member (User + StaffProfile)."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    # Create user with staff role
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role='staff'
    )
    db.session.add(user)
    db.session.flush()  # Get user.id before commit

    # Create staff profile
    profile = StaffProfile(
        user_id=user.id,
        phone=data.get('phone', ''),
        bio=data.get('bio', '')
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({'message': 'Staff member created', 'id': user.id}), 201


# ──────────────── User Management ────────────────

@admin.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """List all trekker users."""
    users = User.query.filter_by(role='trekker').all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'is_active': u.is_active,
            'is_blacklisted': u.is_blacklisted,
            'created_at': str(u.created_at)
        })
    return jsonify(result)


@admin.route('/api/admin/users/<int:user_id>/blacklist', methods=['PUT'])
@admin_required
def toggle_blacklist(user_id):
    """Toggle blacklist status for a user or staff."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.role == 'admin':
        return jsonify({'error': 'Cannot blacklist admin'}), 400

    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()

    status = 'blacklisted' if user.is_blacklisted else 'unblacklisted'
    return jsonify({'message': f'User {status}'})


# ──────────────── Bookings ────────────────

@admin.route('/api/admin/bookings', methods=['GET'])
@admin_required
def get_bookings():
    """List all bookings."""
    bookings = Booking.query.all()
    result = []
    for b in bookings:
        user = User.query.get(b.user_id)
        trek = Trek.query.get(b.trek_id)
        result.append({
            'id': b.id,
            'user_name': user.name if user else 'Unknown',
            'user_email': user.email if user else '',
            'trek_name': trek.name if trek else 'Unknown',
            'booking_date': str(b.booking_date),
            'booking_status': b.booking_status
        })
    return jsonify(result)


# ──────────────── Search ────────────────

@admin.route('/api/admin/search', methods=['GET'])
@admin_required
def search():
    """Search treks, staff, and users by name/email."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'treks': [], 'staff': [], 'users': []})

    search_term = f'%{q}%'

    # Search treks
    treks = Trek.query.filter(
        (Trek.name.ilike(search_term)) | (Trek.location.ilike(search_term))
    ).all()

    # Search staff
    staff = User.query.filter(
        User.role == 'staff',
        (User.name.ilike(search_term)) | (User.email.ilike(search_term))
    ).all()

    # Search users
    users = User.query.filter(
        User.role == 'trekker',
        (User.name.ilike(search_term)) | (User.email.ilike(search_term))
    ).all()

    return jsonify({
        'treks': [{'id': t.id, 'name': t.name, 'location': t.location, 'status': t.status} for t in treks],
        'staff': [{'id': u.id, 'name': u.name, 'email': u.email, 'is_blacklisted': u.is_blacklisted} for u in staff],
        'users': [{'id': u.id, 'name': u.name, 'email': u.email, 'is_blacklisted': u.is_blacklisted} for u in users]
    })


# ──────────────── Export (Celery Task) ────────────────

@admin.route('/api/admin/export/<export_type>', methods=['POST'])
@admin_required
def trigger_export(export_type):
    """Trigger async CSV export via Celery and return the filename."""
    if export_type not in ['treks', 'bookings']:
        return jsonify({'error': 'Export type must be treks or bookings'}), 400

    from tasks import export_csv
    task = export_csv.delay(export_type)
    result = task.get(timeout=30)  # Wait for result (file path)
    filename = os.path.basename(result)
    return jsonify({'message': f'{export_type} export complete', 'filename': filename}), 200


@admin.route('/api/admin/download/<filename>', methods=['GET'])
@admin_required
def download_export(filename):
    """Download a previously exported CSV file."""
    exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    return send_from_directory(exports_dir, filename, as_attachment=True)
