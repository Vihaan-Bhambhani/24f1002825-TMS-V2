from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User, Trek, Booking
from utils.auth_helpers import staff_required

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
