# Pick and Eat – Grocery Ordering System

## Overview

Pick and Eat is a backend-based grocery ordering system built using **FastAPI**.
The system allows users to register, log in, browse products, search products, add items to cart, place orders, and review products.

The project demonstrates **authentication, database management, API development, and backend logic** using modern Python frameworks.

---

## Tech Stack

* **Backend Framework:** FastAPI
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Authentication:** JWT (JSON Web Tokens)
* **Password Hashing:** Passlib (bcrypt)
* **Frontend:** HTML, CSS
* **API Testing:** Swagger UI

---

## Features

### User Authentication

* User registration
* Secure login system
* JWT token authentication
* Password hashing using bcrypt

### Product Management

* View all products
* Search products by name
* Filter products by price
* Sort products (ascending / descending)
* Admin can add or delete products

### Cart System

* Add products to cart
* View items in cart
* Quantity management

### Order System

* Checkout from cart
* Order creation
* Order history tracking
* Stock validation

### Review System

* Add product reviews
* View product ratings and comments

---

## Database Tables

The system includes the following tables:

* Users
* Products
* Cart
* Orders
* Order Items
* Reviews

These tables are connected using **SQLAlchemy relationships**.

---

## API Endpoints

### Authentication

POST /register
POST /login

### Products

GET /products
GET /products/{product_id}
POST /products (Admin only)
DELETE /products/{product_id}

### Product Search

GET /products/search

### Cart

POST /cart
GET /cart

### Orders

POST /checkout
GET /my-orders

### Reviews

POST /add-review
GET /product-reviews

---

## How to Run the Project

### 1. Clone the repository

git clone https://github.com/your-username/pick-and-eat.git

### 2. Go to project folder

cd pick-and-eat

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the FastAPI server

uvicorn main:app --reload

### 5. Open in browser

API Documentation
http://127.0.0.1:8000/docs

Frontend
http://127.0.0.1:8000

---

## Learning Outcomes

This project helped in understanding:

* Building REST APIs using FastAPI
* Implementing JWT authentication
* Database operations with SQLAlchemy
* Designing relational database schemas
* Backend logic for real-world applications
* Handling user sessions and protected routes

---

## Future Improvements

* Payment gateway integration
* Product recommendation system
* Order tracking
* Deployment using Docker
* Cloud database integration

---

## Author

Govardhani G
B.Tech (IoT) – Backend Development Enthusiast
