from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User, Trek, Booking, StaffProfile
from utils.auth_helpers import staff_required
from utils.cache import cache_delete

staff = Blueprint('staff', __name__)


@staff.route('/api/staff/dashboard', methods=['GET'])
@staff_required
def staff_dashboard():
    """Staff dashboard stats."""
    user_id = int(get_jwt_identity())
    assigned_treks = Trek.query.filter_by(assigned_staff=user_id).count()
    trek_ids = [t.id for t in Trek.query.filter_by(assigned_staff=user_id).all()]
    total_bookings = Booking.query.filter(Booking.trek_id.in_(trek_ids)).count() if trek_ids else 0

    return jsonify({
        'assigned_treks': assigned_treks,
        'total_bookings': total_bookings
    })


@staff.route('/api/staff/treks', methods=['GET'])
@staff_required
def get_assigned_treks():
    """List treks assigned to this staff member."""
    user_id = int(get_jwt_identity())
    treks = Trek.query.filter_by(assigned_staff=user_id).all()

    result = []
    for t in treks:
        booking_count = Booking.query.filter_by(trek_id=t.id).count()
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
            'booking_count': booking_count
        })
    return jsonify(result)


@staff.route('/api/staff/treks/<int:trek_id>/status', methods=['PUT'])
@staff_required
def update_trek_status(trek_id):
    """Update the status of an assigned trek."""
    user_id = int(get_jwt_identity())
    trek = Trek.query.filter_by(id=trek_id, assigned_staff=user_id).first()

    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 404

    data = request.get_json()
    new_status = data.get('status')

    valid_statuses = ['pending', 'approved', 'open', 'closed', 'completed']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

    trek.status = new_status
    db.session.commit()
    cache_delete('open:*')
    cache_delete('admin:*')
    return jsonify({'message': f'Trek status updated to {new_status}'})


@staff.route('/api/staff/treks/<int:trek_id>/bookings', methods=['GET'])
@staff_required
def get_trek_bookings(trek_id):
    """View bookings for a specific assigned trek."""
    user_id = int(get_jwt_identity())
    trek = Trek.query.filter_by(id=trek_id, assigned_staff=user_id).first()

    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 404

    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    result = []
    for b in bookings:
        user = User.query.get(b.user_id)
        result.append({
            'id': b.id,
            'user_name': user.name if user else 'Unknown',
            'user_email': user.email if user else '',
            'booking_date': str(b.booking_date),
            'booking_status': b.booking_status
        })
    return jsonify(result)


@staff.route('/api/staff/treks/<int:trek_id>/slots', methods=['PUT'])
@staff_required
def update_trek_slots(trek_id):
    """Update available slots for an assigned trek."""
    user_id = int(get_jwt_identity())
    trek = Trek.query.filter_by(id=trek_id, assigned_staff=user_id).first()

    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 404

    data = request.get_json()
    new_slots = data.get('available_slots')

    if new_slots is None:
        return jsonify({'error': 'available_slots is required'}), 400

    try:
        new_slots = int(new_slots)
    except (ValueError, TypeError):
        return jsonify({'error': 'available_slots must be a number'}), 400

    if new_slots < 0:
        return jsonify({'error': 'available_slots cannot be negative'}), 400

    trek.available_slots = new_slots
    db.session.commit()
    cache_delete('open:*')
    cache_delete('admin:*')
    return jsonify({'message': f'Slots updated to {new_slots}'})


@staff.route('/api/staff/treks/<int:trek_id>/bookings/<int:booking_id>/cancel', methods=['PUT'])
@staff_required
def cancel_participant_booking(trek_id, booking_id):
    """Staff can remove/cancel a participant's booking from their assigned trek."""
    user_id = int(get_jwt_identity())
    trek = Trek.query.filter_by(id=trek_id, assigned_staff=user_id).first()

    if not trek:
        return jsonify({'error': 'Trek not found or not assigned to you'}), 404

    booking = Booking.query.filter_by(id=booking_id, trek_id=trek_id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.booking_status != 'booked':
        return jsonify({'error': 'Booking is already cancelled'}), 400

    booking.booking_status = 'cancelled'
    trek.available_slots += 1
    db.session.commit()
    cache_delete('open:*')
    cache_delete('admin:*')
    return jsonify({'message': 'Participant booking cancelled'})


# ──────────────── Staff Profile ────────────────

@staff.route('/api/staff/profile', methods=['GET'])
@staff_required
def get_staff_profile():
    """Get the logged-in staff member's profile."""
    user_id = int(get_jwt_identity())
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'User not found'}), 404
    sp = StaffProfile.query.filter_by(user_id=user_id).first()
    return jsonify({
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'phone': sp.phone if sp else '',
        'role': u.role,
        'created_at': str(u.created_at)
    })


@staff.route('/api/staff/profile', methods=['PUT'])
@staff_required
def update_staff_profile():
    """Update the logged-in staff member's name, phone, or password."""
    user_id = int(get_jwt_identity())
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    if name:
        u.name = name
    if phone is not None:
        sp = StaffProfile.query.filter_by(user_id=user_id).first()
        if not sp:
            sp = StaffProfile(user_id=user_id)
            db.session.add(sp)
        sp.phone = phone
    if password:
        if len(password) < 4:
            return jsonify({'error': 'Password must be at least 4 characters'}), 400
        u.password_hash = generate_password_hash(password)

    db.session.commit()
    return jsonify({
        'message': 'Profile updated',
        'user': {'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role}
    })

