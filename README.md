## API Server

FastAPI-based backend providing JWT authentication, topics management, dashboard statistics from OpenSearch, and database migrations with Alembic. Configuration is loaded from environment variables or AWS Secrets Manager.

### Highlights
- **FastAPI** app configured in `app.py` with global CORS (allow all)
- **SQLAlchemy** ORM and session management in `src/database/config.py`
- **Alembic** migrations auto-run on startup (`app.py -> run_migrations()`)
- **JWT auth** using `INTELLIGENCE_API_SECRET` as secret (HS256)
- **OpenSearch** integration for analytics in `src/services/search_service.py`

## Architecture Overview

- **Entry point**: `app.py`
  - Loads config via `config.get_config()` (env or AWS Secrets Manager)
  - Runs Alembic migrations on startup
  - Uvicorn runner in `__main__` (defaults to port 8000) and helper script `start_app.sh` (port 8100)

- **Configuration**: `config.py`
  - Loads from `.env` by default
  - If `FLASK_ENV != "local"`, attempts to fetch secrets from AWS Secrets Manager
  - Keys: `OPENAI_API_KEY`, `INTELLIGENCE_API_SECRET` (also used as `JWT_SECRET_KEY`), `DATABASE_URL`, `OPENSEARCH_*`, `TWILIO_*`

- **Database**: `src/database/config.py`
  - Engine + `SessionLocal` + `Base`
  - `get_db()` dependency for request-scoped sessions

- **Models**: `src/models/`
  - `User`: id, email, full_name, hashed_password (nullable), is_active, timestamps
  - `Feedback`: sender_id, product_name, feedback_text, media_urls (JSON), timestamps
  - `Topic`: label (unique, 500 chars), description, is_active, timestamps
  - `Job` + `JobStatus`: job_name, last_processed_id, status, timestamps
  - `JobConfig`: config (JSON)

- **Migrations**: `alembic/`
  - `f3db2bb4e6d7` users
  - `qwdb2bb4ex2p` feedbacks (depends on users)
  - `841457b3948c` job_configs
  - `7a56dde5902f` topics
  - `79b07bc6d325` jobs

- **Auth**: `src/auth/jwt_handler.py`
  - OAuth2 bearer via `OAuth2PasswordBearer(tokenUrl="/auth/login")`
  - `create_access_token(data)` with 24h expiry
  - `get_current_user` and `get_current_active_user` dependencies

- **Services**:
  - `src/services/search_service.py`: Singleton OpenSearch client, queries for dashboard stats, messages, and wordcount analysis (indices: `feedback-analysis`, `wordcount-analysis`)

- **Routes**: `src/routes/`
  - `health.py` (public): `GET /health/` → `{ status: "healthy" }`
  - `auth.py`:
    - `POST /auth/login` → email-only login, returns JWT and profile
    - `GET /auth/me` → current user profile
  - `topic.py` (protected):
    - `GET /topic/all` → list active topics
    - `POST /topic/create` → create topic (unique label, case-insensitive)
    - `DELETE /topic/{topic_id}` → soft-delete (set `is_active=false`)
  - `dashboard.py` (protected):
    - `GET /dashboard/statistics` → counts + sentiment + top topics from OpenSearch
    - `GET /dashboard/wordcount-analysis` → aggregated top words
    - `GET /dashboard/messages` → paginated documents from OpenSearch

### Architecture

```mermaid
flowchart LR
  Client["Client (Dashboard/Admin UI)"] --> FastAPI["FastAPI App (app.py)"]

  subgraph Auth
    FastAPI --> JWT["JWT (OAuth2 Bearer)"]
    Client --> FastAPI
  end

  FastAPI --> Postgres[(PostgreSQL)]
  FastAPI --> OpenSearch[(OpenSearch)]

  Alembic["Alembic Migrations"] --> Postgres
  Secrets["AWS Secrets Manager"] -.-> FastAPI
```

## Environment Variables

Place in `.env` for local development (examples):

```
DATABASE_URL=postgresql://username:password@localhost:5432/theunc
INTELLIGENCE_API_SECRET=replace-with-strong-secret

# OpenSearch
OPENSEARCH_ENDPOINT=https://your-opensearch-domain
OPENSEARCH_USER=your-username
OPENSEARCH_PASS=your-password

# Optional Twilio (if used elsewhere)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890
```

Notes:
- The app treats `INTELLIGENCE_API_SECRET` as the JWT secret.
- If `FLASK_ENV` is not `local`, the app will attempt to load the same keys from AWS Secrets Manager using the exact secret names shown above.

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (see above). Ensure your database is reachable by `DATABASE_URL`.

3. Start the API:
   ```bash
   # Option A: run directly (port 8000)
   uvicorn app:app --reload

   # Option B: helper script (port 8100)
   ./start_app.sh
   ```

The app runs migrations automatically at startup. You can also manage migrations manually:

```bash
alembic upgrade head
alembic revision --autogenerate -m "Description of changes"
```

API docs will be available at `/docs` and `/redoc` once running.

## API Quick Reference

- **Health**
  - `GET /health/`

- **Auth**
  - `POST /auth/login` (body: `{ "email": "user@example.com", "password": null }`) → `{ access_token, token_type, success, profile }`
  - `GET /auth/me` (requires `Authorization: Bearer <token>`) → `{ id, email, full_name }`

- **Topics** (require auth)
  - `GET /topic/all`
  - `POST /topic/create` (body: `{ "label": "string", "description": "string|null" }`)
  - `DELETE /topic/{topic_id}`

- **Dashboard** (require auth; OpenSearch must be configured)
  - `GET /dashboard/statistics`
  - `GET /dashboard/wordcount-analysis`
  - `GET /dashboard/messages`

## OpenSearch

- Client configured in `src/services/search_service.py` using `OPENSEARCH_ENDPOINT`, `OPENSEARCH_USER`, `OPENSEARCH_PASS`.
- Indices and mappings:
  - `opensearch/feedback-analysis.mapping.json`
  - `opensearch/wordcount-analysis.mapping.json`
- A helper script `scripts/reset.sh` shows how to recreate indices via `curl` (update credentials/endpoints before use).

## Notes & Considerations

- CORS is open to all origins in `src/routes/__init__.py`.
- Password verification is not implemented; login succeeds if a `User` with the given email exists and is active.
- Migrations are idempotent on upgrade; downgrade paths drop objects where defined. Always back up data before downgrades.