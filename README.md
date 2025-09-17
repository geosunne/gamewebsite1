# BTW Games - Flask Gaming Platform

A modern web-based gaming platform built with Flask and featuring a complete frontend-backend separation architecture.

## 🚀 Features

### 🎮 **Game Management**
- Complete game library with categories and tags
- Game statistics and analytics
- Featured and new game sections
- Advanced search and filtering
- Game play tracking

### 🏗️ **Technical Architecture**
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: SQLite (lightweight, perfect for development and small-scale production)
- **Frontend**: Vanilla JavaScript with modern API calls
- **Deployment**: Docker containerization with Nginx reverse proxy
- **Caching**: Redis support for session management

### 📊 **Admin Features**
- Comprehensive admin dashboard
- Game and category management
- Real-time statistics and analytics
- Bulk operations support
- API-driven admin interface

### 🔧 **API Endpoints**
- RESTful API design
- Game CRUD operations
- Statistics and analytics endpoints
- Search and filtering capabilities
- Admin management endpoints

## 📁 Project Structure

```
gamewebsite1/
├── app.py                 # Flask application factory
├── models.py              # Database models and schemas
├── routes/
│   ├── api.py            # Public API endpoints
│   ├── admin.py          # Admin API endpoints
│   └── main.py           # Static file serving
├── static/               # Frontend files
│   ├── index.html        # Homepage
│   ├── games.html        # Games listing
│   ├── game.html         # Individual game page
│   ├── admin.html        # Admin dashboard
│   └── assets/
│       ├── js/
│       │   ├── api.js    # API client library
│       │   └── games-data.js
│       ├── css/
│       └── images/
├── requirements.txt      # Python dependencies
├── seed_data.py         # Database seeding script
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service setup
├── nginx.conf           # Nginx configuration
└── .env                 # Environment variables
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- SQLite (included with Python)
- Redis (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gamewebsite1
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   # Create database tables
   python init_db.py

   # Seed with sample data
   python seed_data.py
   ```

6. **Run the development server**
   ```bash
   python run.py
   ```

   Or use Flask's development server:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   flask run
   ```

### Docker Deployment

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database**
   ```bash
   docker-compose exec web python seed_data.py
   ```

The application will be available at:
- **Frontend**: http://localhost (via Nginx)
- **API**: http://localhost/api
- **Admin**: http://localhost/admin

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///btw_games.db` |
| `FLASK_ENV` | Environment mode | `development` |
| `GOOGLE_ANALYTICS_ID` | Google Analytics tracking ID | - |
| `GOOGLE_ADSENSE_CLIENT` | Google AdSense client ID | - |

### Database Configuration

For SQLite (recommended):
```bash
DATABASE_URL=sqlite:///btw_games.db
```

For PostgreSQL in production (optional):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/btw_games
```

## 📡 API Documentation

### Public API Endpoints

#### Games
- `GET /api/games` - List all games with filtering
- `GET /api/games/{id}` - Get specific game
- `GET /api/games/slug/{slug}` - Get game by slug
- `POST /api/games/{id}/play` - Record game play

#### Categories
- `GET /api/categories` - List all categories
- `GET /api/categories/{id}/games` - Get games by category

#### Search & Statistics
- `GET /api/search?q={query}` - Search games
- `GET /api/stats/games` - Overall game statistics
- `GET /api/stats/games/{id}` - Game-specific statistics

### Admin API Endpoints

All admin endpoints require `X-API-Key` header for authentication.

#### Game Management
- `GET /admin/games` - List all games (including inactive)
- `POST /admin/games` - Create new game
- `PUT /admin/games/{id}` - Update game
- `DELETE /admin/games/{id}` - Delete game (soft delete)

#### Category Management
- `GET /admin/categories` - List categories
- `POST /admin/categories` - Create category
- `PUT /admin/categories/{id}` - Update category
- `DELETE /admin/categories/{id}` - Delete category

#### Statistics
- `GET /admin/stats/dashboard` - Dashboard statistics

## 🎮 Game Data Structure

Games are stored with the following structure:

```json
{
  "id": 1,
  "title": "Monster Survivors",
  "slug": "monster-survivors",
  "description": "An intense survival game...",
  "long_description": "Detailed description...",
  "thumbnail_url": "https://example.com/thumb.jpg",
  "game_url": "https://example.com/game",
  "category_id": 1,
  "category_name": "Action",
  "rating": 4.5,
  "total_plays": 15420,
  "is_featured": true,
  "is_new": false,
  "is_active": true,
  "tags": ["Survival", "Action", "Shooter"],
  "features": ["Intense Combat", "Easy Controls"],
  "controls": {
    "WASD": "Move your character",
    "Mouse": "Aim your weapon"
  },
  "release_date": "2024-12-01T00:00:00",
  "created_at": "2024-12-01T10:30:00",
  "updated_at": "2024-12-01T10:30:00"
}
```

## 🔐 Security Features

- API rate limiting via Nginx
- SQL injection protection via SQLAlchemy ORM
- XSS protection headers
- Admin API key authentication
- Input validation and sanitization
- Secure session management

## 📈 Analytics & Tracking

### Game Play Tracking
- Automatic play count incrementation
- Session duration tracking
- IP-based analytics
- Daily statistics aggregation

### Admin Dashboard
- Real-time game statistics
- Popular games tracking
- Category performance metrics
- User engagement analytics

## 🚀 Deployment

### Production Deployment with Docker

1. **Set production environment variables**
   ```bash
   export SECRET_KEY="your-secure-secret-key"
   export DATABASE_URL="postgresql://user:pass@localhost:5432/btw_games"
   export FLASK_ENV="production"
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Set up SSL certificates** (recommended)
   - Uncomment HTTPS server block in `nginx.conf`
   - Add SSL certificates to `./ssl/` directory

### Manual Deployment

1. **Set up SQLite database** (automatically created)
2. **Configure environment variables**
3. **Install dependencies and initialize database**
4. **Configure Nginx as reverse proxy**
5. **Use Gunicorn for production WSGI server**

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## 🧪 Testing

### Run the application
```bash
python run.py
```

### Test API endpoints
```bash
# Test games endpoint
curl http://localhost:5000/api/games

# Test search
curl "http://localhost:5000/api/search?q=monster"

# Test admin endpoint (requires API key)
curl -H "X-API-Key: admin-api-key-change-in-production" http://localhost:5000/admin/games
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review API endpoints
- Examine the admin dashboard for game management

## 🔄 Migration from Static Version

This Flask version maintains backward compatibility with the previous static JavaScript version:

1. **API Compatibility**: The new API mimics the old `GAMES_DATA` object structure
2. **Frontend Adaptation**: Existing frontend code was adapted to use API calls
3. **Data Migration**: Game data can be imported via the admin interface or seeding script

### Key Improvements
- **Scalability**: Database-backed storage vs. static JSON
- **Real-time Analytics**: Live game statistics and tracking
- **Admin Interface**: Complete game management system
- **API Architecture**: RESTful endpoints for external integrations
- **Performance**: Nginx caching and database optimization