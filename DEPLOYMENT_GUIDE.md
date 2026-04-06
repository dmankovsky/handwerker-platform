# Handwerker Platform - Deployment Guide

Complete guide for deploying the Handwerker Platform to production.

---

## Prerequisites

- Hetzner Cloud account (or any VPS provider)
- Domain name (recommended)
- Gmail account with App Password (for email notifications)
- Stripe account (optional, for payments)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/dmankovsky/handwerker-platform.git
cd handwerker-platform
```

### 2. Create Environment File

```bash
cp .env.example .env
nano .env
```

Update the following values:
- `DATABASE_URL`: Use `localhost` instead of `postgres` for local development
- `REDIS_URL`: Use `localhost` instead of `redis` for local development
- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `SMTP_*`: Your Gmail credentials

### 3. Start Services with Docker

```bash
# Build and start all services
docker-compose up -d

# Wait for services to be ready (10-15 seconds)
sleep 15

# Check services are running
docker-compose ps
```

### 4. Initialize Database

```bash
# Create database tables
docker-compose exec app python -m app.core.init_db
```

### 5. Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Production Deployment

### Phase 1: Server Setup (Hetzner Cloud)

#### 1. Create Server

1. Go to https://console.hetzner.cloud/
2. Create new project: "handwerker-platform-production"
3. Create server:
   - **Location**: Nuremberg, Germany (GDPR compliance)
   - **Image**: Ubuntu 22.04
   - **Type**: CX21 (€5.83/month)
   - **SSH Key**: Add your public key
   - **Name**: handwerker-prod

#### 2. SSH into Server

```bash
ssh root@YOUR_SERVER_IP
```

#### 3. Update System

```bash
apt update && apt upgrade -y
```

#### 4. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Enable Docker
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt install docker-compose -y

# Verify installations
docker --version
docker-compose --version
```

#### 5. Install Additional Tools

```bash
apt install -y git nginx certbot python3-certbot-nginx ufw
```

#### 6. Setup Firewall

```bash
# Allow SSH (CRITICAL - do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### Phase 2: Application Deployment

#### 1. Clone Repository

```bash
cd /opt
git clone https://github.com/dmankovsky/handwerker-platform.git
cd handwerker-platform
```

#### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

**Update these values**:

```env
# Database (use Docker service names)
DATABASE_URL=postgresql+asyncpg://handwerker_user:STRONG_PASSWORD@postgres:5432/handwerker_platform
DATABASE_URL_SYNC=postgresql://handwerker_user:STRONG_PASSWORD@postgres:5432/handwerker_platform

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=<generate-random-string>
ENVIRONMENT=production
DEBUG=False
FRONTEND_URL=https://your-domain.com

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<16-char-app-password>
EMAIL_FROM=noreply@your-domain.com

# Stripe (optional)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

**Generate SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. Update docker-compose.yml

```bash
nano docker-compose.yml
```

Update the postgres password to match your .env file:
```yaml
postgres:
  environment:
    POSTGRES_PASSWORD: STRONG_PASSWORD  # Same as in .env!
```

#### 4. Start Services

```bash
# Build and start
docker-compose up -d

# Wait for services
sleep 20

# Check status
docker-compose ps
```

#### 5. Initialize Database

```bash
docker-compose exec app python -m app.core.init_db
```

#### 6. Verify Application

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy","environment":"production"}
```

### Phase 3: Domain & SSL Setup

#### 1. Configure DNS

In your domain registrar (Namecheap, GoDaddy, etc.):

- Add A record: `@` → `YOUR_SERVER_IP`
- Add A record: `www` → `YOUR_SERVER_IP`
- Wait 5-10 minutes for DNS propagation

#### 2. Configure Nginx

```bash
nano /etc/nginx/sites-available/handwerker-platform
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        alias /opt/handwerker-platform/uploads/;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/handwerker-platform /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 3. Get SSL Certificate

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow prompts:
1. Enter email
2. Agree to terms (Y)
3. Share email? (N)
4. Redirect HTTP to HTTPS? (2 - Yes)

#### 4. Test HTTPS

```bash
curl https://your-domain.com/health
```

### Phase 4: Post-Deployment

#### 1. Setup Automated Backups

```bash
mkdir -p /opt/backups

nano /opt/backup-handwerker.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
cd /opt/handwerker-platform
docker-compose exec -T postgres pg_dump -U handwerker_user handwerker_platform | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup .env
cp /opt/handwerker-platform/.env $BACKUP_DIR/env_$DATE.bak

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*.bak" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x /opt/backup-handwerker.sh

# Add to cron (daily at 2 AM)
crontab -e
```

Add line:
```
0 2 * * * /opt/backup-handwerker.sh >> /var/log/handwerker-backup.log 2>&1
```

#### 2. Setup Monitoring

```bash
nano /opt/monitor-handwerker.sh
```

Add:
```bash
#!/bin/bash
cd /opt/handwerker-platform

SERVICES=$(docker-compose ps -q | wc -l)

if [ "$SERVICES" -lt 3 ]; then
    echo "WARNING: Some services are down!"
    docker-compose ps
    docker-compose up -d
    echo "Attempted restart at $(date)"
fi
```

```bash
chmod +x /opt/monitor-handwerker.sh

# Add to cron (check every 5 minutes)
crontab -e
```

Add line:
```
*/5 * * * * /opt/monitor-handwerker.sh >> /var/log/handwerker-monitor.log 2>&1
```

---

## Maintenance

### View Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### Restart Services

```bash
# Restart app only
docker-compose restart app

# Restart all services
docker-compose restart

# Stop and start
docker-compose down
docker-compose up -d
```

### Update Application

```bash
cd /opt/handwerker-platform

# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs
docker-compose logs -f app
```

### Database Migrations

```bash
# Create migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec app alembic upgrade head

# Rollback
docker-compose exec app alembic downgrade -1
```

### Manual Backup

```bash
/opt/backup-handwerker.sh
```

### Restore from Backup

```bash
# List backups
ls -lh /opt/backups/

# Restore database
gunzip < /opt/backups/db_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose exec -T postgres psql -U handwerker_user handwerker_platform
```

---

## Troubleshooting

### Services won't start

```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Database connection failed

```bash
# Check passwords match
cat .env | grep DATABASE_URL
cat docker-compose.yml | grep POSTGRES_PASSWORD

# Restart postgres
docker-compose restart postgres
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Check large files
du -sh /opt/* | sort -h
```

### SSL certificate renewal

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
```

---

## Monthly Costs

| Item | Cost |
|------|------|
| Hetzner CX21 VPS | €5.83 |
| Domain (yearly/12) | €0.83 |
| **Total** | **€6.66/month** |

- Gmail SMTP: FREE (500 emails/day)
- SSL (Let's Encrypt): FREE
- Stripe: 1.4% + €0.25 per transaction

---

## Security Checklist

- [ ] Strong database password
- [ ] Secure SECRET_KEY
- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] Regular backups enabled
- [ ] Monitoring enabled
- [ ] Gmail App Password (not main password)
- [ ] .env file not committed to git
- [ ] DEBUG=False in production
- [ ] Regular security updates (`apt upgrade`)

---

## Production URLs

- **API**: https://your-domain.com
- **API Docs**: https://your-domain.com/docs
- **Health**: https://your-domain.com/health

---

**Estimated deployment time**: 2-3 hours

Good luck! 🚀
