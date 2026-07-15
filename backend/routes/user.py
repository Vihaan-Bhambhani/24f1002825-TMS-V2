import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User, Trek, Booking
from utils.auth_helpers import trekker_required
from utils.cache import cache_get, cache_set, cache_delete

user = Blueprint('user', __name__)


@user.route('/api/treks', methods=['GET'])
@trekker_required
def browse_treks():
    """List open treks with optional search/filter (cached when no filters)."""
    # Get filter/search parameters
    search = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip().lower()
    location = request.args.get('location', '').strip()
    duration = request.args.get('duration', '').strip()

    has_filters = any([search, difficulty, location, duration])

    # Use cache only when there are no filters
    if not has_filters:
        cached = cache_get('open:treks')
        if cached:
            return jsonify(cached)

    # Build query
    query = Trek.query.filter_by(status='open')

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Trek.name.ilike(search_term)) | (Trek.location.ilike(search_term))
        )
    if difficulty and difficulty in ['easy', 'moderate', 'hard']:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    if duration:
        try:
            query = query.filter(Trek.duration <= int(duration))
        except ValueError:
            pass

    treks = query.all()
    result = []
    for t in treks:
        result.append({
            'id': t.id,
            'name': t.name,
            'location': t.location,
            'difficulty': t.difficulty,
            'duration': t.duration,
            'available_slots': t.available_slots,
            'description': t.description,
            'start_date': str(t.start_date) if t.start_date else None,
            'end_date': str(t.end_date) if t.end_date else None
        })

    if not has_filters:
        cache_set('open:treks', result, ttl=60)

    return jsonify(result)


@user.route('/api/bookings', methods=['GET'])
@trekker_required
def get_my_bookings():
    """List all bookings for the logged-in trekker."""
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).all()
    result = []
    for b in bookings:
        trek = Trek.query.get(b.trek_id)
        result.append({
            'id': b.id,
            'trek_name': trek.name if trek else 'Unknown',
            'trek_location': trek.location if trek else '',
            'trek_difficulty': trek.difficulty if trek else '',
            'trek_duration': trek.duration if trek else 0,
            'trek_start_date': str(trek.start_date) if trek and trek.start_date else None,
            'trek_end_date': str(trek.end_date) if trek and trek.end_date else None,
            'trek_status': trek.status if trek else '',
            'booking_date': str(b.booking_date),
            'booking_status': b.booking_status
        })
    return jsonify(result)


@user.route('/api/bookings', methods=['POST'])
@trekker_required
def book_trek():
    """Book a trek. Reduces available slots by 1."""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    trek_id = data.get('trek_id')

    if not trek_id:
        return jsonify({'error': 'trek_id is required'}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.status != 'open':
        return jsonify({'error': 'This trek is not open for booking'}), 400

    if trek.available_slots <= 0:
        return jsonify({'error': 'No available slots'}), 400

    # Check if user already booked this trek
    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id, booking_status='booked').first()
    if existing:
        return jsonify({'error': 'You have already booked this trek'}), 409

    # Create booking and reduce slots
    booking = Booking(user_id=user_id, trek_id=trek_id, booking_status='booked')
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    cache_delete('open:*')   # Invalidate treks cache (slots changed)
    cache_delete('admin:*')  # Invalidate admin stats

    return jsonify({'message': 'Trek booked successfully', 'booking_id': booking.id}), 201


@user.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
@trekker_required
def cancel_booking(booking_id):
    """Cancel a booking. Restores the slot."""
    user_id = int(get_jwt_identity())
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.booking_status != 'booked':
        return jsonify({'error': 'Only active bookings can be cancelled'}), 400

    booking.booking_status = 'cancelled'

    # Restore the slot
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    db.session.commit()
    cache_delete('open:*')
    cache_delete('admin:*')
    return jsonify({'message': 'Booking cancelled'})


# ──────────────── Profile ────────────────

@user.route('/api/profile', methods=['GET'])
@trekker_required
def get_profile():
    """Get the logged-in user's profile."""
    user_id = int(get_jwt_identity())
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role,
        'created_at': str(u.created_at)
    })


@user.route('/api/profile', methods=['PUT'])
@trekker_required
def update_profile():
    """Update the logged-in user's name or password."""
    user_id = int(get_jwt_identity())
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()

    if name:
        u.name = name
    if password:
        if len(password) < 4:
            return jsonify({'error': 'Password must be at least 4 characters'}), 400
        u.password_hash = generate_password_hash(password)

    db.session.commit()

    # Update localStorage user info via response
    return jsonify({
        'message': 'Profile updated',
        'user': {'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role}
    })


# ──────────────── User Export (Celery) ────────────────

@user.route('/api/export/bookings', methods=['POST'])
@trekker_required
def trigger_user_export():
    """Trigger async CSV export of the user's booking history. Returns task ID immediately."""
    user_id = int(get_jwt_identity())

    from tasks import export_user_bookings
    task = export_user_bookings.delay(user_id)

    return jsonify({'message': 'Export started', 'task_id': task.id}), 202


@user.route('/api/export/status/<task_id>', methods=['GET'])
@trekker_required
def check_export_status(task_id):
    """Poll the status of an export task."""
    from celery_config import celery_app
    result = celery_app.AsyncResult(task_id)

    if result.state == 'PENDING':
        return jsonify({'status': 'pending'})
    elif result.state == 'SUCCESS':
        filename = os.path.basename(result.result)
        return jsonify({'status': 'done', 'filename': filename})
    elif result.state == 'FAILURE':
        return jsonify({'status': 'failed', 'error': str(result.result)}), 500
    else:
        return jsonify({'status': result.state.lower()})


@user.route('/api/download/<filename>', methods=['GET'])
@trekker_required
def download_user_export(filename):
    """Download a previously exported CSV file."""
    exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    return send_from_directory(exports_dir, filename, as_attachment=True)

