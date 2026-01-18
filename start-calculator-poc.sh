#!/bin/bash

# Calculator POC Startup Script

set -e

echo "🚀 Starting Calculator POC..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    echo "❌ Error: docker compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start services
echo "📦 Building and starting services..."
docker compose -f docker-compose.calculator-poc.yml up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

# Check Redis
if docker compose -f docker-compose.calculator-poc.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "⚠️  Redis is not responding"
fi

# Check Scheduler
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Scheduler is healthy"
else
    echo "⚠️  Scheduler is not responding"
fi

# Check Calculation Agent
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Calculation Agent is healthy"
else
    echo "⚠️  Calculation Agent is not responding"
fi

# Check Formatting Agent
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Formatting Agent is healthy"
else
    echo "⚠️  Formatting Agent is not responding"
fi

echo ""
echo "🎉 Calculator POC is running!"
echo ""
echo "📍 Access points:"
echo "   - Web UI:            http://localhost:5173"
echo "   - Scheduler API:     http://localhost:8000"
echo "   - API Docs:          http://localhost:8000/docs"
echo "   - Calculation Agent: http://localhost:8001"
echo "   - Formatting Agent:  http://localhost:8002"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:         docker compose -f docker-compose.calculator-poc.yml logs -f"
echo "   - Stop services:     docker compose -f docker-compose.calculator-poc.yml down"
echo "   - Restart services:  docker compose -f docker-compose.calculator-poc.yml restart"
echo ""
echo "📖 For more information, see docs/CALCULATOR_POC.md"

