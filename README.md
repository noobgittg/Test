# 🚀 High-Performance Auto Filter Bot

A lightning-fast Telegram auto filter bot with 4 database support, Redis caching, and advanced search capabilities.

## ⚡ Features

- **4 Database Redundancy**: MongoDB cluster support for high availability
- **Redis Caching**: Sub-second response times with intelligent caching
- **IMDB Integration**: Automatic movie information and posters
- **Smart Search**: Spell check, relevance scoring, and pagination
- **High Performance**: Concurrent processing and load balancing
- **Admin Tools**: Bulk indexing, statistics, and management commands

## 🛠️ Installation

### Method 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autofilter-bot.git
cd autofilter-bot
```

2. Copy and configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

### Method 2: Manual Installation

1. Install Python 3.9+
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables
4. Run the bot:
```bash
python bot.py
```

## ⚙️ Configuration

### Required Environment Variables

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# At least one database URI is required
DATABASE_URI_1=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_URI_2=mongodb+srv://username:password@cluster2.mongodb.net/
DATABASE_URI_3=mongodb+srv://username:password@cluster3.mongodb.net/
DATABASE_URI_4=mongodb+srv://username:password@cluster4.mongodb.net/

# Redis for caching (recommended)
REDIS_URL=redis://localhost:6379

# Admin users (space-separated user IDs)
AUTH_USERS=123456789 987654321

# Channels to index (space-separated channel IDs)
CHANNELS=-1001234567890 -1001234567891
```

## 🔧 Admin Commands

- `/index <channel_id>` - Index files from a channel
- `/stats` - Get database and performance statistics
- `/broadcast <message>` - Broadcast message to all users

## 🚀 Performance Optimizations

### Database Level
- Connection pooling with configurable pool sizes
- Concurrent queries across multiple databases
- Optimized indexes for fast text search
- Load balancing between database instances

### Caching Layer
- Redis for distributed caching
- TTL-based cache invalidation
- Local memory cache for frequently accessed data
- Smart cache warming strategies

### Application Level
- Asynchronous processing throughout
- Batch operations for bulk indexing
- Rate limiting for external API calls
- Efficient pagination for large result sets

## 📊 Monitoring

The bot includes comprehensive monitoring:
- Real-time performance metrics
- Database health checks
- Cache hit/miss ratios
- Search response times
- Error tracking and logging

## 🔒 Security Features

- Channel subscription verification
- Admin-only command restrictions
- Rate limiting for API protection
- Input validation and sanitization
- Secure file handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Join our Telegram support group
- Contact the maintainers

## 🙏 Acknowledgments

- Pyrogram library for Telegram Bot API
- MongoDB for database services
- Redis for caching solutions
- All contributors and users

---

**Note**: This bot is designed for high-performance scenarios and includes advanced features. Make sure to properly configure all components for optimal performance.