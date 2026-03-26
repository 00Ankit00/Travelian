# 🚀 Travelian India - Complete Setup Guide

This comprehensive guide will help you set up the complete **React + TypeScript Frontend + FastAPI Backend** integration for the Travelian India platform with all the latest features including smooth animations, rich text formatting, interactive maps, and budget-aware planning.

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm/yarn
- **Google Gemini API Key** (required) - Get from [Google AI Studio](https://ai.google.dev/)
- **Git** for version control
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3002)               │
│              TypeScript + Tailwind CSS + GSAP               │
│              Framer Motion + Lucide Icons                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API Calls (REST)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)              │
│                    Python + Pydantic + Uvicorn              │
│                    CORS + Environment Variables             │
└─────────────────────┬───────────────────────────────────────┘
                      │ AI Processing
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Multi-Agent System (LangChain)               │
│              + Google Gemini API + Budget Parser            │
│              + OpenStreetMap Integration                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Features:
- **🎨 Modern UI**: React 19.1.1 with TypeScript and Tailwind CSS
- **🎭 Smooth Animations**: GSAP and Framer Motion for enhanced UX
- **🗺️ Interactive Maps**: OpenStreetMap with Google Maps fallback
- **💰 Budget Planning**: Smart budget parsing and allocation
- **📝 Rich Text**: Book-like itinerary formatting
- **🔒 Secure**: Environment-based API key management

## 🚀 Quick Start

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd Travelian

# Verify directory structure
ls -la
# Should show: backend/, frontend/, README.md, etc.
```

### 2. Backend Setup (FastAPI)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp env.example .env
# Edit .env file with your actual API keys

# Run the FastAPI server
python main.py
```

**Backend will be available at:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs`
**Health Check:** `http://localhost:8000/health`

### 3. Frontend Setup (React + TypeScript)

```bash
cd frontend

# Install Node.js dependencies
npm install

# Copy environment template and configure
cp env.example .env
# Edit .env file with your configuration

# Start development server
npm start
```

**Frontend will be available at:** `http://localhost:3002`
**Note:** The app runs on port 3002 to avoid conflicts with other React apps

## 🔧 Detailed Setup Instructions

### Backend Configuration

#### 1. Install Dependencies

```bash
cd backend

# Install core FastAPI dependencies
pip install fastapi uvicorn pydantic python-multipart python-dotenv

# Install AI and language model dependencies
pip install langchain google-generativeai langchain-google-genai

# Install optional dependencies for enhanced features
pip install pymongo openai requests
```

#### 2. Environment Variables

Copy the environment template and configure your API keys:

```bash
# Copy the template
cp env.example .env

# Edit the .env file with your actual API keys
```

The `.env` file should contain:

```env
# Required
GEMINI_API_KEY=your_actual_gemini_api_key

# Optional
MONGODB_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
TAILVY_API_KEY=your_tailvy_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 3. Verify Backend

```bash
# Test the backend health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "travel_module": true
}

# Test API documentation
# Open http://localhost:8000/docs in your browser
# You should see the FastAPI interactive documentation
```

### Frontend Configuration

#### 1. Install Dependencies

```bash
cd frontend

# Install all dependencies
npm install

# This will install:
# - React 19.1.1 with TypeScript
# - Tailwind CSS for styling
# - Framer Motion for animations
# - GSAP for advanced animations
# - Lucide React for icons
# - React Router DOM for routing
# - Axios for API calls
# - React Hot Toast for notifications
```

#### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
```

The `.env` file should contain:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
REACT_APP_APP_NAME=Travelian India
REACT_APP_VERSION=2.0.0
```

#### 3. Verify Frontend

Open `http://localhost:3002` in your browser. You should see:
- Beautiful landing page with Indian theme (orange/green colors)
- Smooth hero animations with GSAP
- Navigation header with logo
- Responsive design that works on all devices
- Interactive elements with hover effects

#### 4. Test API Integration

1. **Navigate to Travel Planner**: Go to `/plan` page
2. **Fill Travel Form**: Enter origin, destination, dates, budget, and preferences
3. **Generate Itinerary**: Click "Create My Personal Travel Itinerary"
4. **Verify Results**: Check that you get:
   - Detailed day-by-day itinerary with rich text formatting
   - Budget breakdown with proper allocation
   - Interactive map showing your route
   - Loading states and smooth animations
