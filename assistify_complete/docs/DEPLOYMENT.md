# Assistify Deployment Guide

Complete guide for deploying Assistify to production.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] ML models trained and saved
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Backup strategy in place
- [ ] Monitoring setup complete

## Windows Deployment

### Option 1: Windows Server with IIS

#### 1. Install Dependencies
```powershell
# Install Python
choco install python nodejs postgresql redis

# Install Python packages
pip install -r backend/requirements.txt
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

#### 2. Configure IIS
```powershell
# Install IIS
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer

# Install URL Rewrite
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite

# Install Application Request Routing (ARR)
# Download from: https://www.iis.net/downloads/microsoft/application-request-routing
```

#### 3. Deploy Django
```powershell
# Create IIS application pool
New-WebAppPool -Name "Assistify" -RuntimeVersion "No Managed Code"

# Create IIS website
New-Website -Name "Assistify" -PhysicalPath "C:\assistify\backend" -Port 8000
```

#### 4. Configure WSGI
```powershell
# Install FastCGI
pip install waitress

# Create startup script
# C:\assistify\backend\run_server.bat
@echo off
cd C:\assistify\backend
waitress-serve --port=8000 assistify.wsgi:application
```

### Option 2: Docker on Windows

#### 1. Install Docker
```powershell
choco install docker-desktop
```

#### 2. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "assistify.wsgi:application"]
```

#### 3. Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: assistify
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/assistify
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

#### 4. Deploy with Docker
```powershell
docker-compose up -d
```

## Linux Deployment (Ubuntu/Debian)

### Option 1: Manual Deployment

#### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip nodejs postgresql postgresql-contrib redis-server nginx
```

#### 2. Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/yourusername/assistify.git
cd assistify
```

#### 3. Setup Python Environment
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

#### 4. Setup Database
```bash
sudo -u postgres psql
\i config/database.sql
\q
```

#### 5. Configure Django
```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 6. Setup Gunicorn
```bash
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/assistify.service
```

**Content:**
```ini
[Unit]
Description=Assistify Django Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/assistify/backend
ExecStart=/var/www/assistify/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    assistify.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 7. Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable assistify
sudo systemctl start assistify
```

#### 8. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/assistify
```

**Content:**
```nginx
upstream assistify {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /var/www/assistify/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/assistify/backend/media/;
    }

    location / {
        proxy_pass http://assistify;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 9. Enable Nginx
```bash
sudo ln -s /etc/nginx/sites-available/assistify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 10. Setup SSL with Let's Encrypt
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Option 2: Docker Deployment

#### 1. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### 2. Deploy with Docker Compose
```bash
cd /var/www/assistify
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### 1. Create EC2 Instance
```bash
# Launch Ubuntu 22.04 LTS instance
# Security group: Allow HTTP (80), HTTPS (443), SSH (22)
```

#### 2. Install and Deploy
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
cd /home/ubuntu
git clone https://github.com/yourusername/assistify.git
cd assistify

# Follow Linux deployment steps above
```

#### 3. Setup RDS Database
```bash
# Create PostgreSQL RDS instance
# Update DATABASE_URL in .env
```

#### 4. Setup ElastiCache
```bash
# Create Redis cluster
# Update REDIS_URL in .env
```

#### 5. Setup S3 for Media
```bash
# Create S3 bucket
# Configure AWS credentials in .env
```

### Google Cloud Deployment

#### 1. Create Compute Engine Instance
```bash
gcloud compute instances create assistify \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a
```

#### 2. Deploy Application
```bash
gcloud compute ssh assistify
# Follow Linux deployment steps
```

#### 3. Setup Cloud SQL
```bash
gcloud sql instances create assistify-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro
```

### Heroku Deployment

#### 1. Install Heroku CLI
```bash
npm install -g heroku
heroku login
```

#### 2. Create Heroku App
```bash
heroku create assistify-app
```

#### 3. Add Buildpacks
```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs
```

#### 4. Configure Environment
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=your-database-url
```

#### 5. Deploy
```bash
git push heroku main
heroku run python backend/manage.py migrate
```

## Post-Deployment

### 1. Verify Deployment
```bash
# Test API
curl https://yourdomain.com/api/health/

# Check logs
tail -f /var/log/assistify/error.log
```

### 2. Setup Monitoring
```bash
# Install monitoring tools
pip install prometheus-client
pip install grafana-api
```

### 3. Setup Backups
```bash
# Database backup
pg_dump assistify > backup.sql

# Automated backup script
sudo nano /etc/cron.daily/assistify-backup
```

**Content:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/assistify"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump assistify | gzip > $BACKUP_DIR/assistify_$DATE.sql.gz
```

### 4. Setup Logging
```bash
# Configure centralized logging
# Use ELK stack or CloudWatch
```

### 5. Performance Tuning
```bash
# Database optimization
VACUUM ANALYZE;

# Cache optimization
redis-cli FLUSHALL

# Model optimization
# Quantize models for faster inference
```

## Troubleshooting

### Application Won't Start
```bash
# Check logs
journalctl -u assistify -n 50

# Check database connection
python manage.py dbshell

# Check environment variables
env | grep ASSISTIFY
```

### High Memory Usage
```bash
# Reduce Gunicorn workers
# Optimize ML models
# Enable model quantization
```

### Slow Response Times
```bash
# Enable caching
# Optimize database queries
# Use CDN for static files
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection pool
psql -c "SELECT * FROM pg_stat_activity;"
```

## Maintenance

### Regular Tasks
- [ ] Monitor disk space
- [ ] Update dependencies
- [ ] Backup database
- [ ] Review logs
- [ ] Monitor performance
- [ ] Update SSL certificates

### Monthly Tasks
- [ ] Update system packages
- [ ] Retrain ML models
- [ ] Review analytics
- [ ] Optimize database

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Disaster recovery test

## Scaling

### Horizontal Scaling
```bash
# Add more Gunicorn workers
gunicorn --workers 8 assistify.wsgi:application

# Add load balancer
# Configure Nginx upstream
```

### Vertical Scaling
```bash
# Increase server resources
# Upgrade instance type
# Increase database resources
```

### Database Scaling
```bash
# Enable read replicas
# Implement sharding
# Optimize queries
```

## Rollback Procedure

If deployment fails:

```bash
# Rollback to previous version
git revert HEAD
git push heroku main

# Or restore from backup
pg_restore -d assistify backup.sql
```

## Support

For deployment issues, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Gunicorn Documentation: https://gunicorn.org/
- Nginx Documentation: https://nginx.org/
- Docker Documentation: https://docs.docker.com/
