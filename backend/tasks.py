import csv
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery_config import celery_app
from app import create_app
from extensions import db
from models import User, Trek, Booking


def get_flask_context():
    """Create Flask app context for database access in Celery tasks."""
    app = create_app()
    return app, app.app_context()


def send_email(to_email, subject, html_body):
    """Send an email using SMTP. Falls back to console print if SMTP is not configured."""
    app, ctx = get_flask_context()
    with ctx:
        server_host = app.config.get('MAIL_SERVER', 'localhost')
        server_port = app.config.get('MAIL_PORT', 587)
        username = app.config.get('MAIL_USERNAME', '')
        password = app.config.get('MAIL_PASSWORD', '')
        sender = app.config.get('MAIL_DEFAULT_SENDER', 'tms@trekking.com')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(server_host, server_port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.sendmail(sender, to_email, msg.as_string())
            print(f'[EMAIL] Sent to {to_email}: {subject}')
        except Exception as e:
            # Fallback: print to console if SMTP fails
            print(f'[EMAIL FALLBACK] Could not send email ({e}). Printing instead:')
            print(f'  To: {to_email}')
            print(f'  Subject: {subject}')
            print(f'  Body: {html_body[:500]}...')


@celery_app.task(name='tasks.daily_reminder')
def daily_reminder():
    """Daily reminder — notify users with upcoming trek bookings via email."""
    app, ctx = get_flask_context()
    with ctx:
        active_bookings = Booking.query.filter_by(booking_status='booked').all()

        if not active_bookings:
            print('[REMINDER] No active bookings to remind.')
            return 'No active bookings'

        reminded = 0
        for booking in active_bookings:
            user = User.query.get(booking.user_id)
            trek = Trek.query.get(booking.trek_id)
            if user and trek:
                html = f"""
                <h2>Trek Reminder</h2>
                <p>Dear {user.name},</p>
                <p>Your trek <strong>{trek.name}</strong> at <strong>{trek.location}</strong> is coming up!</p>
                <ul>
                    <li>Difficulty: {trek.difficulty}</li>
                    <li>Duration: {trek.duration} days</li>
                    <li>Start Date: {trek.start_date or 'TBD'}</li>
                    <li>End Date: {trek.end_date or 'TBD'}</li>
                </ul>
                <p>Please ensure you are prepared. Happy trekking!</p>
                """
                send_email(user.email, f'Reminder: Upcoming Trek - {trek.name}', html)
                reminded += 1

        result = f'Sent reminders for {reminded} bookings'
        print(f'[REMINDER] {result}')
        return result


@celery_app.task(name='tasks.monthly_report')
def monthly_report():
    """Monthly report — generate HTML report and email to admin."""
    app, ctx = get_flask_context()
    with ctx:
        total_treks = Trek.query.count()
        completed_treks = Trek.query.filter_by(status='completed').count()
        total_users = User.query.filter_by(role='trekker').count()
        total_bookings = Booking.query.count()
        active_bookings = Booking.query.filter_by(booking_status='booked').count()
        cancelled_bookings = Booking.query.filter_by(booking_status='cancelled').count()

        # Find popular treks (most bookings)
        popular_treks = db.session.query(
            Trek.name, db.func.count(Booking.id).label('count')
        ).join(Booking, Trek.id == Booking.trek_id
        ).group_by(Trek.id
        ).order_by(db.func.count(Booking.id).desc()
        ).limit(5).all()

        popular_rows = ''
        for name, count in popular_treks:
            popular_rows += f'<tr><td>{name}</td><td>{count}</td></tr>'
        if not popular_rows:
            popular_rows = '<tr><td colspan="2">No bookings yet</td></tr>'

        report_month = datetime.now().strftime('%B %Y')

        html_report = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>Monthly Trekking Activity Report</h1>
            <h3>{report_month}</h3>
            <hr>
            <h3>Summary</h3>
            <table border="1" cellpadding="8" cellspacing="0">
                <tr><td><strong>Total Treks</strong></td><td>{total_treks}</td></tr>
                <tr><td><strong>Treks Completed</strong></td><td>{completed_treks}</td></tr>
                <tr><td><strong>Total Registered Users</strong></td><td>{total_users}</td></tr>
                <tr><td><strong>Total Bookings</strong></td><td>{total_bookings}</td></tr>
                <tr><td><strong>Active Bookings</strong></td><td>{active_bookings}</td></tr>
                <tr><td><strong>Cancelled Bookings</strong></td><td>{cancelled_bookings}</td></tr>
            </table>
            <h3>Popular Treks</h3>
            <table border="1" cellpadding="8" cellspacing="0">
                <tr><th>Trek Name</th><th>Total Bookings</th></tr>
                {popular_rows}
            </table>
            <hr>
            <p><em>This is an automated report from TMS V2.</em></p>
        </body>
        </html>
        """

        # Send to admin
        admin = User.query.filter_by(role='admin').first()
        admin_email = app.config.get('ADMIN_EMAIL', admin.email if admin else 'admin@trekking.com')
        send_email(admin_email, f'TMS Monthly Report - {report_month}', html_report)

        print(f'[REPORT] Monthly report generated for {report_month}')
        return f'Monthly report sent for {report_month}'


@celery_app.task(name='tasks.export_user_bookings')
def export_user_bookings(user_id):
    """Export a specific user's booking history as CSV."""
    app, ctx = get_flask_context()
    with ctx:
        exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(exports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bookings_user{user_id}_{timestamp}.csv'
        filepath = os.path.join(exports_dir, filename)

        bookings = Booking.query.filter_by(user_id=user_id).all()

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['User ID', 'Trek Name', 'Location', 'Booking Status', 'Booking Date', 'Trek Start Date', 'Trek End Date'])
            for b in bookings:
                trek = Trek.query.get(b.trek_id)
                writer.writerow([
                    b.user_id,
                    trek.name if trek else 'Unknown',
                    trek.location if trek else '',
                    b.booking_status,
                    str(b.booking_date),
                    str(trek.start_date) if trek and trek.start_date else '',
                    str(trek.end_date) if trek and trek.end_date else ''
                ])

        print(f'[EXPORT] User {user_id} booking CSV saved: {filepath}')
        return filepath


@celery_app.task(name='tasks.export_csv')
def export_csv(export_type):
    """Export treks or bookings data to CSV file (admin use)."""
    app, ctx = get_flask_context()
    with ctx:
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
