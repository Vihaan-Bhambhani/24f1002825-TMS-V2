from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models import User, Trek, Booking
from utils.auth_helpers import login_required
from utils.cache import cache_get, cache_set, cache_delete

user = Blueprint('user', __name__)


@user.route('/api/treks', methods=['GET'])
@login_required
def browse_treks():
    """List all open treks available for booking (cached)."""
    cached = cache_get('open:treks')
    if cached:
        return jsonify(cached)

    treks = Trek.query.filter_by(status='open').all()
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
    cache_set('open:treks', result, ttl=60)
    return jsonify(result)


@user.route('/api/bookings', methods=['GET'])
@login_required
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
            'booking_date': str(b.booking_date),
            'booking_status': b.booking_status
        })
    return jsonify(result)


@user.route('/api/bookings', methods=['POST'])
@login_required
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
@login_required
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
