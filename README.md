# FastAPI Product CRUD Application with JWT Security

This project is a **FastAPI-based REST API** for managing products with **CRUD operations** (Create, Read, Update, Delete) and **JWT token-based authentication** for secure access.

---

## Features
- Product management with CRUD operations
- JWT token-based authentication
- Role-based access (admin vs regular user)
- Modular FastAPI structure with routers
- PostgreSQL support for database
- Password hashing with Argon2 (secure)

---

## Requirements
- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy
- python-jose[cryptography] (for JWT)
- passlib[argon2] (for password hashing)
- psycopg2 (if using PostgreSQL) or SQLite

---

## Installation

1. **Clone the repository**

git clone https://github.com/yourusername/product-crud-fastapi.git
cd product-crud-fastapi

2. **Create and activate virtual environment**

python -m venv local

## inside this (venv\Scripts\activate)  
D:\Skills\Python\product_app\local\Scripts\Activate.ps1  

3. **Install dependencies**

pip install fastapi uvicorn python-jose[cryptography] passlib[argon2] sqlalchemy  etc.


4. **Configure database**

Update SQLALCHEMY_DATABASE_URL in db_config.py with your database credentials (PostgreSQL).

5. **Run Application**

uvicorn main:app --reload

6. **Access APIs Docs**
API docs available at: http://127.0.0.1:8000/docs | http://localhost:8000/docs#/
ReDoc available at: http://127.0.0.1:8000/redoc   | http://localhost:8000/docs#/