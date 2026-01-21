# Savoria TODO Backend

Savoria TODO Backend

Savoria TODO Backend is a modern backend for a TODO application built with FastAPI and SQLAlchemy. It provides a fast, secure, and scalable API for managing tasks, users, and authentication.

The backend supports:

- CRUD operations for tasks
- User authentication via JWT tokens
- OAuth 2.0 login with Google
- Redis caching 
- PostgreSQL as the main database

## SETUP

```bash
1. Clone the repository:
git clone https://github.com/GilevIlya/Savoria_todo-Backend.git

2. Create a .env file in the project root and add your environment variables
POSTGRES_DB=<your_database_name>
POSTGRES_USER=<your_database_user>
POSTGRES_PASSWORD=<your_database_password>

REDIS_HOST=<your_redis_host>
REDIS_PORT=<your_redis_port>
REDIS_PASSWORD=<your_redis_password>

JWT_SECRET_KEY=<your_jwt_secret_key>

CLIENT_ID=<your_google_client_id>
CLIENT_SECRET=<your_google_client_secret>
GOOGLE_TOKEN_URL=<your_google_token_url>
GOOGLE_AUTH_FORM_BASE_URL=<your_google_auth_base_url>
REDIRECT_URI=<your_redirect_uri>


3. Start with docker-compose:
docker-compose up --build

