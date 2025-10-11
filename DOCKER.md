# 🐳 Docker Deployment Guide

This guide covers how to run the Idle Clans Profit Optimizer using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### 1. Clone the Repository
```bash
git clone https://github.com/And0r-/Idle-Clans-Economy-Efficiency.git
cd Idle-Clans-Economy-Efficiency
```

### 2. Simple Deployment
```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at: **http://localhost:5000**

## 📋 Deployment Options

### Option 1: Simple Flask App Only
```bash
docker-compose up -d idle-clans-optimizer
```
- Runs on port `5000`
- Direct access to Flask application

### Option 2: Production with Nginx Reverse Proxy
```bash
docker-compose --profile production up -d
```
- Nginx on port `80` (http://localhost)
- Flask app behind reverse proxy
- Better for production use
- Includes gzip compression and security headers

### Option 3: Development Mode
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```
- Development environment with code mounting
- Auto-reload on code changes
- Debug mode enabled
- Runs on port `5001`

## 🔧 Configuration

### Environment Variables
You can customize the deployment by setting these environment variables:

```bash
# Example with custom settings
FLASK_ENV=production docker-compose up -d
```

### Volume Mounting
The `data/` directory is mounted read-only to ensure data persistence:
```yaml
volumes:
  - ./data:/app/data:ro
```

## 📊 Monitoring

### Health Checks
The application includes built-in health checks:

```bash
# Check application status
curl http://localhost:5000/status

# Check health via Docker
docker-compose ps
```

### Logs
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs idle-clans-optimizer
```

## 🔒 Security Features

- **Non-root user**: Application runs as `appuser`
- **Security headers**: Added via Nginx (when using production profile)
- **No admin endpoints**: No force-refresh or admin functionality
- **Rate limiting**: Built into the background scheduler

## 🛠️ Maintenance

### Update the Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove images and volumes
docker-compose down --rmi all --volumes
```

## 🚀 Production Deployment

For production deployment, consider:

1. **Use the nginx profile**:
   ```bash
   docker-compose --profile production up -d
   ```

2. **Set proper environment variables**:
   ```bash
   echo "FLASK_ENV=production" > .env
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats
   ```

4. **Set up log rotation** for long-running deployments

5. **Use a reverse proxy** like nginx for SSL termination

## 📱 Mobile & Responsive

The web interface is fully responsive and works on:
- 📱 Mobile devices
- 💻 Tablets
- 🖥️ Desktop computers

## 🔄 Automatic Updates

The application automatically fetches new market data every **15 minutes** in the background, so no manual intervention is needed.

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Use different port
   docker-compose -p idle-clans-alt up -d
   ```

2. **Permission denied**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER .
   ```

3. **Build fails**:
   ```bash
   # Clean build
   docker-compose build --no-cache
   ```

4. **API connection issues**:
   - Check internet connection
   - Verify Idle Clans API is accessible
   - Check application logs: `docker-compose logs`

### Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify all files are present
3. Ensure Docker and Docker Compose are up to date
4. Check the application health: `curl http://localhost:5000/status`

---

Happy optimizing! 🏆