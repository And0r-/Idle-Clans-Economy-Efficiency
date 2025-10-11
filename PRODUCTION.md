# 🚀 Production Deployment Guide

This guide covers production-ready deployment of the Idle Clans Profit Optimizer.

## 🏗️ Production Setup

### 1. Server Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ free space
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### 2. Initial Setup

```bash
# Clone repository
git clone https://github.com/And0r-/Idle-Clans-Economy-Efficiency.git
cd Idle-Clans-Economy-Efficiency

# Create production environment file
cp .env.example .env
nano .env  # Edit configuration

# Create logs directory
mkdir -p logs

# Set proper permissions
chmod 755 logs
```

### 3. Environment Configuration

Edit `.env` file with production values:

```bash
# Production settings
FLASK_ENV=production
FLASK_DEBUG=false
DATA_UPDATE_INTERVAL_MINUTES=15
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-super-secret-production-key-here

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## 🚀 Deployment Options

### Option 1: Simple Production
```bash
docker-compose up -d
```
- Single container
- Direct access on port 5000
- Basic resource limits

### Option 2: Full Production with Nginx
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
- Multiple replicas for redundancy
- Nginx reverse proxy with SSL support
- Advanced rate limiting
- Production-optimized settings

### Option 3: Production with Monitoring
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile monitoring up -d
```
- Includes Watchtower for auto-updates
- Container monitoring

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw enable
```

### 2. SSL/HTTPS Setup (Recommended)

#### Using Let's Encrypt:
```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
sudo chown $USER:$USER ./ssl/*
```

#### Update nginx configuration:
```bash
# Edit nginx.prod.conf and uncomment SSL sections
nano nginx.prod.conf
```

### 3. Regular Updates
```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## 📊 Monitoring & Maintenance

### 1. Health Checks
```bash
# Check container status
docker-compose ps

# Check application health
curl http://localhost/status

# View logs
docker-compose logs -f
```

### 2. Log Management
```bash
# View application logs
tail -f logs/app.log

# View nginx logs (if using nginx profile)
docker-compose logs nginx

# Log rotation is automatic (configured in docker-compose.yml)
```

### 3. Performance Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
df -h
du -sh logs/

# Monitor nginx access patterns
tail -f logs/nginx/access.log | grep -v "200"
```

## 🔄 Updates & Maintenance

### 1. Application Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 2. Database Cleanup (if needed)
```bash
# The app doesn't use a database, but logs should be rotated
find logs/ -name "*.log" -mtime +30 -delete
```

### 3. Backup Strategy
```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env docker-compose*.yml nginx*.conf

# No database to backup - all data comes from API
```

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**:
   ```bash
   # Check logs
   docker-compose logs idle-clans-optimizer

   # Check disk space
   df -h
   ```

2. **High memory usage**:
   ```bash
   # Check resource limits in docker-compose.prod.yml
   # Consider reducing replicas or optimizing memory usage
   ```

3. **API rate limiting**:
   ```bash
   # Check logs for rate limit errors
   grep "rate" logs/app.log

   # Adjust DATA_UPDATE_INTERVAL_MINUTES if needed
   ```

4. **SSL certificate issues**:
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/cert.pem -text -noout

   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

## 📈 Performance Optimization

### 1. Resource Scaling
- Increase `replicas` in `docker-compose.prod.yml`
- Adjust memory/CPU limits based on usage
- Use external load balancer for high traffic

### 2. Caching Strategy
- Nginx serves static content with long cache headers
- Application caches market data for 15 minutes
- Consider adding Redis for session storage (if needed)

### 3. CDN Integration
- Use CloudFlare or similar CDN
- Configure nginx to set proper cache headers
- Enable gzip compression (already configured)

## 🌐 Domain & DNS Setup

1. **Point domain to server IP**:
   ```
   A record: your-domain.com -> your.server.ip.address
   ```

2. **Update nginx configuration**:
   ```bash
   # Edit nginx.prod.conf
   # Replace 'localhost' with 'your-domain.com'
   ```

3. **Enable HTTPS redirect**:
   ```bash
   # Uncomment HTTPS redirect section in nginx.prod.conf
   ```

## ✅ Production Checklist

Before going live:

- [ ] Environment variables configured (`.env`)
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Firewall configured
- [ ] Domain DNS pointing to server
- [ ] Health checks passing
- [ ] Logs directory created and writable
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Rate limiting tested
- [ ] Resource limits appropriate
- [ ] Security headers configured

## 📞 Support

For production issues:
1. Check application logs: `docker-compose logs`
2. Check system resources: `htop`, `df -h`
3. Verify API connectivity to Idle Clans
4. Check nginx configuration if using reverse proxy

---

Your Idle Clans Profit Optimizer is now production-ready! 🎉