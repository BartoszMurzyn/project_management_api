# Project Management API

## Overview

The **Project Management API** is a RESTful API for managing projects, including creating, updating, deleting, and retrieving project details. It also provides endpoints for managing project documents and user authentication.  

This is a **multi-repository project**: the core repository (`project_management_core`) is automatically installed via `pyproject.toml`.

Core repo: [https://github.com/BartoszMurzyn/project-management-core](https://github.com/BartoszMurzyn/project-management-core)

---

## Architecture

### FastAPI
Built with **FastAPI**, a high-performance Python framework with automatic OpenAPI docs and type hints support.

### SQLAlchemy
Database interactions use **SQLAlchemy**, including async support via `asyncpg`.

### JWT Authentication
Authentication is via **JWT (JSON Web Tokens)**. Obtain a token by logging in with valid credentials and use it in the `Authorization` header for protected endpoints.

---

---

## Architecture

### FastAPI

The application is built using **FastAPI**, a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. FastAPI is known for its high performance and automatic generation of OpenAPI documentation.

### SQLAlchemy

For database interactions, the application utilizes **SQLAlchemy**, a powerful and flexible ORM (Object Relational Mapper) for Python. SQLAlchemy provides a set of high-level API to connect to relational databases and perform CRUD operations.

### JWT Authentication

User authentication is handled using **JWT (JSON Web Tokens)**. Users authenticate by providing their credentials, and upon successful authentication, a JWT token is issued. This token is then used to authorize subsequent requests to protected endpoints.



---

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.11+**: Required for running the application.
- **Docker**: Used for containerization.
- **Docker Compose**: Simplifies the management of multi-container Docker applications.

### Steps

1. **Clone the Repository**
```bash
   git clone https://github.com/BartoszMurzyn/project_management_api.git
   cd project_management_api
```

2.	**Create .env file**
Create a .env file in the root directory. You can use .env.example as a template:

```bash
cp .env.example .env
```
Fill in your own database credentials:
```bash
DBUsername=YOUR_DB_USERNAME
DBPassword=YOUR_DB_PASSWORD
DBHost=db
DBPort=5432
DBDatabase=project_management
```

3.	**Build and Run with Docker Compose**
```bash 
pip install .
docker-compose up --build
```
The API will be available at http://localhost:8000
Postgres will run on localhost:5433 (mapped from container port 5432)


### Usage

Once the application is running, you can interact with the API endpoints. 

**Authentication**

Before interacting with the API, obtain a JWT token by logging in with valid credentials. Use this token in the Authorization header for subsequent requests.

OpenAPI documentation is available at: http://localhost:8000/docs