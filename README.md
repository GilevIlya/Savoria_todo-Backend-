Savoria TODO Backend — a FastAPI-based REST API for managing user tasks with JWT authentication and Google OAuth support

To run the backend, clone the project https://github.com/BoarArtem/Savoria-Backend.git, make sure the directory in the terminal is correct, and cd SavoriaBackend.


Launch Dockerengine and run docker-compose up --build in the terminal, wait until all dependencies are pulled in


The base API URL is http://localhost:8000, API documentation will be available at http://localhost:8000/docs


## 🔹 Features

- User registration and login
- Google OAuth authentication
- CRUD operations for tasks
- JWT token management (access and refresh)
- Structured architecture with services, repositories, and routers

---

## 🛠 Technologies

- Python 3.13+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- JWT (PyJWT)
- Docker & Docker Compose