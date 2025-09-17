#!/bin/bash

# BTW Games Setup Script
# This script sets up the Flask gaming platform

set -e  # Exit on any error

echo "🎮 BTW Games Setup Script"
echo "========================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Docker is available
DOCKER_AVAILABLE=false
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    DOCKER_AVAILABLE=true
fi

echo "🔍 Environment Check:"
echo "   Python: $(python3 --version)"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "   Docker: $(docker --version)"
    echo "   Docker Compose: $(docker-compose --version)"
else
    echo "   Docker: Not available"
fi
echo ""

# Ask user for setup type
echo "🛠️ Setup Options:"
echo "1. Local Development Setup (Python virtual environment)"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "2. Docker Development Setup"
    echo "3. Docker Production Setup"
fi
echo ""

read -p "Choose setup type (1$([ "$DOCKER_AVAILABLE" = true ] && echo "/2/3")): " SETUP_TYPE

case $SETUP_TYPE in
    1)
        echo "🔧 Setting up local development environment..."

        # Create virtual environment
        echo "📦 Creating virtual environment..."
        python3 -m venv venv

        # Activate virtual environment
        echo "🔄 Activating virtual environment..."
        source venv/bin/activate

        # Install dependencies
        echo "📚 Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt

        # Set up environment file
        if [ ! -f .env.local ]; then
            echo "⚙️ Creating environment configuration..."
            cat > .env.local << EOF
DATABASE_URL=sqlite:///btw_games.db
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
GOOGLE_ANALYTICS_ID=G-SM7PBYVK97
GOOGLE_ADSENSE_CLIENT=ca-pub-8930741225505243
EOF
            cp .env.local .env
        fi

        # Initialize database
        echo "🗄️ Initializing database..."
        python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

        # Seed database
        echo "🌱 Seeding database with sample data..."
        python3 seed_data.py

        echo ""
        echo "✅ Local development setup complete!"
        echo ""
        echo "🚀 To start the development server:"
        echo "   source venv/bin/activate"
        echo "   python run.py"
        echo ""
        echo "🌐 The application will be available at: http://localhost:5000"
        echo "🔧 Admin panel: http://localhost:5000/admin"
        echo "📡 API documentation: http://localhost:5000/api"
        ;;

    2)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo "❌ Docker is not available. Please install Docker and Docker Compose."
            exit 1
        fi

        echo "🐳 Setting up Docker development environment..."

        # Create development environment file
        if [ ! -f .env ]; then
            echo "⚙️ Creating environment configuration..."
            cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:///data/btw_games.db
GOOGLE_ANALYTICS_ID=G-SM7PBYVK97
GOOGLE_ADSENSE_CLIENT=ca-pub-8930741225505243
EOF
        fi

        # Build and start services
        echo "🏗️ Building Docker images..."
        docker-compose build

        echo "🚀 Starting services..."
        docker-compose up -d

        # Wait for database to be ready
        echo "⏳ Waiting for database to be ready..."
        sleep 10

        # Initialize database
        echo "🗄️ Initializing database..."
        docker-compose exec web python seed_data.py

        echo ""
        echo "✅ Docker development setup complete!"
        echo ""
        echo "🌐 The application is available at: http://localhost"
        echo "🔧 Admin panel: http://localhost/admin"
        echo "📡 API: http://localhost/api"
        echo ""
        echo "🐳 Docker commands:"
        echo "   View logs: docker-compose logs -f"
        echo "   Stop services: docker-compose down"
        echo "   Restart: docker-compose restart"
        ;;

    3)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo "❌ Docker is not available. Please install Docker and Docker Compose."
            exit 1
        fi

        echo "🏭 Setting up Docker production environment..."

        # Check for required environment variables
        echo "⚙️ Production environment setup..."

        if [ ! -f .env.production ]; then
            echo "📝 Creating production environment template..."
            cat > .env.production << EOF
FLASK_ENV=production
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_SECRET_KEY
DATABASE_URL=sqlite:///data/btw_games.db
GOOGLE_ANALYTICS_ID=YOUR_GA_ID
GOOGLE_ADSENSE_CLIENT=YOUR_ADSENSE_CLIENT
EOF
            echo "⚠️ Please edit .env.production with your production values!"
            read -p "Press Enter after editing .env.production..."
        fi

        # Copy production environment
        cp .env.production .env

        # Build and start production services
        echo "🏗️ Building production Docker images..."
        docker-compose -f docker-compose.yml build

        echo "🚀 Starting production services..."
        docker-compose -f docker-compose.yml up -d

        # Wait for services
        echo "⏳ Waiting for services to be ready..."
        sleep 15

        # Initialize database
        echo "🗄️ Initializing production database..."
        docker-compose exec web python seed_data.py

        echo ""
        echo "✅ Docker production setup complete!"
        echo ""
        echo "🌐 The application is available at: http://localhost"
        echo "🔐 Don't forget to:"
        echo "   - Set up SSL certificates"
        echo "   - Configure domain name"
        echo "   - Set up monitoring"
        echo "   - Configure backups"
        ;;

    *)
        echo "❌ Invalid option selected."
        exit 1
        ;;
esac

echo ""
echo "📚 Additional Information:"
echo "   - Admin API Key: admin-api-key-change-in-production"
echo "   - Sample games are pre-loaded"
echo "   - Check README.md for detailed documentation"
echo ""
echo "🎉 Setup completed successfully!"