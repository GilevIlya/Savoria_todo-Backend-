# Savoria Todo Backend

Backend API for Savoria Todo application built with FastAPI. Implements user registration, authentication, and task management.

## Technologies

FastAPI, Python, PostgreSQL, SQLAlchemy, Alembic, Pydantic, Uvicorn, Docker

## Getting Started

Create a `.env` file with the required environment variables, then run:

```bash
docker-compose up --build
```

## API Documentation

After starting, documentation is available at http://localhost:8000/docs

## Structure

- `src/` - application source code
- `uploads/` - uploaded files  
- `alembic/` - database migrations
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker configuration

## Current Features

User registration implemented with Pydantic data validation (first name, last name, email, username, password). Passwords are hashed before saving, duplicate checks included. Asynchronous project running on Uvicorn, built with FastAPI and SQLAlchemy for PostgreSQL interaction.

## In Development

JWT authorization, profile management, data editing, password reset, email confirmation, extended Todo functionality with categories and priorities.
