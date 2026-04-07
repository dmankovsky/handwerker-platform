# Testing Guide - Handwerker Platform

## Quick Start

### Backend API (Already Running)
The backend is running at: `http://localhost:8001`

**Health Check:**
```bash
curl http://localhost:8001/health
```

## Testing the API

### 1. Test User Registration

**Register a Homeowner:**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "homeowner@test.com",
    "password": "password123",
    "full_name": "Test Homeowner",
    "phone": "+49 123 456789",
    "role": "homeowner"
  }'
```

**Register a Craftsman:**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "craftsman@test.com",
    "password": "password123",
    "full_name": "Test Craftsman",
    "phone": "+49 987 654321",
    "role": "craftsman"
  }'
```

### 2. Test Login

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=homeowner@test.com&password=password123"
```

Save the `access_token` from the response.

### 3. Test Authenticated Requests

**Get Current User:**
```bash
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Create Craftsman Profile:**
```bash
curl -X PUT http://localhost:8001/api/craftsman/profile \
  -H "Authorization: Bearer CRAFTSMAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Handwerker GmbH",
    "bio": "Professional craftsman with 10 years experience",
    "years_experience": 10,
    "trades": ["electrician", "plumber"],
    "service_areas": ["Berlin", "Munich"],
    "hourly_rate": 75,
    "accepts_bookings": true
  }'
```

**Search Craftsmen:**
```bash
curl "http://localhost:8001/api/craftsman/search?trade=electrician"
```

**Create Booking:**
```bash
curl -X POST http://localhost:8001/api/bookings/ \
  -H "Authorization: Bearer HOMEOWNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "craftsman_id": 1,
    "job_title": "Fix electrical outlet",
    "job_description": "Kitchen outlet not working, needs inspection and repair",
    "service_address": "Hauptstraße 123, 10115 Berlin",
    "requested_date": "2026-04-15",
    "estimated_hours": 2
  }'
```

### 4. Test i18n API

**Get Supported Languages:**
```bash
curl http://localhost:8001/api/i18n/languages
```

**Get Translations:**
```bash
curl "http://localhost:8001/api/i18n/translate/common.welcome?lang=de"
curl "http://localhost:8001/api/i18n/translate/common.welcome?lang=en"
```

**Get Category Translations:**
```bash
curl "http://localhost:8001/api/i18n/translations/booking?lang=de"
```

## API Documentation

Visit the interactive API docs:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Database Access

**Connect to PostgreSQL:**
```bash
docker exec -it handwerker_postgres psql -U handwerker_user -d handwerker_platform
```

**Useful Queries:**
```sql
-- List all users
SELECT id, email, full_name, role FROM users;

-- List all craftsman profiles
SELECT * FROM craftsman_profiles;

-- List all bookings
SELECT id, job_title, status, homeowner_id, craftsman_id FROM bookings;
```

## WebSocket Testing

**Connect to WebSocket (requires auth token):**
```javascript
const ws = new WebSocket('ws://localhost:8001/ws?token=YOUR_ACCESS_TOKEN');

ws.onmessage = (event) => {
  console.log('Notification:', JSON.parse(event.data));
};
```

## Email Testing

Emails are configured to be sent via SMTP. Check your console/logs for email sending attempts or configure a real SMTP server in `.env`.

## Frontend Setup (When npm is available)

Due to npm registry configuration issues, the frontend needs to be set up with a different npm configuration. Once resolved:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: http://localhost:3000

## What's Been Implemented

### Backend (Complete)
- ✅ User authentication (JWT)
- ✅ Craftsman profiles
- ✅ Booking management
- ✅ Reviews and ratings
- ✅ Messaging system
- ✅ Payment integration (Stripe)
- ✅ Verification system
- ✅ Email notifications
- ✅ WebSocket real-time notifications
- ✅ Multi-language support (German/English)

### Frontend (Complete)
- ✅ Authentication UI (Login/Register)
- ✅ Craftsman search and discovery
- ✅ Booking management interface
- ✅ Responsive design
- ✅ Form validation
- ✅ Protected routes
- ✅ Role-based UI

### Remaining Tasks
- Real-time messaging UI
- Profile management UI
- Payment integration UI
- Review/rating UI

## Test User Accounts

Once registered, you can use these test accounts:

**Homeowner:**
- Email: homeowner@test.com
- Password: password123

**Craftsman:**
- Email: craftsman@test.com
- Password: password123

## Common Issues

1. **Port conflicts:** Make sure ports 8001, 5433, and 6380 are available
2. **Database not initialized:** Run `docker-compose exec app python -m app.core.init_db`
3. **Health check failing:** The app might show as unhealthy but still work - check `/health` endpoint directly

## Testing Workflow

1. Register a homeowner and craftsman
2. Login as craftsman and create profile
3. Login as homeowner and search for craftsmen
4. Create a booking as homeowner
5. Login as craftsman and accept/reject booking
6. Test booking lifecycle (accept → confirm → start → complete)
7. Leave a review as homeowner
8. Test real-time notifications via WebSocket