5. **Check Browser Console**: Verify API calls are working without errors

## 🌐 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/travel/plan` | Generate travel itinerary with budget breakdown |
| `POST` | `/chatbot/ask` | AI chatbot response |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) |

### Request/Response Examples

#### Travel Planning

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

**Response includes:**
- Detailed itinerary with rich text formatting
- Budget breakdown (total, daily, and category-wise)
- Map data for route visualization
- Important notes and recommendations

#### Chatbot

```bash
curl -X POST "http://localhost:8000/chatbot/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best places to visit in Rajasthan for a 7-day trip?"
  }'
```

## 🎨 Frontend Features

### Pages

1. **Homepage** (`/`) - Landing page with hero animations and features
2. **Travel Planner** (`/plan`) - Main itinerary generation form with budget selection
3. **Itinerary View** (`/itinerary-view`) - Detailed itinerary display with rich text formatting
4. **Chatbot** (`/chatbot`) - AI travel assistant with conversational interface
5. **About** (`/about`) - Team and project information
6. **Demo** (`/demo`) - Rich text formatting demonstration

### Key Components

- **HeroAnimationComponent** - GSAP-powered smooth animations
- **SmoothHeroAnimation** - Advanced animation system with auto-play
- **RichText** - Book-like text formatting with bold, italic, bullets
- **SimpleMap** - OpenStreetMap integration with Google Maps fallback
- **BudgetSummary** - Smart budget breakdown and visualization
- **DayItinerary** - Individual day itinerary display
- **ImportantNotes** - Formatted important travel notes
- **LoadingSpinner** - Elegant loading states
- **Header/Footer** - Navigation with responsive design

### Styling & Animations

