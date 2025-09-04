#!/bin/bash

# Production Deployment Script for Dataset Processor
# This script sets up the production environment

set -e  # Exit on any error

echo "🚀 Starting Dataset Processor Production Deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.prod.example .env
    echo "⚠️  Please edit .env file with your actual configuration values before continuing."
    echo "   Important: Change the SECRET_KEY and POSTGRES_PASSWORD!"
    read -p "Press Enter after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p exports
mkdir -p data
mkdir -p ssl
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 exports
chmod 755 data
chmod 755 ssl
chmod 755 logs

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Your Dataset Processor is now available at:"
    echo "   - API: http://localhost:8000"
    echo "   - Health Check: http://localhost:8000/health"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitoring:"
    echo "   - Prometheus: http://localhost:9090"
    echo "   - Grafana: http://localhost:3000 (admin/your_grafana_password)"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Configure your domain name in nginx.conf"
    echo "   2. Set up SSL certificates in ssl/ directory"
    echo "   3. Update ALLOWED_HOSTS in .env file"
    echo "   4. Configure monitoring and alerting"
    echo ""
    echo "🔧 Useful commands:"
    echo "   - View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   - Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "   - Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo "   - Update services: docker-compose -f docker-compose.prod.yml up --build -d"
else
    echo "❌ Application failed to start. Check logs with:"
    echo "   docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
