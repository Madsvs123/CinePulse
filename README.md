# CinePulse

Movie discovery and recommendation platform for viewers and entertainment teams. It combines a movie catalog, personalized recommendations, reviews and lists, taste profiles, admin analytics, and live notifications.

## Stack

Django 5 and Django REST Framework, PostgreSQL full-text search, Celery, and Django Channels. React 18, TypeScript, and Vite on the frontend.

## Layout

- `backend/` — Django API
- `frontend/` — React client

## Local setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Use PostgreSQL and Redis when the project expects them. Copy `.env.example` to `.env` where an example file is present, and keep real secrets out of git.

## License

Released under the [MIT License](LICENSE).
