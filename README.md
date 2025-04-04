# LabFast API

A FastAPI backend with authentication and PostgreSQL integration.

## Features

- User authentication with JWT tokens
- PostgreSQL database integration
- CRUD operations for users
- CORS support for React frontend
- Type safety with Pydantic models

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE labfast;

# Create user (if needed)
CREATE USER postgres WITH PASSWORD 'postgres';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE labfast TO postgres;
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

## Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /token`: Login to get access token
- `POST /users/`: Create new user
- `GET /users/me/`: Get current user
- `GET /users/`: Get all users (requires authentication)
- `PUT /users/me/`: Update current user
- `DELETE /users/me/`: Delete current user

## Development

The project structure is organized as follows:

```
FastAPI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── database.py
├── requirements.txt
├── .env
└── README.md
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is configured for the React frontend
- Environment variables are used for sensitive data 