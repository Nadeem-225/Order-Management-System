# Order Management System with Priority Scheduling

A backend **Order Management System** built using **Python, Flask, SQLite, JWT Authentication, and Docker**.

The system supports secure order management, role-based access, priority scheduling using queues/heaps, and REST APIs with Swagger documentation.

---

## Features

- User Authentication with JWT
- Role-based access control (Admin/User)
- Create, Read, Update, Delete Orders (CRUD)
- Priority-based Order Processing
- Queue / Heap-based Scheduling Logic
- Search, Filtering, and Pagination
- Swagger API Documentation
- Dockerized Deployment
- Environment Variable Support using `.env`

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite + SQLAlchemy
- **Authentication:** JWT (`Flask-JWT-Extended`)
- **API Testing:** Postman
- **Documentation:** Swagger (`Flasgger`)
- **Containerization:** Docker

---

## Project Structure

```text
Order-Management-System/
│── app.py
│── requirements.txt
│── Dockerfile
│── .env
│── extensions.py
│── orders.db
│── README.md
│
├── models/
│   ├── order.py
│   └── user.py
│
├── routes/
│   ├── order_routes.py
│   └── auth_routes.py
│
└── venv/
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register a user |
| POST | `/login` | Login and get JWT token |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Create order (Admin only) |
| GET | `/api/v1/orders` | Get all orders |
| GET | `/api/v1/orders/<id>` | Get order by ID |
| PUT | `/api/v1/orders/<id>` | Update order (Admin only) |
| DELETE | `/api/v1/orders/<id>` | Delete order (Admin only) |
| GET | `/api/v1/orders/process` | Process highest priority order |

---

## Authentication

Protected endpoints require a JWT token.

Example:

```http
Authorization: Bearer your_jwt_token
```

---

## Installation

### Clone Repository

```bash
git clone <(https://github.com/Nadeem-225/Order-Management-System)>
cd Order-Management-System
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create `.env`

```env
JWT_SECRET_KEY=your_super_secure_secret_key_here
```

### Run Application

```bash
venv/bin/python app.py
```

Server runs at:

```text
http://127.0.0.1:5000
```

Swagger Documentation:

```text
http://127.0.0.1:5000/apidocs/
```

---

## Docker Setup

### Build Docker Image

```bash
docker build -t order-management .
```

### Run Docker Container

```bash
docker run -p 5001:5000 order-management
```

Application URL:

```text
http://127.0.0.1:5001
```

---

## Sample Order JSON

```json
{
  "customer_name": "Nadeem",
  "product": "MacBook",
  "quantity": 2,
  "priority": 1
}
```

---

## Future Improvements

- PostgreSQL Integration
- Redis Queue Support
- Cloud Deployment (AWS / Render)
- Unit Testing
- Admin Dashboard

---

## Author

**Nadeem Shaik**
