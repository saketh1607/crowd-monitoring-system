# Emergency Management System - Deployment Guide

This guide provides step-by-step instructions for deploying the Emergency Management System in different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Google Colab Model Training](#google-colab-model-training)
6. [Configuration](#configuration)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB minimum for data and models
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows 10+

### Software Dependencies
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd emergency-management-system
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Install PostgreSQL locally or use Docker
docker run --name emergency_postgres \
  -e POSTGRES_DB=emergency_db \
  -e POSTGRES_USER=emergency_user \
  -e POSTGRES_PASSWORD=emergency_pass \
  -p 5432:5432 -d postgres:15

# Setup database schema and sample data
python scripts/setup_database.py
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### 5. Start API Server
```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Dashboard
```bash
# Navigate to dashboard directory
cd src/dashboard

# Install dependencies
npm install

# Start development server
npm start
```

The system will be available at:
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Docker Deployment

### 1. Build and Start Services
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 2. Initialize Database
```bash
# Run database setup inside container
docker-compose exec api python scripts/setup_database.py
```

### 3. Access Services
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Stop Services
```bash
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v
```

## Production Deployment

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Security Configuration
```bash
# Create production environment file
cp .env.example .env.production

# Generate secure secrets
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 16  # For database passwords
```

### 3. SSL/TLS Setup
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/emergency.key \
  -out nginx/ssl/emergency.crt

# For production, use Let's Encrypt:
# sudo certbot --nginx -d yourdomain.com
```

### 4. Production Docker Compose
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 5. Backup Strategy
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose exec postgres pg_dump -U emergency_user emergency_db > \
  $BACKUP_DIR/emergency_db_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "emergency_db_*.sql" -mtime +7 -delete
```

## Google Colab Model Training

### 1. Upload Notebook
1. Open Google Colab (https://colab.research.google.com)
2. Upload `notebooks/Emergency_Detection_Training.ipynb`
3. Enable GPU runtime: Runtime → Change runtime type → GPU

### 2. Run Training
```python
# The notebook will automatically:
# 1. Install required packages
# 2. Generate synthetic training data
# 3. Train all ML models
# 4. Save trained models for download
```

### 3. Download Trained Models
After training completes, download these files:
- `fire_detection_model.h5`
- `crowd_density_model.h5`
- `behavior_analysis_model.pkl`
- `behavior_label_encoder.pkl`
- `behavior_scaler.pkl`
- Sensor anomaly models (4 files each for temperature, humidity, sound, motion)

### 4. Deploy Models
```bash
# Create models directory
mkdir -p data/models

# Copy downloaded models
cp ~/Downloads/*_model.* data/models/
cp ~/Downloads/*_encoder.pkl data/models/
cp ~/Downloads/*_scaler.pkl data/models/

# Update model paths in config/settings.py
MODEL_PATH = "data/models"
```

## Configuration

### Environment Variables
```bash
# Application
APP_NAME=Emergency Management System
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/emergency_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
WEATHER_API_KEY=your-weather-api-key
TWITTER_API_KEY=your-twitter-api-key

# Notification
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
EMERGENCY_CONTACTS=+1234567890,+0987654321
```

### Model Configuration
```python
# config/settings.py
MODEL_CONFIGS = {
    "fire_detection": {
        "model_path": "data/models/fire_detection_model.h5",
        "confidence_threshold": 0.7
    },
    "crowd_density": {
        "model_path": "data/models/crowd_density_model.h5",
        "density_thresholds": {"low": 1.0, "medium": 2.5, "high": 4.0}
    }
}
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# API health check
curl http://localhost:8000/health

# Database connection check
docker-compose exec postgres pg_isready -U emergency_user

# Redis check
docker-compose exec redis redis-cli ping
```

### 2. Log Monitoring
```bash
# View application logs
docker-compose logs -f api

# View specific service logs
docker-compose logs -f dashboard
docker-compose logs -f postgres
```

### 3. Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Check disk usage
df -h
du -sh data/

# Monitor database performance
docker-compose exec postgres psql -U emergency_user -d emergency_db -c "
SELECT schemaname,tablename,attname,n_distinct,correlation 
FROM pg_stats WHERE tablename='emergencies';"
```

### 4. Backup and Recovery
```bash
# Automated backup script
#!/bin/bash
# /etc/cron.daily/emergency-backup

BACKUP_DIR="/var/backups/emergency"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec postgres pg_dump -U emergency_user emergency_db | \
  gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Models backup
tar -czf $BACKUP_DIR/models_$DATE.tar.gz data/models/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### 5. Updates and Maintenance
```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Update dependencies
pip install -r requirements.txt --upgrade
cd src/dashboard && npm update

# Database migrations (if needed)
alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   
   # Reset database
   docker-compose down
   docker volume rm emergency_postgres_data
   docker-compose up -d postgres
   ```

2. **Model Loading Errors**
   ```bash
   # Check if model files exist
   ls -la data/models/
   
   # Verify model file integrity
   python -c "import tensorflow as tf; tf.keras.models.load_model('data/models/fire_detection_model.h5')"
   ```

3. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats --no-stream
   
   # Restart services if needed
   docker-compose restart api
   ```

4. **WebSocket Connection Issues**
   ```bash
   # Check if WebSocket endpoint is accessible
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws
   ```

For additional support, check the logs and refer to the API documentation at `/docs` endpoint.
