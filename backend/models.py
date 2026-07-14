from datetime import datetime
from extensions import db


class User(db.Model):
    """All users — admin, staff, and trekkers — in one table.
    The 'role' column distinguishes them."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'trekker'
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    assigned_treks = db.relationship('Trek', backref='staff', lazy=True)

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


class StaffProfile(db.Model):
    """Extra info for staff members. Created by admin along with the user."""
    __tablename__ = 'staff_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(15), default='')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StaffProfile user_id={self.user_id}>'


class Trek(db.Model):
    """A trekking event. Can be assigned to one staff member."""
    __tablename__ = 'trek'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # 'easy', 'moderate', 'hard'
    duration = db.Column(db.Integer, nullable=False)  # days
    available_slots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'open', 'closed', 'completed'
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    assigned_staff = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True)

    def __repr__(self):
        return f'<Trek {self.name} ({self.status})>'


class Booking(db.Model):
    """Links a trekker to a trek they booked."""
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_status = db.Column(db.String(20), default='booked')  # 'booked', 'cancelled', 'completed'

    def __repr__(self):
        return f'<Booking user={self.user_id} trek={self.trek_id} ({self.booking_status})>'
