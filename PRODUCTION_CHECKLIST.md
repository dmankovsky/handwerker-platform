# Production Deployment Checklist

**Target:** Deploy Handwerker Platform to production ASAP
**Estimated Time:** 4-6 hours

---

## ⚠️ CRITICAL: Test Frontend First (30 mins)

Before deploying, you **must** verify the frontend works locally:

```bash
cd frontend

# Fix npm registry if needed
npm config set registry https://registry.npmjs.org/

# Install dependencies
npm install

# Create .env file
cp .env.example .env
nano .env
```

Update `.env`:
```bash
VITE_API_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001/ws
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key  # Get from Stripe dashboard
```

```bash
# Start frontend
npm run dev
```

**Test these critical flows:**
- [ ] Frontend loads at http://localhost:5173
- [ ] Can navigate between pages
- [ ] Registration form appears
- [ ] Login form appears
- [ ] Search page loads
- [ ] No console errors

**If frontend has errors:** STOP and fix them before deploying. Report errors for assistance.

---

## 📋 Pre-Deployment Requirements

### 1. Get a Server (15 mins)

**Recommended Providers:**
- **DigitalOcean** - $24/month (2 CPU, 4GB RAM) - [Sign up](https://digitalocean.com)
- **Hetzner** - €9/month (2 CPU, 4GB RAM) - [Sign up](https://hetzner.com)
- **AWS Lightsail** - $20/month - [Sign up](https://aws.amazon.com/lightsail/)

**Minimum Specs:**
- 2 CPU cores
- 4GB RAM
- 50GB disk
- Ubuntu 22.04 LTS

**After creating server:**
- [ ] Note your server IP: `_______________`
- [ ] SSH access works: `ssh root@your-server-ip`

### 2. Get a Domain (10 mins)

**Domain Registrars:**
- Namecheap, GoDaddy, Google Domains, etc.

**DNS Setup:**
```
Type: A Record
Name: @
Value: your-server-ip

Type: A Record
Name: www
Value: your-server-ip
```

- [ ] Domain registered: `_______________`
- [ ] DNS configured (may take 5-60 minutes to propagate)

### 3. Get Stripe Keys (10 mins)

1. Create Stripe account: https://dashboard.stripe.com/register
2. Get your API keys: https://dashboard.stripe.com/test/apikeys

- [ ] Stripe Secret Key: `sk_test_...`
- [ ] Stripe Publishable Key: `pk_test_...`

**Note:** Use test keys initially. Switch to live keys after testing.

### 4. Get Email SMTP (10 mins)

**Option A: Gmail (Easiest)**
1. Enable 2FA on Gmail account
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use credentials:
   - SMTP_HOST: `smtp.gmail.com`
   - SMTP_PORT: `587`
   - SMTP_USER: `your-email@gmail.com`
   - SMTP_PASSWORD: `your-16-char-app-password`

**Option B: SendGrid (Professional)**
1. Sign up: https://sendgrid.com
2. Get API key
3. Free tier: 100 emails/day

- [ ] SMTP configured

---

## 🚀 Deployment Steps

### Step 1: Server Setup (30 mins)

SSH into your server:
```bash
ssh root@your-server-ip
```

Run these commands:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Clone repository
git clone https://github.com/dmankovsky/handwerker-platform.git /opt/handwerker
cd /opt/handwerker

# Verify files
ls -la
```

- [ ] Server updated
- [ ] Docker installed
- [ ] Repository cloned

### Step 2: Configuration (20 mins)

Create production environment file:
```bash
cd /opt/handwerker
cp .env.production.example .env
nano .env
```

**Fill in these values:**
```bash
# Database (generate strong passwords!)
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD
REDIS_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=PASTE_32_CHAR_RANDOM_STRING_HERE

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=noreply@your-domain.com

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Domain (UPDATE AFTER SSL SETUP)
VITE_API_URL=http://your-server-ip/api
VITE_WS_URL=ws://your-server-ip/ws
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

Save and exit (Ctrl+X, Y, Enter)

- [ ] .env file created and configured

### Step 3: Build and Deploy (20 mins)

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Look for:**
- ✅ All containers show "Up"
- ✅ No error messages in logs
- ✅ Backend: "Application startup complete"
- ✅ Frontend: nginx started

Press Ctrl+C to stop viewing logs

- [ ] Containers running
- [ ] Migrations completed
- [ ] No errors in logs

**Test basic connectivity:**
```bash
# Test backend API
curl http://localhost:8001/health

# Should return: {"status":"healthy"}
```

- [ ] Backend responds

### Step 4: Nginx Reverse Proxy (30 mins)

```bash
# Install Nginx
apt install nginx -y

# Create configuration
nano /etc/nginx/sites-available/handwerker
```

Paste this configuration (replace `your-domain.com`):
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

    # Health check
    location /health {
        proxy_pass http://localhost:8001/health;
    }
}
```

Save and activate:
```bash
# Enable site
ln -s /etc/nginx/sites-available/handwerker /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Enable on boot
systemctl enable nginx
```

**Test in browser:**
- Open http://your-domain.com (or http://your-server-ip)
- You should see the Handwerker Platform homepage

- [ ] Nginx configured
- [ ] Site accessible

### Step 5: SSL Certificate (30 mins)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace your-domain.com)
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow prompts:
- Enter email: `your-email@gmail.com`
- Agree to terms: `Y`
- Share email: `N` (optional)
- Redirect HTTP to HTTPS: `2` (Yes)

**Test:**
- Open https://your-domain.com
- Should see 🔒 padlock icon

- [ ] SSL certificate installed
- [ ] HTTPS working

### Step 6: Update Frontend with HTTPS URLs (10 mins)

```bash
cd /opt/handwerker
nano .env
```

Update these lines:
```bash
VITE_API_URL=https://your-domain.com/api
VITE_WS_URL=wss://your-domain.com/ws
```

Rebuild frontend with new URLs:
```bash
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

- [ ] Frontend rebuilt with HTTPS URLs

### Step 7: Create Admin Account (5 mins)

```bash
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@your-domain.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User",
    "phone": "+49123456789",
    "role": "homeowner"
  }'
```

**Save credentials:**
- Email: `admin@your-domain.com`
- Password: `SecurePassword123!`

- [ ] Admin account created

---

## ✅ Pre-Launch Testing (30 mins)

Test each feature on https://your-domain.com:

### Authentication
- [ ] Can register new homeowner account
- [ ] Can register new craftsman account
- [ ] Can login with credentials
- [ ] Can logout
- [ ] Receive welcome email

### Search & Discovery
- [ ] Search page loads
- [ ] Can view craftsman profiles
- [ ] Filters work

### Bookings
- [ ] Can create a booking request
- [ ] Craftsman receives email notification
- [ ] Can accept booking (as craftsman)
- [ ] Can view booking details

### Payments
- [ ] "Pay Now" button appears on confirmed booking
- [ ] Payment page loads
- [ ] Stripe form appears
- [ ] Can complete test payment (use card: 4242 4242 4242 4242)
- [ ] Redirects to success page
- [ ] Payment status updates

### Messaging
- [ ] Can send messages
- [ ] Can receive messages
- [ ] Unread count updates

### Profile
- [ ] Can view profile
- [ ] Can edit craftsman profile
- [ ] Can update trades and service areas

### Reviews
- [ ] Can leave review after completed booking
- [ ] Reviews appear on craftsman profile
- [ ] Craftsman can respond to reviews

---

## 🔧 Post-Launch Setup

### 1. Database Backups (15 mins)

```bash
# Create backup script
mkdir -p /opt/backups
nano /opt/scripts/backup-db.sh
```

Paste:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose -f /opt/handwerker/docker-compose.prod.yml exec -T postgres pg_dump -U handwerker_user handwerker_prod | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz
find $BACKUP_DIR -type f -mtime +30 -delete
```

Make executable and schedule:
```bash
chmod +x /opt/scripts/backup-db.sh

# Add to cron (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /opt/scripts/backup-db.sh
```

- [ ] Backups configured

### 2. Monitoring (15 mins)

```bash
# Create health check script
nano /opt/scripts/health-check.sh
```

Paste:
```bash
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/health)
if [ $RESPONSE -ne 200 ]; then
    echo "Health check failed! Response: $RESPONSE" | mail -s "Handwerker Platform Alert" your-email@gmail.com
fi
```

```bash
chmod +x /opt/scripts/health-check.sh

# Run every 5 minutes
crontab -e
# Add line:
*/5 * * * * /opt/scripts/health-check.sh
```

- [ ] Health checks configured

### 3. Firewall (10 mins)

```bash
# Configure firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

- [ ] Firewall enabled

---

## 🎉 Launch!

Your platform is now live at **https://your-domain.com**

### Next Steps:

1. **Switch to Stripe Live Mode** (when ready for real payments)
   - Get live keys from Stripe dashboard
   - Update .env with live keys
   - Rebuild: `docker-compose -f docker-compose.prod.yml build`
   - Restart: `docker-compose -f docker-compose.prod.yml up -d`

2. **Create Test Data**
   - Register several craftsman accounts
   - Fill out profiles with real-looking data
   - Add profile pictures (upcoming feature)

3. **Marketing**
   - Add Google Analytics
   - Submit to search engines
   - Create social media accounts

4. **Legal**
   - Add Privacy Policy
   - Add Terms of Service
   - Add Cookie Consent (GDPR)

---

## 🆘 Troubleshooting

### Frontend not loading
```bash
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml restart frontend
```

### Backend API errors
```bash
docker-compose -f docker-compose.prod.yml logs backend
# Check .env file for correct values
```

### Database connection errors
```bash
docker-compose -f docker-compose.prod.yml logs postgres
docker-compose -f docker-compose.prod.yml restart postgres
```

### Email not sending
- Verify Gmail App Password
- Check spam folder
- View logs: `docker-compose -f docker-compose.prod.yml logs backend | grep email`

### SSL certificate issues
```bash
certbot renew --dry-run
systemctl status certbot.timer
```

### Check all services
```bash
docker-compose -f docker-compose.prod.yml ps
docker stats
```

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Review DEPLOYMENT.md for detailed troubleshooting
3. Report specific error messages for assistance

---

**Deployment Time Estimate:**
- Server setup: 30 mins
- Configuration: 20 mins
- Build & deploy: 20 mins
- Nginx setup: 30 mins
- SSL: 30 mins
- Testing: 30 mins
- Post-launch: 40 mins

**Total: 3-4 hours** (first time)
**Total: 1-2 hours** (subsequent deployments)