- **Tailwind CSS** for utility-first styling
- **Indian Theme** with orange (#FF671F) and green (#046A38) colors
- **GSAP Animations** for smooth hero animations and transitions
- **Framer Motion** for component animations
- **Responsive Design** for all screen sizes (mobile-first)
- **Hardware Acceleration** for optimal performance

## ✨ New Features in v2.0

### 🎭 Advanced Animations
- **GSAP Integration**: Smooth hero animations with auto-play functionality
- **Performance Optimized**: Hardware-accelerated animations for 60fps
- **Interactive Elements**: Mouse-following animations and hover effects

### 📝 Rich Text Formatting
- **Book-like Display**: Bold, italic, and bullet point formatting
- **Markdown Support**: Automatic parsing of formatted text
- **Enhanced Readability**: Professional typography and spacing

### 🗺️ Interactive Maps
- **OpenStreetMap**: Free, no API key required
- **Google Maps Fallback**: External links for enhanced features
- **Error Handling**: Graceful fallbacks when maps fail to load
- **Route Visualization**: Origin to destination route display

### 💰 Smart Budget Planning
- **Budget Parsing**: Automatic extraction from text descriptions
- **Category Breakdown**: Accommodation, food, transport, activities
- **Visual Display**: Clear budget allocation and visualization
- **Dynamic Calculation**: Real-time budget adjustments

### 🔒 Security & Configuration
- **Environment Variables**: Secure API key management
- **No Hardcoded Keys**: All sensitive data in environment files
- **CORS Configuration**: Proper cross-origin resource sharing
- **Type Safety**: Full TypeScript implementation

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd backend
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

2. **API Key Issues**
   ```bash
   # Verify environment variable
   echo $GEMINI_API_KEY
   # Or check in Python
   python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
   ```

3. **Port Already in Use**
   ```bash
   # Kill process on port 8000 (backend)
   lsof -ti:8000 | xargs kill -9
   
   # Kill process on port 3002 (frontend)
   lsof -ti:3002 | xargs kill -9
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Check if .env file exists
   ls -la backend/.env
   ls -la frontend/.env
   
   # Verify environment variables are loaded
   python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
   ```

5. **CORS Issues**
   ```bash
   # Check CORS configuration in backend
   # Ensure frontend URL is in ALLOWED_ORIGINS
   # Default: http://localhost:3002
   ```

#### Frontend Issues

1. **Dependencies Not Found**
   ```bash
   # Clear npm cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **API Connection Errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend
   - Verify `REACT_APP_API_BASE_URL` in frontend `.env`
   - Check browser console for network errors

3. **Animation Performance Issues**
   ```bash
   # Check if GSAP is properly installed
   npm list gsap
   
   # Verify hardware acceleration is enabled
   # Check browser dev tools for performance
   ```

4. **Map Not Loading**
   - Check if OpenStreetMap is accessible
   - Verify fallback to Google Maps works
   - Check browser console for map errors

5. **Build Errors**
   ```bash
   # Check TypeScript errors
   npm run build
   
   # Fix any type issues
   # Common fixes:
   # - Update type definitions
   # - Fix import statements
   # - Resolve interface mismatches
   ```

### Debug Mode

#### Backend Debug

```bash
# Run with debug logging
uvicorn main:app --reload --log-level debug
```

#### Frontend Debug

```bash
# Check browser console for errors
# Enable network tab to see API calls
# Verify environment variables
```

## 🚀 Production Deployment

### Backend Deployment

1. **Docker (Recommended)**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Cloud Platforms**
   - **Railway**: Connect GitHub repo
   - **Render**: Deploy from Git
   - **Heroku**: Use Procfile

### Frontend Deployment

1. **Build for Production**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   vercel --prod
   ```

3. **Deploy to Netlify**
   - Connect GitHub repository
   - Build command: `npm run build`
   - Publish directory: `dist`

## 📊 Monitoring & Logging

### Backend Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use in your code
logger.info("Travel itinerary generated successfully")
logger.error("Failed to connect to AI service")
```

### Frontend Monitoring

```typescript
// Add error boundaries
// Monitor API response times
// Track user interactions
```

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure CORS properly for production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Input Validation**: Validate all user inputs
5. **HTTPS**: Use HTTPS in production

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React TypeScript Guide](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Create React App Docs](https://create-react-app.dev/)

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review error logs
3. Verify all dependencies are installed
4. Ensure both backend and frontend are running
5. Check API documentation at `/docs`

## ✅ Complete Setup Verification

### Checklist for Successful Setup

**Backend Verification:**
- [ ] Backend runs on `http://localhost:8000`
- [ ] Health check returns `{"status": "healthy"}`
- [ ] API docs accessible at `http://localhost:8000/docs`
- [ ] Environment variables loaded correctly
- [ ] Gemini API key configured

**Frontend Verification:**
- [ ] Frontend runs on `http://localhost:3002`
- [ ] Homepage loads with hero animations
- [ ] Navigation works between pages
- [ ] Travel planner form is functional
- [ ] API calls to backend succeed

**Feature Verification:**
- [ ] Travel itinerary generation works
- [ ] Budget breakdown displays correctly
- [ ] Interactive map loads and shows route
- [ ] Rich text formatting renders properly
- [ ] Smooth animations perform well
- [ ] Chatbot responds to queries

### Test Travel Plan

Try generating a test itinerary:
1. **Origin**: Mumbai
2. **Destination**: Delhi
3. **Duration**: 3 days
4. **Budget**: Moderate (₹10,000 - ₹25,000)
5. **Interests**: Culture & Heritage, Food & Cuisine

Expected results:
- Detailed day-by-day itinerary
- Budget breakdown with categories
- Interactive map with route
- Rich text formatting with bold/italic
- Smooth loading animations

## 🎯 Next Steps

After successful setup:

1. **Customize AI Prompts**: Modify agent instructions in `backend/travel.py`
2. **Add Destinations**: Expand the travel database with more Indian locations
3. **Enhance Maps**: Add more map providers or custom markers
4. **User Authentication**: Implement user accounts and saved itineraries
5. **Payment Integration**: Add booking capabilities with Indian payment gateways
6. **Mobile App**: Create React Native version for mobile users
7. **Deploy to Production**: Use Docker, Railway, or Vercel for deployment

## 🚀 Deployment Options

### Quick Deploy with Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Deploy to Cloud Platforms
- **Frontend**: Vercel, Netlify, or GitHub Pages
- **Backend**: Railway, Render, or Heroku
- **Database**: MongoDB Atlas or Supabase

---

**Happy Coding! 🚀**

Built with ❤️ by BitWizards for Samsung Prism GenAI'25 Hackathon

*Travelian India - Modern AI-Powered Travel Planning*
