# Trekking Management Application V2

A role-based Trekking Management Application built with Flask and Vue.js for the IIT Madras MAD-2 course.

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: Vue.js, Vite
- **Auth**: JWT (upcoming)

## Project Structure

```
backend/    — Flask REST API
frontend/   — Vue.js SPA
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

## Milestones

- [x] Milestone 0: Repository and project setup
- [ ] Milestone 1: Database models and schema
- [ ] Milestone 2: Authentication and RBAC
- [ ] Milestone 3: Admin dashboard and management
- [ ] Milestone 4: Trek staff dashboard and operations
- [ ] Milestone 5: User dashboard and trek booking
- [ ] Milestone 6: Booking history and status tracking
- [ ] Milestone 7: Backend jobs (Celery + Redis)
- [ ] Milestone 8: API caching (Redis)
