#!/bin/bash

# Center Deep Installation Script
echo "🦄 Installing Center Deep - You can't get deeper than Center Deep!"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. You can customize it if needed."
else
    echo "✅ .env file already exists."
fi

# Create data directory for logs
mkdir -p data

# Stop any existing containers
echo "🧹 Cleaning up any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start Center Deep (without cache)
echo "🚀 Building and starting Center Deep (fresh build without cache)..."
docker-compose build --no-cache
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "🎉 Center Deep is now running!"
    echo "🌐 Open http://localhost:8888 in your browser"
    echo "🌐 Also available at http://0.0.0.0:8888"
    echo ""
    echo "🦄 Dive deep into the web with privacy and magic!"
    echo ""
    echo "To stop Center Deep: docker-compose down"
    echo "To restart Center Deep: docker-compose up -d"
    echo "To view logs: docker-compose logs -f center-deep"
else
    echo "❌ Something went wrong. Check the logs with: docker-compose logs"
    exit 1
fi