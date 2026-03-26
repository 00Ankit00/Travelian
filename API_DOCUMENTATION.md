# 🔌 Travelian India v2.0 - Complete API Documentation

This document contains all the APIs, endpoints, and external services used in the Travelian India application.

## 📋 Table of Contents

1. [Internal API Endpoints](#internal-api-endpoints)
2. [External Service APIs](#external-service-apis)
3. [Map Services](#map-services)
4. [Environment Variables](#environment-variables)
5. [API Usage Examples](#api-usage-examples)

## 🏠 Internal API Endpoints

### Backend API (FastAPI - Port 8000)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health` | Health check endpoint | - | `{"status": "healthy", "timestamp": "...", "travel_module": true}` |
| `POST` | `/travel/plan` | Generate travel itinerary | TravelRequest | TravelResponse with itinerary, budget, map data |
| `POST` | `/chatbot/ask` | AI chatbot response | ChatbotRequest | ChatbotResponse with AI reply |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) | - | Swagger UI interface |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) | - | ReDoc interface |

### Frontend Routes (React - Port 3002)

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | HomePage | Landing page with hero animations |
| `/plan` | TravelPlanner | Main itinerary generation form |
| `/itinerary-view` | ItineraryView | Detailed itinerary display |
| `/chatbot` | Chatbot | AI travel assistant |
| `/about` | About | Team and project information |
| `/demo` | DemoItinerary | Rich text formatting demonstration |

## 🌐 External Service APIs

### Required Services

#### Google Gemini AI
- **Base URL**: `https://ai.google.dev/`
- **API Key**: Required (GEMINI_API_KEY)
- **Usage**: AI-powered travel planning, itinerary generation, chatbot responses
- **Rate Limits**: Based on API key tier
- **Documentation**: https://ai.google.dev/docs

### Optional Services

#### Tailvy API
- **Base URL**: `https://api.tailvy.com`
- **API Key**: Optional (TAILVY_API_KEY)
- **Usage**: Enhanced travel recommendations
- **Documentation**: Contact Tailvy for API documentation

#### OpenAI API
- **Base URL**: `https://api.openai.com/v1`
- **API Key**: Optional (OPENAI_API_KEY)
- **Usage**: Vector embeddings for semantic search
- **Documentation**: https://platform.openai.com/docs

#### MongoDB Atlas
- **Base URL**: `https://cloud.mongodb.com`
- **Connection String**: Optional (MONGODB_URI)
- **Usage**: Geo-based attraction recommendations
- **Documentation**: https://docs.atlas.mongodb.com

## 🗺️ Map Services

### OpenStreetMap (Primary - Free)
- **API URL**: `https://www.openstreetmap.org/api`
- **Directions URL**: `https://www.openstreetmap.org/directions`
- **Embed URL**: `https://www.openstreetmap.org/export/embed.html`
- **API Key**: Not required
- **Usage**: Interactive maps, route visualization
- **Documentation**: https://wiki.openstreetmap.org/wiki/API

### Google Maps (Fallback - Optional)
- **API URL**: `https://maps.googleapis.com/maps/api`
- **Embed URL**: `https://www.google.com/maps/embed/v1`
- **Directions URL**: `https://www.google.com/maps/dir`
- **API Key**: Optional (GOOGLE_MAPS_API_KEY)
- **Usage**: Enhanced map features, satellite imagery
- **Documentation**: https://developers.google.com/maps/documentation

## 🔧 Environment Variables

### Backend Environment Variables

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional
TAILVY_API_KEY=your_tailvy_api_key_here
MONGODB_URI=your_mongodb_connection_string_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3002,http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
```

### Frontend Environment Variables

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# Map Configuration
REACT_APP_MAP_PROVIDER=openstreetmap
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Application Configuration
REACT_APP_APP_NAME=Travelian India
REACT_APP_VERSION=2.0.0
REACT_APP_ENVIRONMENT=development

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG_MODE=true
REACT_APP_ENABLE_MAP_FEATURES=true
```

## 📝 API Usage Examples

### Travel Planning Request

```bash
curl -X POST "http://localhost:8000/travel/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Mumbai",
    "destination": "Jaipur",
    "startDate": "2024-02-01",
    "endDate": "2024-02-07",
    "duration": 7,
    "budget": "Moderate (₹10,000 - ₹25,000)",
    "travelStyle": "Family Trip",
    "interests": ["Culture & Heritage", "Food & Cuisine"],
    "specialRequirements": "Vegetarian food preferences"
  }'
```

### Chatbot Request

```bash
curl -X POST "http://localhost:8000/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best places to visit in Rajasthan for a 7-day trip?"
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files for sensitive data
3. **CORS**: Configure CORS properly for production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **HTTPS**: Use HTTPS in production environments

## 📊 API Response Formats

### TravelResponse
```json
{
  "itinerary": "Detailed day-by-day itinerary...",
  "mapUrl": "{\"origin\": \"Mumbai\", \"destination\": \"Jaipur\", \"type\": \"directions\"}",
  "budget": {
    "total_budget": 18000,
    "daily_budget": 2571,
    "accommodation": 6300,
    "food": 4500,
    "transport": 3600,
    "activities": 2700,
    "shopping": 900
  }
}
```

### ChatbotResponse
```json
{
  "response": "AI-generated response to user query..."
}
```

### HealthResponse
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "travel_module": true
}
```

## 🚀 Deployment Considerations

### Production Environment Variables
- Update `ALLOWED_ORIGINS` with production domain
- Set `DEBUG=False` for production
- Use production API keys
- Configure proper logging levels
- Set up monitoring and alerting

### Docker Environment
- Use Docker secrets for sensitive data
- Configure proper networking
- Set up health checks
- Use environment-specific configurations

---

**Last Updated**: January 2024  
**Version**: 2.0.0  
**Maintained by**: BitWizards Team
