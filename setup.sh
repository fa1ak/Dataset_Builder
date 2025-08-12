#!/bin/bash

echo "🚀 Setting up Dataset Processor Tool..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create data directory for user files
mkdir -p data
echo "✅ Created data directory for your files"

# Create exports directory
mkdir -p exports
echo "✅ Created exports directory for results"

echo ""
echo "🎯 Setup complete! To start the tool:"
echo "   docker-compose up --build"
echo ""
echo "📁 Place your documents in the 'data' folder"
echo "📤 Results will be saved in the 'exports' folder"
echo "🌐 Access the tool at: http://localhost:8000"
