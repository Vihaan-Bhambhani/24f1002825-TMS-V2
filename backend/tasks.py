import csv
import os
from datetime import datetime
from celery_config import celery_app
from app import create_app
from extensions import db
from models import User, Trek, Booking


def get_flask_context():
    """Create Flask app context for database access in Celery tasks."""
    app = create_app()
    return app.app_context()


@celery_app.task(name='tasks.daily_reminder')
def daily_reminder():
    """Daily reminder — check for upcoming treks and notify users with bookings."""
    with get_flask_context():
        # Find all active bookings for open treks
        active_bookings = Booking.query.filter_by(booking_status='booked').all()

        if not active_bookings:
            print('[REMINDER] No active bookings to remind.')
            return 'No active bookings'

        for booking in active_bookings:
            user = User.query.get(booking.user_id)
            trek = Trek.query.get(booking.trek_id)
            if user and trek:
                # In a real app, this would send an email
                print(f'[REMINDER] Dear {user.name}, your trek "{trek.name}" is coming up!')

        result = f'Sent reminders for {len(active_bookings)} bookings'
        print(f'[REMINDER] {result}')
        return result


@celery_app.task(name='tasks.monthly_report')
def monthly_report():
    """Monthly report — generate summary stats."""
    with get_flask_context():
        total_treks = Trek.query.count()
        total_users = User.query.filter_by(role='trekker').count()
        total_bookings = Booking.query.count()
        active_bookings = Booking.query.filter_by(booking_status='booked').count()
        cancelled_bookings = Booking.query.filter_by(booking_status='cancelled').count()

        report = (
            f'\n{"="*40}\n'
            f'  MONTHLY REPORT - {datetime.now().strftime("%B %Y")}\n'
            f'{"="*40}\n'
            f'  Total Treks:       {total_treks}\n'
            f'  Total Users:       {total_users}\n'
            f'  Total Bookings:    {total_bookings}\n'
            f'  Active Bookings:   {active_bookings}\n'
            f'  Cancelled:         {cancelled_bookings}\n'
            f'{"="*40}\n'
        )
        print(report)
        return report


@celery_app.task(name='tasks.export_csv')
def export_csv(export_type):
    """Export treks or bookings data to CSV file."""
    with get_flask_context():
        exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(exports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{export_type}_{timestamp}.csv'
        filepath = os.path.join(exports_dir, filename)

        if export_type == 'treks':
            treks = Trek.query.all()
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Location', 'Difficulty', 'Duration', 'Slots', 'Status', 'Start Date', 'End Date'])
                for t in treks:
                    writer.writerow([t.id, t.name, t.location, t.difficulty, t.duration, t.available_slots, t.status, t.start_date, t.end_date])

        elif export_type == 'bookings':
            bookings = Booking.query.all()
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'User ID', 'Trek ID', 'Booking Date', 'Status'])
                for b in bookings:
                    writer.writerow([b.id, b.user_id, b.trek_id, b.booking_date, b.booking_status])

        print(f'[EXPORT] CSV saved: {filepath}')
        return filepath
