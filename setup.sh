#!/bin/bash

echo "🚀 Setting up IT Operations Analytics MVP..."

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required but not installed."; exit 1; }

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Please edit .env file with your API keys before continuing"
else
    echo "✅ .env file already exists"
fi

# Build and start services
echo "🏗️  Building Docker services..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check services
echo "🔍 Checking service health..."
curl -f http://localhost:8000/health || echo "❌ Backend not ready"
curl -f http://localhost:3000 || echo "❌ Frontend not ready"

echo "✅ Setup complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo "   Database Admin: http://localhost:8080"
echo ""
echo "📚 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Visit http://localhost:3000 to see your dashboard"
echo "   3. Check API docs at http://localhost:8000/docs"
