##  Handwerker Platform API Documentation

**Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Register User

**POST** `/api/auth/register`

Create a new user account (homeowner or craftsman).

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "phone": "+49 176 12345678",
  "role": "homeowner",  // or "craftsman"
  "city": "Berlin",
  "postal_code": "10115"
}
```

**Response** (201):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "homeowner",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### Login

**POST** `/api/auth/login`

Login with email and password (form data).

**Request Body** (form-data):
```
username: user@example.com
password: SecurePassword123
```

**Response** (200):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": { ... }
}
```

### Get Current User

**GET** `/api/auth/me`

Get information about the currently authenticated user.

**Response** (200):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "homeowner",
  "city": "Berlin",
  "postal_code": "10115",
  "is_active": true,
  "email_verified": false,
  "created_at": "2024-01-15T10:30:00"
}
```

---

## Craftsman Profile

### Create Profile

**POST** `/api/craftsman/profile`

Create a craftsman profile (craftsmen only).

**Request Body**:
```json
{
  "company_name": "Schmidt Elektrik GmbH",
  "bio": "Experienced electrician with 15 years in the field...",
  "hourly_rate": 65.00,
  "years_experience": 15,
  "max_radius_km": 30,
  "handwerkskammer_number": "HWK123456",
  "trades": [
    {
      "trade_type": "electrician",
      "is_primary": true
    }
  ],
  "service_areas": [
    {
      "postal_code": "10115",
      "city": "Berlin",
      "state": "Berlin"
    }
  ]
}
```

**Response** (201):
```json
{
  "id": 1,
  "user_id": 2,
  "company_name": "Schmidt Elektrik GmbH",
  "bio": "Experienced electrician...",
  "hourly_rate": 65.00,
  "years_experience": 15,
  "is_verified": false,
  "total_jobs": 0,
  "average_rating": 0.0,
  "total_reviews": 0,
  "accepts_bookings": true,
  "max_radius_km": 30,
  "trades": [...],
  "service_areas": [...],
  "portfolio": []
}
```

### Search Craftsmen

**GET** `/api/craftsman/search`

Search for craftsmen with filters.

**Query Parameters**:
- `trade_type` (optional): Filter by trade (e.g., "electrician", "plumber")
- `postal_code` (optional): Filter by postal code
- `city` (optional): Filter by city name
- `max_hourly_rate` (optional): Maximum hourly rate
- `min_rating` (optional): Minimum average rating (0-5)
- `is_verified` (optional): Only verified craftsmen
- `skip` (default: 0): Pagination offset
- `limit` (default: 20): Results per page

**Example**:
```
GET /api/craftsman/search?trade_type=electrician&city=Berlin&max_hourly_rate=80&min_rating=4.0
```

**Response** (200):
```json
[
  {
    "id": 1,
    "user_id": 2,
    "company_name": "Schmidt Elektrik GmbH",
    "hourly_rate": 65.00,
    "average_rating": 4.8,
    "total_reviews": 24,
    "is_verified": true,
    "trades": [...],
    "service_areas": [...]
  },
  ...
]
```

### Get Craftsman Profile

**GET** `/api/craftsman/{craftsman_id}`

Get a specific craftsman's public profile.

**Response** (200):
```json
{
  "id": 1,
  "company_name": "Schmidt Elektrik GmbH",
  "bio": "...",
  "hourly_rate": 65.00,
  "average_rating": 4.8,
  "total_reviews": 24,
  "trades": [...],
  "service_areas": [...],
  "portfolio": [
    {
      "id": 1,
      "title": "Modern Office Electrical Installation",
      "description": "Complete rewiring of 500m² office space",
      "image_url": "https://...",
      "trade_type": "electrician",
      "created_at": "2024-01-10T14:20:00"
    }
  ]
}
```

---

## Bookings

### Create Booking

**POST** `/api/bookings/`

Create a new booking request (homeowners only).

**Request Body**:
```json
{
  "craftsman_id": 2,
  "title": "Kitchen Electrical Rewiring",
  "description": "Need to rewire kitchen for new appliances, add 2 additional outlets...",
  "trade_type": "electrician",
  "service_address": "Alexanderplatz 1, 10178 Berlin",
  "postal_code": "10178",
  "city": "Berlin",
  "requested_date": "2024-02-15T09:00:00",
  "estimated_hours": 6.0
}
```

**Response** (201):
```json
{
  "id": 1,
  "homeowner_id": 1,
  "craftsman_id": 2,
  "title": "Kitchen Electrical Rewiring",
  "description": "...",
  "trade_type": "electrician",
  "service_address": "Alexanderplatz 1, 10178 Berlin",
  "status": "pending",
  "requested_date": "2024-02-15T09:00:00",
  "estimated_hours": 6.0,
  "hourly_rate": 65.00,
  "estimated_cost": 390.00,
  "platform_commission_rate": 0.12,
  "created_at": "2024-01-15T11:00:00"
}
```

### Get My Bookings

**GET** `/api/bookings/`

Get all bookings for current user (as homeowner or craftsman).

**Query Parameters**:
- `status_filter` (optional): Filter by status (pending, accepted, completed, etc.)

**Response** (200):
```json
[
  {
    "id": 1,
    "title": "Kitchen Electrical Rewiring",
    "status": "pending",
    "requested_date": "2024-02-15T09:00:00",
    "estimated_cost": 390.00,
    ...
  },
  ...
]
```

### Accept Booking

**PUT** `/api/bookings/{booking_id}/accept`

Accept a booking request (craftsmen only).

**Request Body**:
```json
{
  "scheduled_date": "2024-02-15T09:00:00"
}
```

**Response** (200):
```json
{
  "id": 1,
  "status": "accepted",
  "scheduled_date": "2024-02-15T09:00:00",
  "accepted_at": "2024-01-15T12:00:00",
  ...
}
```

### Reject Booking

**PUT** `/api/bookings/{booking_id}/reject`

Reject a booking request (craftsmen only).

**Request Body**:
```json
{
  "reason": "Already booked for that date"
}
```

### Complete Booking

**PUT** `/api/bookings/{booking_id}/complete`

Mark booking as completed (craftsmen only).

**Request Body**:
```json
{
  "actual_hours": 7.5
}
```

**Response** (200):
```json
{
  "id": 1,
  "status": "completed",
  "actual_hours": 7.5,
  "final_cost": 487.50,
  "completed_at": "2024-02-15T17:30:00",
  ...
}
```

### Cancel Booking

**PUT** `/api/bookings/{booking_id}/cancel`

Cancel a booking (homeowner or craftsman).

**Request Body**:
```json
{
  "reason": "Found another craftsman with earlier availability"
}
```

---

## Reviews

### Create Review

**POST** `/api/reviews/`

Create a review for a completed booking (homeowners only).

**Request Body**:
```json
{
  "booking_id": 1,
  "rating": 5.0,
  "quality_rating": 5.0,
  "communication_rating": 4.5,
  "punctuality_rating": 5.0,
  "value_rating": 4.5,
  "title": "Excellent work!",
  "comment": "Very professional, arrived on time, cleaned up after work. Highly recommended!"
}
```

**Response** (201):
```json
{
  "id": 1,
  "booking_id": 1,
  "reviewer_id": 1,
  "craftsman_id": 2,
  "rating": 5.0,
  "quality_rating": 5.0,
  "communication_rating": 4.5,
  "punctuality_rating": 5.0,
  "value_rating": 4.5,
  "title": "Excellent work!",
  "comment": "...",
  "is_verified": true,
  "is_visible": true,
  "created_at": "2024-02-16T10:00:00"
}
```

### Get Craftsman Reviews

**GET** `/api/reviews/craftsman/{craftsman_id}`

Get all visible reviews for a craftsman.

**Query Parameters**:
- `skip` (default: 0): Pagination offset
- `limit` (default: 20): Results per page

**Response** (200):
```json
[
  {
    "id": 1,
    "rating": 5.0,
    "title": "Excellent work!",
    "comment": "...",
    "created_at": "2024-02-16T10:00:00",
    "reviewer_name": "John D.",
    "response": "Thank you for the kind words!",
    "response_date": "2024-02-16T15:00:00"
  },
  ...
]
```

### Respond to Review

**POST** `/api/reviews/{review_id}/respond`

Respond to a review (craftsman only).

**Request Body**:
```json
{
  "response": "Thank you for the kind words! It was a pleasure working with you."
}
```

---

## Messages

### Send Message

**POST** `/api/messages/`

Send a message in a booking conversation.

**Request Body**:
```json
{
  "booking_id": 1,
  "content": "I have a question about the electrical panel..."
}
```

**Response** (201):
```json
{
  "id": 1,
  "thread_id": 1,
  "sender_id": 1,
  "recipient_id": 2,
  "content": "I have a question about the electrical panel...",
  "is_read": false,
  "created_at": "2024-01-15T13:00:00"
}
```

### Get Message Threads

**GET** `/api/messages/threads`

Get all message threads for current user.

**Response** (200):
```json
[
  {
    "id": 1,
    "booking_id": 1,
    "booking_title": "Kitchen Electrical Rewiring",
    "booking_status": "in_progress",
    "messages": [...],
    "unread_count": 2,
    "updated_at": "2024-01-15T14:00:00"
  },
  ...
]
```

### Get Booking Messages

**GET** `/api/messages/booking/{booking_id}`

Get all messages for a specific booking.

**Response** (200):
```json
{
  "id": 1,
  "booking_id": 1,
  "booking_title": "Kitchen Electrical Rewiring",
  "messages": [
    {
      "id": 1,
      "sender_id": 1,
      "content": "I have a question...",
      "is_read": true,
      "created_at": "2024-01-15T13:00:00"
    },
    ...
  ],
  "unread_count": 0
}
```

### Get Unread Count

**GET** `/api/messages/unread-count`

Get total unread message count.

**Response** (200):
```json
{
  "unread_count": 3
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

**Error Format**:
```json
{
  "detail": "Error message description"
}
```

**Validation Error Format**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

---

## Interactive API Documentation

Visit `/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.

Visit `/redoc` for alternative ReDoc documentation.
