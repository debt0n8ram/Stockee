#!/bin/bash

# Stockee - AI-Powered Stock & Crypto Trading Simulator
# Startup script for development environment

echo "🚀 Starting Stockee Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys before starting the application."
    echo "   Required API keys:"
    echo "   - OPENAI_API_KEY (for ChatGPT integration)"
    echo "   - ALPHA_VANTAGE_API_KEY (for stock data)"
    echo "   - POLYGON_API_KEY (for additional market data)"
    echo ""
    read -p "Press Enter to continue after adding your API keys..."
fi

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ Stockee is now running!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🗄️  Database:"
echo "   PostgreSQL: localhost:5432"
echo "   Database: stockee"
echo "   Username: stockee_user"
echo "   Password: stockee_password"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Start trading with the simulated portfolio"
echo "   3. Try the AI assistant for insights"
echo "   4. Explore the analytics dashboard"
echo ""
echo "Happy trading! 📈"
