# Handwerker Booking Platform

**Status**: 🚧 In Development

A platform connecting homeowners with verified craftsmen (Handwerker) in Germany.

## Overview

This platform addresses a critical pain point in Germany: finding reliable, available craftsmen for home repairs and renovations. Long wait times (often 6-12 months) and difficulty finding available professionals create frustration for homeowners and lost revenue for craftsmen.

## Planned Features

### For Homeowners
- Search for craftsmen by trade, location, and availability
- View verified profiles with ratings and reviews
- Book appointments directly online
- Track job status and communicate with craftsmen
- Secure payment processing
- Review and rate completed work

### For Craftsmen
- Digital profile and portfolio management
- Online calendar and booking system
- Automated appointment reminders
- Job request management
- Payment processing integration
- Customer relationship management
- Marketing exposure to local customers

### For Platform
- Verification system for craftsmen (Handwerkskammer integration)
- Rating and review system
- Dispute resolution
- Payment escrow
- Analytics and reporting
- Commission-based revenue model (10-15%)

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: JWT
- **Payments**: Stripe
- **Frontend**: React (planned)
- **Deployment**: Docker, Hetzner Cloud

## Business Model

- **Free** for homeowners
- **Commission-based** for craftsmen: 10-15% per completed job
- **Premium tier** for craftsmen: Enhanced profile, priority in search results (€29/month)

## Market Opportunity

### Total Addressable Market
- 41M households in Germany
- ~1M registered craftsmen
- €400B annual home improvement market
- Average wait time: 6-12 months for appointments

### Target Segments
1. **Homeowners**: Busy professionals, elderly, expats
2. **Craftsmen**: Solo practitioners, small businesses (1-10 employees)
3. **Trades**: Electricians, plumbers, painters, carpenters, renovations

### Revenue Projections (Conservative)
- **Year 1**: 100 craftsmen, 500 bookings/month → €60K revenue
- **Year 2**: 500 craftsmen, 2,500 bookings/month → €300K revenue
- **Year 3**: 2,000 craftsmen, 10,000 bookings/month → €1.2M revenue

## Development Status

Currently in initial setup phase. Basic project structure created.

### Completed
- [x] Project structure
- [x] Database configuration
- [x] Basic settings

### Planned
- [ ] User authentication (homeowners + craftsmen)
- [ ] Craftsman profile management
- [ ] Search and filtering
- [ ] Booking system
- [ ] Calendar integration
- [ ] Payment processing
- [ ] Rating and review system
- [ ] Messaging system
- [ ] Admin panel
- [ ] Frontend application

## Related Projects

This platform is part of a suite of solutions addressing inefficiencies in the German market:
- **Termin-Notify**: Automated appointment notification system for government services
- **Handwerker Platform**: This project

## Getting Started

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

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start with Docker
docker-compose up -d

# Initialize database
docker-compose exec app alembic upgrade head

# Access API
open http://localhost:8000/docs
```

## License

MIT License - See LICENSE file for details

## Contact

Developed by @dmankovsky

---

**Note**: This project is in early development. Contributions and feedback are welcome!
