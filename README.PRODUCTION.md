# 🚀 Dataset Processor - Production Deployment Guide

This guide will help you deploy the Dataset Processor to production with a domain, database, and proper infrastructure.

## 📋 **Prerequisites**

### **1. Server Requirements**
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB+ (8GB+ recommended)
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ or similar Linux distribution

### **2. Domain & DNS**
- Domain name (e.g., `your-domain.com`)
- DNS access to point domain to your server
- SSL certificate (Let's Encrypt recommended)

### **3. Server Setup**
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

# Logout and login to apply Docker group changes
```

## 🚀 **Step-by-Step Deployment**

### **Step 1: Clone and Setup**
```bash
# Clone your repository
git clone https://github.com/yourusername/DatasetBuilder.git
cd DatasetBuilder

# Make deployment script executable
chmod +x deploy.sh
```

### **Step 2: Configure Environment**
```bash
# Copy environment template
cp env.prod.example .env

# Edit configuration
nano .env
```

**Important Configuration Values:**
```bash
# Database
POSTGRES_PASSWORD=your_very_secure_password_here
DATABASE_URL=postgresql://postgres:your_very_secure_password_here@db:5432/dataset_processor

# Security (CRITICAL - Change these!)
SECRET_KEY=your_super_secret_key_here_change_this_in_production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Monitoring
GRAFANA_PASSWORD=your_grafana_password_here
```

### **Step 3: Configure Domain**
```bash
# Edit nginx configuration
nano nginx.conf
```

**Update the server block:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # ... rest of configuration
}
```

### **Step 4: Deploy Application**
```bash
# Run deployment script
./deploy.sh
```

### **Step 5: Setup SSL Certificate**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### **Step 6: Configure Firewall**
```bash
# Enable UFW
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Application (if needed)
```

## 🔧 **Production Configuration**

### **Database Setup**
The application automatically creates the database schema. You can also manually initialize:

```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d dataset_processor

# Check tables
\dt

# Exit
\q
```

### **Monitoring Setup**
1. **Prometheus**: http://your-domain.com:9090
2. **Grafana**: http://your-domain.com:3000
   - Username: `admin`
   - Password: (from your .env file)

### **Backup Strategy**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres dataset_processor > $BACKUP_DIR/db_backup_$DATE.sql

# Backup exports
tar -czf $BACKUP_DIR/exports_backup_$DATE.tar.gz exports/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Check application health
curl http://your-domain.com/health

# Check all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### **Performance Monitoring**
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and alerts
- **Nginx**: Access logs and error logs

### **Scaling**
```bash
# Scale application (if needed)
docker-compose -f docker-compose.prod.yml up --scale dataset-processor=3 -d
```

## 🔒 **Security Best Practices**

### **1. Environment Security**
- Use strong, unique passwords
- Rotate secrets regularly
- Never commit `.env` files to git

### **2. Network Security**
- Use HTTPS only
- Configure proper CORS
- Implement rate limiting
- Use firewall rules

### **3. Application Security**
- Regular security updates
- Monitor for vulnerabilities
- Implement proper logging
- Use secure headers

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs dataset-processor

# Check database connection
docker-compose -f docker-compose.prod.yml exec dataset-processor python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Check database logs
docker-compose -f docker-compose.prod.yml logs db
```

#### **File Upload Issues**
```bash
# Check file permissions
ls -la exports/
ls -la data/

# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### **Performance Issues**
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d dataset_processor -c "SELECT * FROM pg_stat_activity;"
```

## 📈 **Scaling for High Traffic**

### **Horizontal Scaling**
```yaml
# In docker-compose.prod.yml
services:
  dataset-processor:
    # ... existing config
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### **Load Balancing**
```nginx
# In nginx.conf
upstream dataset_processor {
    server dataset-processor-1:8000;
    server dataset-processor-2:8000;
    server dataset-processor-3:8000;
}
```

## 🎯 **Production Checklist**

- [ ] Domain configured and pointing to server
- [ ] SSL certificate installed and auto-renewing
- [ ] Environment variables configured securely
- [ ] Database backups scheduled
- [ ] Monitoring and alerting configured
- [ ] Firewall rules configured
- [ ] Rate limiting configured
- [ ] Log rotation configured
- [ ] Security headers configured
- [ ] Performance testing completed
- [ ] Documentation updated
- [ ] Team access configured

## 📞 **Support**

If you encounter issues:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify configuration: `docker-compose -f docker-compose.prod.yml config`
3. Check service health: `curl http://your-domain.com/health`
4. Review this documentation
5. Check GitHub issues

## 🎉 **Success!**

Your Dataset Processor is now running in production! Users can:
- Upload documents via the API
- Process various file formats
- Export structured data
- Monitor processing status
- Access processed results

**API Endpoints:**
- `POST /api/process` - Upload and process documents
- `GET /api/jobs` - List processing jobs
- `GET /api/job/{id}` - Get job details
- `GET /api/job/{id}/export` - Export job data
- `GET /api/stats` - Get processing statistics
