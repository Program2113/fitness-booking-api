# 🏋️‍♀️ Fitness Studio Booking API

A simple RESTful API for managing class schedules and bookings at a fictional fitness studio. Built with Python and designed to demonstrate clean architecture, validation, and basic CRUD functionality.

---

## 🚀 Features

- View all upcoming fitness classes
- Book a spot in a class (with availability checks)
- Retrieve all bookings for a specific client

---

## 📌 Endpoints

### 1. `GET /classes`

Returns a list of all upcoming fitness classes.

#### ✅ Response:
```json
[
  {
    "id": 1,
    "name": "Yoga",
    "date": "2025-06-15T10:00:00",
    "instructor": "Alice",
    "available_slots": 5
  },
]

2. POST /book
Books a spot in a class for a client. Checks for slot availability.

📥 Request Body:
{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}

✅ Successful Response:
{
  "message": "Booking successful!",
  "booking_id": 123
}

❌ Error Response (e.g., no slots available):
{
  "error": "No available slots for this class."
}

3. GET /bookings?email=client@example.com
Returns all bookings associated with a specific client email.

#### ✅ Response:
[
  {
    "booking_id": 123,
    "class_name": "Yoga",
    "date": "2025-06-15T10:00:00",
    "instructor": "Alice"
  },
  ...
]

## 🧪 Running the Project Locally
#### 1. Clone the repository

git clone https://github.com/Program2113/fitness-booking-api.git
cd fitness-booking-api

#### 2. Install dependencies

pip install -r requirements.txt

