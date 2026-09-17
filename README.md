# JobTrackr API

An AI-powered job application tracker REST API built with Flask, PostgreSQL, JWT auth.

**Live demo:** https://jobtrackr-kvfp.onrender.com
**Swagger docs:** https://jobtrackr-kvfp.onrender.com/docs
---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 3.0 |
| Database | PostgreSQL (prod) / SQLite (local) |
| ORM | Flask-SQLAlchemy |
| Auth | JWT (Flask-JWT-Extended) |
| Password hashing | Flask-Bcrypt |
| AI | Anthropic Claude API |
| API Docs | Flasgger (Swagger UI) |
| Containerization | Docker |
| Deployment | Render (free tier) |

---

## Local Setup (5 minutes)

```bash
# 1. Clone and enter
git clone https://github.com/yourusername/jobtrackr.git
cd jobtrackr

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY

# 5. Run
python run.py
```

API is now running at `http://localhost:5000`  
Swagger docs at `http://localhost:5000/docs`

---

## Docker Setup

```bash
# Run with Docker Compose (includes PostgreSQL)
docker-compose up --build
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth? |
|--------|----------|-------------|-------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login, get JWT token | No |
| GET | `/api/auth/me` | Get current user | Yes |

### Jobs (all require JWT token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs` | Add a job application |
| GET | `/api/jobs` | Get all your jobs (filter by `?status=` or `?company=`) |
| GET | `/api/jobs/<id>` | Get a single job |
| PUT | `/api/jobs/<id>` | Update a job |
| DELETE | `/api/jobs/<id>` | Delete a job |
| GET | `/api/jobs/stats` | Your application stats |
| POST | `/api/jobs/<id>/analyze` | AI analysis of job fit |

---

## Example Usage

### 1. Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Rahul Sharma", "email": "rahul@email.com", "password": "secret123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "rahul@email.com", "password": "secret123"}'
# Save the token from response
```

### 3. Add a job
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "role": "Backend Engineer Intern",
    "status": "applied",
    "job_description": "We need a Python developer with Flask and API experience...",
    "location": "Bangalore",
    "applied_date": "2026-05-16"
  }'
```

### 4. Get AI analysis
```bash
curl -X POST http://localhost:5000/api/jobs/1/analyze \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"resume_summary": "2 years Python, built 3 Flask REST APIs, knows PostgreSQL and Docker"}'
```

---

## Deploy to Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variables (from your `.env`)
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn run:app`
7. Done — live URL in 2 minutes

---

## Job Status Flow

```
applied → interview → offer
       ↘ rejected
       ↘ withdrawn
```

---

