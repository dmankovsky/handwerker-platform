# Handwerker Booking Platform

**Status**: ✅ MVP Complete - Ready for Deployment

A comprehensive platform connecting homeowners with verified craftsmen (Handwerker) in Germany.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

---

## Overview

This platform solves a critical problem in Germany: finding reliable, available craftsmen for home repairs and renovations. With average wait times of 6-12 months and difficulty finding available professionals, both homeowners and craftsmen lose out.

**For Homeowners**: Find and book verified craftsmen quickly, track work progress, and pay securely.

**For Craftsmen**: Get more customers, manage bookings efficiently, and receive payments automatically.

---

## Features

### ✨ For Homeowners

- **Search & Filter**: Find craftsmen by trade, location, rating, and hourly rate
- **View Profiles**: See detailed craftsman profiles with portfolios, ratings, and reviews
- **Book Online**: Request bookings with job details and preferred dates
- **Track Progress**: Monitor booking status from pending to completion
- **In-App Messaging**: Communicate directly with craftsmen
- **Rate & Review**: Leave detailed feedback after job completion
- **Secure Payments**: Pay through Stripe with platform protection

### 🔨 For Craftsmen

- **Professional Profile**: Company info, bio, hourly rate, service areas, and portfolio
- **Job Management**: Accept/reject booking requests, set schedules
- **Calendar System**: Manage availability and upcoming jobs
- **Portfolio Showcase**: Upload photos of completed work
- **Customer Communication**: Message homeowners directly
- **Automated Payments**: Receive payouts automatically after job completion
- **Reputation Building**: Collect reviews and build ratings

### 🏢 Platform Features

- **User Authentication**: Secure JWT-based authentication for both roles
- **Dual User Roles**: Separate interfaces for homeowners and craftsmen
- **Search & Discovery**: Advanced filtering by trade, location, price, and rating
- **Booking Lifecycle**: Complete workflow from request to payment
- **Review System**: Verified reviews with detailed ratings
- **Messaging**: Real-time communication within bookings
- **Stripe Payments**: Integrated payment processing with Stripe Connect
- **Payment Escrow**: Secure payment holding until job completion
- **Automated Payouts**: Automatic transfers to craftsmen after completion
- **Verification System**: Document upload and Handwerkskammer verification
- **Commission System**: Automatic 12% platform fee calculation
- **GDPR Compliant**: Built for German market compliance

---

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11
- **Database**: PostgreSQL 15 (async with SQLAlchemy 2.0)
- **Cache**: Redis 7
- **Authentication**: JWT with bcrypt password hashing
- **Payments**: Stripe Connect
- **Email**: SMTP (Gmail/SendGrid)
- **Deployment**: Docker & Docker Compose

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **SSL**: Let's Encrypt (certbot)
- **Hosting**: Hetzner Cloud VPS (€5.83/month)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Installation

```bash
# Clone repository
git clone https://github.com/dmankovsky/handwerker-platform.git
cd handwerker-platform

# Create environment file
cp .env.example .env

# Update .env with your configuration
# - Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# - Add your Gmail App Password for SMTP
nano .env

# Start services with Docker
docker-compose up -d

# Wait for services to start
sleep 15

# Initialize database
docker-compose exec app python -m app.core.init_db

# Check services are running
docker-compose ps
```

### Access the Application

- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## API Overview

### Authentication
- `POST /api/auth/register` - Register new user (homeowner/craftsman)
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user info

### Craftsman Profile
- `POST /api/craftsman/profile` - Create craftsman profile
- `GET /api/craftsman/profile/me` - Get my profile
- `PUT /api/craftsman/profile` - Update profile
- `GET /api/craftsman/search` - Search craftsmen with filters
- `GET /api/craftsman/{id}` - Get craftsman profile
- `POST /api/craftsman/trades` - Add trade
- `POST /api/craftsman/service-areas` - Add service area
- `POST /api/craftsman/portfolio` - Add portfolio item

### Bookings
- `POST /api/bookings/` - Create booking request
- `GET /api/bookings/` - Get my bookings
- `GET /api/bookings/{id}` - Get booking details
- `PUT /api/bookings/{id}/accept` - Accept booking (craftsman)
- `PUT /api/bookings/{id}/reject` - Reject booking (craftsman)
- `PUT /api/bookings/{id}/start` - Start work
- `PUT /api/bookings/{id}/complete` - Complete work
- `PUT /api/bookings/{id}/cancel` - Cancel booking

### Reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/craftsman/{id}` - Get craftsman reviews
- `GET /api/reviews/booking/{id}` - Get booking review
- `PUT /api/reviews/{id}` - Update review
- `POST /api/reviews/{id}/respond` - Respond to review (craftsman)

### Messaging
- `POST /api/messages/` - Send message
- `GET /api/messages/threads` - Get all message threads
- `GET /api/messages/booking/{id}` - Get booking messages
- `PUT /api/messages/{id}/read` - Mark message as read
- `GET /api/messages/unread-count` - Get unread count

**Full API documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## Business Model

### Revenue Streams

1. **Commission**: 12% fee on completed bookings
2. **Premium Craftsman Tier**: €29/month for:
   - Priority in search results
   - Enhanced profile features
   - Lower commission rate (10%)
   - Advanced analytics

