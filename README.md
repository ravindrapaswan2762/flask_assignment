# Flask User Management API

A REST API built with **Flask** and **MySQL** for managing users.  
This project was created as part of a Software Engineer assignment.

---

## AI Usage Declaration

| Item | Detail |
|------|--------|
| **Tools used** | Google Antigravity IDE (Gemini-based coding assistant) |
| **AI-generated parts** | Initial boilerplate for routes, model, service, config, Dockerfile |
| **Manual modifications** | Validation logic tuning, error message wording, pagination clamping, JWT decorator design, README writing, SQL index decisions |

---

## Project Structure

```
flask_assignment/
├── app.py                  # Application factory
├── run.py                  # Entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose (API + MySQL)
│
├── config/
│   ├── __init__.py
│   ├── settings.py         # Config classes (dev / prod / test)
│   └── database.py         # Connection pool + DB initializer
│
├── models/
│   ├── __init__.py
│   └── user_model.py       # Data-access layer (raw SQL via mysql-connector)
│
├── services/
│   ├── __init__.py
│   └── user_service.py     # Business logic + validation
│
└── routes/
    ├── __init__.py
    ├── user_routes.py      # /users endpoints (Blueprint)
    └── auth_routes.py      # /auth endpoints - JWT login (Bonus)
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- MySQL 8.0+
- Git

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd flask_assignment
git checkout assignment
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in your MySQL credentials:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=users
JWT_SECRET_KEY=your-jwt-secret
```

### 5. Start MySQL and run the app
The app automatically creates the `users` database and `users` table on first run.
```bash
python run.py
```
The API will be available at `http://localhost:5000`

### 6. (Optional) Run with Docker
```bash
docker-compose up --build
```

---

## API Endpoints

### Health Check
```
GET /health
```
```json
{ "success": true, "message": "API is running." }
```

---

### Users

#### GET /users — Retrieve all users (paginated)
```
GET http://localhost:5000/users
GET http://localhost:5000/users?page=1&limit=10
GET http://localhost:5000/users?search=john
```
**Response:**
```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin", "created_at": "2026-09-25T10:00:00", "updated_at": "2026-09-25T10:00:00" }
  ],
  "pagination": { "total": 1, "page": 1, "limit": 10, "pages": 1 },
  "message": "Retrieved 1 user(s)."
}
```

---

#### POST /users — Create a new user
```
POST http://localhost:5000/users
Content-Type: application/json
```
**Request body:**
```json
{ "name": "John Doe", "email": "john@example.com", "role": "admin" }
```
**Success response (201):**
```json
{
  "success": true,
  "data": { "id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin", "created_at": "...", "updated_at": "..." },
  "message": "User created successfully."
}
```
**Validation error (422):**
```json
{ "success": false, "error": "Validation failed.", "errors": ["'email' is not a valid email address."] }
```
**Duplicate email (409):**
```json
{ "success": false, "error": "Email 'john@example.com' is already registered." }
```

---

#### GET /users/<id> — Retrieve user by ID
```
GET http://localhost:5000/users/1
```
**Success (200):**
```json
{ "success": true, "data": { "id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin", ... }, "message": "User retrieved successfully." }
```
**Not found (404):**
```json
{ "success": false, "error": "User with ID 99 not found." }
```

---

### Auth (Bonus - JWT)

#### POST /auth/login — Get a JWT token
```
POST http://localhost:5000/auth/login
Content-Type: application/json

{ "email": "john@example.com" }
```
**Response:**
```json
{ "success": true, "token": "<jwt-token>", "user": { ... } }
```

#### GET /auth/me — Get current user (requires token)
```
GET http://localhost:5000/auth/me
Authorization: Bearer <jwt-token>
```

---

## Database Schema

**Database:** `users`

**Table:** `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `name` | VARCHAR(255) | NOT NULL |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE |
| `role` | VARCHAR(100) | NOT NULL |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

**SQL:**
```sql
CREATE DATABASE IF NOT EXISTS `users`;

CREATE TABLE IF NOT EXISTS `users` (
    `id`         INT          NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(255) NOT NULL,
    `email`      VARCHAR(255) NOT NULL UNIQUE,
    `role`       VARCHAR(100) NOT NULL,
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_email` (`email`),
    INDEX `idx_name`  (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Assumptions Made

1. **No password field** – The assignment schema only specifies `id`, `name`, `email`, `role`. The JWT login uses email-only lookup (demo mode).
2. **Role is a free-text field** – No enum constraint was applied so any role string is accepted (e.g., `admin`, `user`, `moderator`).
3. **Pagination max limit** – Clamped to 100 records per page to prevent DB overload.
4. **Search is case-insensitive** – Implemented via SQL `LIKE %term%` on `name` and `email`.
5. **Auto DB creation** – The app creates the database and table on startup if they don't exist, simplifying setup.
6. **`mysql-connector-python`** was chosen over `PyMySQL` for its official support from Oracle and built-in connection pooling.

---

## Task 7 – Short Answers

### 1. Why did you choose Flask?
Flask was chosen for its **simplicity, flexibility, and minimal footprint**. Unlike Django (which is "batteries included"), Flask lets you choose exactly which components to use. For an API-first project with a single resource, Flask's Blueprint system, lightweight routing, and explicit config management are ideal. It is also easier to understand end-to-end in an interview/assignment context.

### 2. How would you scale this system?
- **Horizontal scaling**: Run multiple Flask instances behind a **load balancer** (Nginx / AWS ALB).
- **Connection pooling**: Already implemented; increase `pool_size` and use **PgBouncer / ProxySQL** in front of MySQL.
- **Caching**: Add **Redis** for caching frequent `GET /users` responses.
- **Read replicas**: Route `SELECT` queries to MySQL read replicas.
- **Async workers**: Use **Gunicorn + Uvicorn** (ASGI) or **Celery** for background tasks.
- **API Gateway**: Add rate-limiting, auth, and routing at the gateway layer (Kong / AWS API Gateway).
- **Database sharding / partitioning**: For massive user tables, shard by `id` range.

### 3. What changes would you make for production?
- **Passwords**: Add `password_hash` column; use `bcrypt` or `argon2`.
- **HTTPS only**: Enforce TLS via reverse proxy (Nginx / Caddy).
- **Environment secrets**: Use **AWS Secrets Manager**, **HashiCorp Vault**, or Kubernetes Secrets instead of `.env`.
- **Structured logging**: Replace `print()` with `logging` + **JSON formatter** → ship to ELK / CloudWatch.
- **Health & metrics**: Add `/metrics` (Prometheus) and deep health checks (DB connectivity).
- **Rate limiting**: Use `Flask-Limiter` to prevent abuse.
- **Input sanitisation**: Add stricter validation, length limits, and HTML-escape on output.
- **Database migrations**: Use **Alembic** instead of raw `CREATE TABLE IF NOT EXISTS`.
- **CI/CD pipeline**: GitHub Actions → run tests → build Docker image → push to registry → deploy.
- **Error monitoring**: Integrate **Sentry** for real-time exception tracking.

---

## Git Workflow

```bash
git init
git checkout -b assignment
git add .
git commit -m "feat: initial Flask User Management API"
git remote add origin <your-github-url>
git push -u origin assignment
# Then open a Pull Request from assignment → main
```
