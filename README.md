# Trekking Management Application V2

A role-based Trekking Management Application built with Flask and Vue.js for the IIT Madras MAD-2 course.

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, SQLite, Flask-JWT-Extended, Flask-CORS
- **Frontend**: Vue.js 3, Vite, Vue Router, Axios, Bootstrap 5
- **Auth**: JWT (JSON Web Tokens)

## Project Structure

```
backend/    — Flask REST API (port 5001)
frontend/   — Vue.js SPA (port 5173)
```

## Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Default Admin Credentials

- **Email**: admin@trekking.com
- **Password**: admin123

## Milestones

- [x] Milestone 0: Repository and project setup
- [x] Milestone 1: Database models and schema
- [x] Milestone 2: Authentication and RBAC
- [x] Milestone 3: Admin dashboard and management
- [x] Milestone 4: Trek staff dashboard and operations
- [x] Milestone 5: User dashboard and trek booking
- [ ] Milestone 6: Booking history and status tracking
- [ ] Milestone 7: Backend jobs (Celery + Redis)
- [ ] Milestone 8: API caching (Redis)
