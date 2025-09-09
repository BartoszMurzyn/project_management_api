# Project Management API

## Overview

The **Project Management API** is a RESTful API designed to facilitate the management of projects, including functionalities such as creating, updating, deleting, and retrieving project details. It provides endpoints for managing project documents and user authentication, making it a comprehensive solution for project management needs.

---

## Architecture

### FastAPI

The application is built using **FastAPI**, a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. FastAPI is known for its high performance and automatic generation of OpenAPI documentation.

### SQLAlchemy

For database interactions, the application utilizes **SQLAlchemy**, a powerful and flexible ORM (Object Relational Mapper) for Python. SQLAlchemy provides a set of high-level API to connect to relational databases and perform CRUD operations.

### JWT Authentication

User authentication is handled using **JWT (JSON Web Tokens)**. Users authenticate by providing their credentials, and upon successful authentication, a JWT token is issued. This token is then used to authorize subsequent requests to protected endpoints.

### Domain-Driven Design (DDD)

The application follows **Domain-Driven Design (DDD)** principles, organizing the codebase around the business domain. This approach ensures that the system's design reflects the business logic and processes, leading to a more maintainable and scalable application.

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

2.	**Install Python Dependencies**

    ```bash
    pip install .

This command installs the necessary Python packages as defined in the pyproject.toml file.

3.	**Build and Run with Docker Compose**
    ```bash
    docker-compose up -d --build
This command builds and starts the application in detached mode.

### Usage

Once the application is running, you can interact with the API endpoints. 

**Authentication**

Before interacting with the API, obtain a JWT token by logging in with valid credentials. Use this token in the Authorization header for subsequent requests.