### Pricing for Craftsmen

- **Free**: Create profile, receive booking requests
- **Commission**: 12% per completed job
- **Premium**: €29/month + 10% commission

### Market Opportunity

- **TAM**: 41M households in Germany
- **Craftsmen**: ~1M registered professionals
- **Market Size**: €400B annual home improvement spending
- **Average wait time**: 6-12 months for appointments

### Revenue Projections (Conservative)

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| **Craftsmen** | 100 | 500 | 2,000 |
| **Bookings/Month** | 500 | 2,500 | 10,000 |
| **Avg. Booking** | €1,000 | €1,000 | €1,000 |
| **Monthly Revenue** | €5,000 | €25,000 | €100,000 |
| **Annual Revenue** | €60K | €300K | €1.2M |

---

## Database Schema

### Core Models

1. **User**: Authentication and profile (homeowner/craftsman/admin)
2. **CraftsmanProfile**: Business information, rates, verification
3. **Trade**: Trades offered by craftsman (electrician, plumber, etc.)
4. **ServiceArea**: Geographic coverage (postal codes, cities)
5. **Portfolio**: Work examples with photos
6. **Booking**: Job requests and scheduling
7. **Review**: Ratings and feedback
8. **Payment**: Transaction tracking with Stripe
9. **Message/MessageThread**: In-app communication

---

## Deployment

### Production Deployment

Follow the comprehensive deployment guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Estimated time**: 2-3 hours
**Monthly cost**: €6.66 (VPS + domain)

### Quick Deploy to Hetzner

```bash
# 1. Create Hetzner CX21 server
# 2. SSH into server
ssh root@YOUR_SERVER_IP

# 3. Run deployment script
curl -sSL https://raw.githubusercontent.com/dmankovsky/handwerker-platform/main/deploy.sh | bash

# 4. Configure domain and SSL
# See DEPLOYMENT_GUIDE.md for details
```

---

## Development

### Project Structure

```
handwerker-platform/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── craftsman.py  # Craftsman profiles
│   │   ├── booking.py    # Booking management
│   │   ├── review.py     # Reviews and ratings
│   │   └── message.py    # Messaging
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   ├── security.py   # Auth utilities
│   │   └── init_db.py    # DB initialization
│   ├── models/           # Database models
│   │   ├── user.py
│   │   ├── craftsman.py
│   │   ├── booking.py
│   │   ├── review.py
│   │   ├── payment.py
│   │   └── message.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   ├── craftsman.py
│   │   ├── booking.py
│   │   ├── review.py
│   │   └── message.py
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── tests/                # Unit and integration tests
├── docker-compose.yml    # Docker services
├── Dockerfile            # Application container
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

### Running Tests

```bash
# Run all tests
docker-compose exec app pytest

# Run specific test file
docker-compose exec app pytest tests/test_auth.py

# Run with coverage
docker-compose exec app pytest --cov=app
```

### Database Migrations

```bash
# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec app alembic upgrade head

# Rollback migration
docker-compose exec app alembic downgrade -1
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

---

## Roadmap

### ✅ Phase 1: MVP (Complete)
- User authentication (homeowner + craftsman)
- Craftsman profiles with trades and service areas
- Search and filtering
- Booking system with lifecycle management
- Reviews and ratings
- In-app messaging
- Database models and API endpoints
- Docker deployment setup

### ✅ Phase 2: Payments & Verification (Complete)
- ✅ Stripe Connect integration
- ✅ Payment intent system with escrow
- ✅ Automated payouts to craftsmen
- ✅ Handwerkskammer verification system
- ✅ Document upload for verification

### 📋 Phase 3: Enhanced Features
- [ ] Frontend web application (React)
- [ ] Mobile apps (React Native)
- [ ] Real-time notifications (WebSocket)
- [ ] Calendar integration
- [ ] Email reminders
- [ ] SMS notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (German + English)

### 🎯 Phase 4: Scale & Optimize
- [ ] Performance optimization
- [ ] Caching strategies
- [ ] Rate limiting
- [ ] Admin panel
- [ ] Dispute resolution system
- [ ] Insurance integration
- [ ] Marketing automation

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints
- Write docstrings for functions
- Keep functions small and focused
- Write tests for new features

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For questions, issues, or suggestions:

- **GitHub Issues**: https://github.com/dmankovsky/handwerker-platform/issues
- **Email**: support@handwerker-platform.de
- **Developer**: @dmankovsky

---

## Related Projects

Part of the German IT solutions suite:

- **Termin-Notify**: Automated appointment notifications for German government services
  - Repository: https://github.com/dmankovsky/termin-notify
  - Status: Production-ready

- **Handwerker Platform**: This project
  - Repository: https://github.com/dmankovsky/handwerker-platform
  - Status: MVP complete

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database with [PostgreSQL](https://www.postgresql.org/)
- Payments by [Stripe](https://stripe.com/)
- Deployed on [Hetzner Cloud](https://www.hetzner.com/cloud)

---

**Ready to connect craftsmen with customers in Germany!** 🇩🇪 🔨

For deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
For API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).
