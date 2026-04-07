# Handwerker Platform - Deployment Guide

This guide covers deploying the Handwerker Platform to production and managing the application lifecycle.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** 2.30+
- **Node.js** 18+ and **npm** 8+ (for frontend development)
- **Python** 3.11+ (for backend development)

### Required Services
- **PostgreSQL** 15+ database
- **Redis** 7+ for caching
- **SMTP Server** for email notifications
- **Domain name** with DNS access
- **SSL Certificate** (Let's Encrypt recommended)

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/dmankovsky/handwerker-platform.git
cd handwerker-platform
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your local configuration

# Start database and Redis with Docker
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8001
```

Backend will be available at `http://localhost:8001`

API Documentation: `http://localhost:8001/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Set VITE_API_URL=http://localhost:8001

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 4. Database Seeding (Optional)

```bash
# Create test users
python scripts/seed_data.py
```

---

## Production Deployment

### Option 1: Docker Compose Deployment (Recommended for Small-Medium Scale)

#### 1. Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create application directory
sudo mkdir -p /opt/handwerker-platform
cd /opt/handwerker-platform
```

#### 2. Clone Repository

```bash
sudo git clone https://github.com/dmankovsky/handwerker-platform.git .
```

#### 3. Configure Environment

```bash
# Create production .env file
sudo nano .env
```

Add production configuration (see [Environment Configuration](#environment-configuration))

#### 4. Build and Start Services

```bash
# Build images
sudo docker-compose -f docker-compose.prod.yml build

# Start services
sudo docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
sudo docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### 5. Set Up Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/handwerker-platform
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/handwerker-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Kubernetes Deployment (For Large Scale)

See [kubernetes/README.md](kubernetes/README.md) for Kubernetes deployment instructions.

---

## Environment Configuration

### Backend Environment Variables (.env)

```bash
# Application
APP_NAME=Handwerker Platform
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8001
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/handwerker_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-min-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@your-domain.com
SMTP_FROM_NAME=Handwerker Platform

# Stripe (Payment Processing)
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# AWS S3 (File Storage - Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=eu-central-1
S3_BUCKET_NAME=handwerker-uploads

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Frontend Environment Variables (.env)

```bash
# API Configuration
VITE_API_URL=https://your-domain.com/api
VITE_WS_URL=wss://your-domain.com/ws

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable-key

# Application
VITE_APP_NAME=Handwerker Platform
VITE_APP_VERSION=1.0.0

# Analytics (Optional)
VITE_GA_TRACKING_ID=G-XXXXXXXXXX
```

---

## Database Setup

### Production Database Configuration

#### 1. Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. Create Database and User

```bash
sudo -u postgres psql

CREATE DATABASE handwerker_prod;
CREATE USER handwerker_user WITH PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE handwerker_prod TO handwerker_user;
\q
```

#### 3. Configure PostgreSQL for Production

Edit `/etc/postgresql/15/main/postgresql.conf`:

```conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

#### 4. Database Backups

Create backup script `/opt/scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE="handwerker_prod"

mkdir -p $BACKUP_DIR

pg_dump -U handwerker_user -h localhost $DATABASE | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -type f -mtime +30 -delete
```

Make it executable and add to cron:

```bash
chmod +x /opt/scripts/backup-db.sh
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/scripts/backup-db.sh
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free SSL)

#### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

#### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts to configure HTTPS.

#### 3. Auto-Renewal

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

### Manual SSL Certificate

If using a purchased certificate:

```bash
# Copy certificate files
sudo cp your-certificate.crt /etc/ssl/certs/
sudo cp your-private-key.key /etc/ssl/private/

# Update Nginx configuration
sudo nano /etc/nginx/sites-available/handwerker-platform
```

Add SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/ssl/certs/your-certificate.crt;
    ssl_certificate_key /etc/ssl/private/your-private-key.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Monitoring and Maintenance

### Application Monitoring

#### 1. Set Up Logging

Configure backend logging in `app/core/config.py`:

```python
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/handwerker/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    }
}
```

#### 2. Monitor with Prometheus + Grafana (Optional)

See [monitoring/README.md](monitoring/README.md) for setup instructions.

#### 3. Error Tracking with Sentry

Already configured via `SENTRY_DSN` environment variable.

### Health Checks

Create health check script:

```bash
#!/bin/bash
# /opt/scripts/health-check.sh

API_URL="https://your-domain.com/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "API health check failed! Response: $RESPONSE"
    # Send alert (email, Slack, etc.)
fi
```

Add to cron (every 5 minutes):

```bash
*/5 * * * * /opt/scripts/health-check.sh
```

### Performance Monitoring

Monitor key metrics:
- **Response times**: API endpoint latency
- **Database**: Connection pool usage, query performance
- **Memory**: Backend/frontend container memory usage
- **CPU**: Server CPU utilization
- **Disk**: Database and logs disk usage

### Updating the Application

```bash
cd /opt/handwerker-platform

# Pull latest changes
sudo git pull origin master

# Rebuild and restart services
sudo docker-compose -f docker-compose.prod.yml build
sudo docker-compose -f docker-compose.prod.yml up -d

# Run new migrations
sudo docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Troubleshooting

### Common Issues

#### Backend not starting

```bash
# Check logs
sudo docker-compose logs backend

# Common causes:
# - Database connection issues (check DATABASE_URL)
# - Redis connection issues (check REDIS_URL)
# - Missing environment variables
```

#### Database connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U handwerker_user -h localhost -d handwerker_prod

# Check connection limits
SELECT count(*) FROM pg_stat_activity;
```

#### Email notifications not sending

```bash
# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-password')
print('SMTP connection successful!')
"
```

#### High memory usage

```bash
# Check Docker container stats
docker stats

# Restart specific service
docker-compose restart backend

# Adjust memory limits in docker-compose.prod.yml
```

#### WebSocket connection issues

```bash
# Check Nginx configuration for WebSocket proxying
# Ensure proper headers:
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";

# Test WebSocket endpoint
wscat -c wss://your-domain.com/ws
```

### Performance Optimization

#### Database Query Optimization

```bash
# Enable query logging
sudo nano /etc/postgresql/15/main/postgresql.conf

# Add:
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000  # Log queries > 1s

# Restart PostgreSQL
sudo systemctl restart postgresql

# Analyze slow queries
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### Redis Optimization

```bash
# Monitor Redis
redis-cli --stat

# Check memory usage
redis-cli info memory

# Clear cache if needed
redis-cli FLUSHDB
```

#### Frontend Performance

```bash
# Build optimized production bundle
cd frontend
npm run build

# Analyze bundle size
npm run build -- --analyze
```

---

## Security Best Practices

1. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   npm outdated
   ```

2. **Regular security audits**:
   ```bash
   pip-audit
   npm audit
   ```

3. **Firewall configuration**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **Database security**:
   - Use strong passwords
   - Limit network access (localhost only if possible)
   - Regular backups
   - Encrypt sensitive data

5. **API security**:
   - Rate limiting enabled
   - CORS properly configured
   - Input validation
   - SQL injection prevention (using ORM)

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/dmankovsky/handwerker-platform/issues
- Documentation: https://github.com/dmankovsky/handwerker-platform/wiki
- Email: support@your-domain.com

---

## License

See [LICENSE](LICENSE) file for details.
