---
title: Travelian India
emoji: 🏃
colorFrom: Blue
colorTo: Indicolite
sdk: react
sdk_version: 19.1.1
app_file: frontend/src/App.tsx
pinned: false
short_description: AI-Powered Travel Planner for India - React + FastAPI
---
<p align="center">
  <img src="LOGO.png" alt="Travelian Logo" width="200"/>
</p>

# Travelian India

A modern AI-powered travel itinerary planner built with React + FastAPI, specifically designed for Indian travelers. This application leverages advanced AI agents to create personalized, budget-aware travel itineraries with beautiful UI and interactive maps.

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** with npm
- **Python 3.8+** with pip
- **Groq API Key** (required for ultra-fast, authentic LLM queries)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Travelian
   ```

2. **Backend Setup (FastAPI)**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Copy environment template and add your API keys
   cp env.example .env
   # Edit .env file with your actual API keys (especially GROQ_API_KEY)
   
   python main.py
   ```
   Backend runs on: `http://localhost:8000`

3. **Frontend Setup (React)**
   ```bash
   cd frontend
   npm install
   
   # Copy environment template and configure
   cp env.example .env
   # Edit .env file with your configuration
   
   npm start
   ```
   Frontend runs on: `http://localhost:3002`

## ✨ Features

### 🎯 Core Itinerary Features
- **Authentic LLM Orchestration**: Transitioned to the **Groq API** (`llama-3.1-8b-instant`) for near-instant, real-world data processing, replacing previous mock models.
- **7-Agent Execution Pipeline**: A specialized multi-agent swarm (Research, Accommodation, Transport, Activities, Dining, Itinerary, and Chatbot) that works in parallel to build plans.
- **Budget-Optimized Planning**: Intelligent parsing of user budget levels (Budget, Moderate, Luxury, Premium) to curate realistic travel recommendations.
- **Rich Text Itineraries**: Generated plans are rendered with professional typography, bold highlighting, and structured bullet points for readability.
- **Session-Based Persistence**: Your plan remains stored in the browser's local storage, ensuring you don't lose progress on refresh.

### 👥 TripSync & Social Features
- **Dynamic Group Coordination**: The specialized TripSync module allows users to join or create travel groups for specific dates and destinations.
- **Map-to-Sync Registration**: Integrated **Leaflet.js** map allowing travelers to double-click any location on the world map to immediately pull up the Sync-Registration interface.
- **Live Group Tracking**: Real-time visibility into group capacity, member IDs, and matching scores for collaborative planning.

### 🚀 Smart Crowd Insights
- **Capacity Level Tracking**: Visual indicators (Low/Medium/High) showing live tourist density for global destinations.
- **Optimal Visit Time Prediction**: AI-calculated "Best at HH:MM AM/PM" badges helping travelers avoid peak congestion.
- **High-Contrast Heatmaps (Internal)**: Mathematical trend analysis based on location hashes to predict upcoming density spikes.
- **Signal-Based Analysis**: Factors in weather impact scores, local event intensity, and weekend/holiday weighting for every prediction.
- **Alternative Recommendations**: Dynamic suggestions for "Low-Crowd" nearby places if your primary destination is currently at high capacity.

### 🎨 Premium UI/UX & Animations
- **Cinematic Footer**: High-impact footer featuring a semi-transparent dark overlay on top of looping background video (`.mp4`) for a premium digital experience.
- **GSAP & Framer Motion**: Advanced micro-animations for the hero section, loading transitions, and results timeline entrance.
- **Modern Dark/Light Themes**: A sleek, high-contrast dark-mode focused aesthetic with vibrant "Indian Tricolor" accenting (Saffron/Olive).
- **Real-time Stream Indicators**: Progressive loading bars and status notes showing exactly which AI agent is "thinking" during the generation process.

### 🗺️ Mapping & Navigation
- **Leaflet & OpenStreetMap**: Full interactive map integration that requires **zero API keys** to visualize travel routes.
- **Dynamic Route Drawing**: Automatic polyline visualization from Origin to Destination on every generated plan.
- **Proximity Geocoding**: Reverse-geocoding of map clicks to identify city names for instant trip planning.
- **One-Tap External Directions**: Deep-linking directly into Google Maps and OpenStreetMap for turn-by-turn navigation.

## 💻 Usage

1. **Start the Application**: Ensure both backend (port 8000) and frontend (port 3002) are running
2. **Enter Travel Details**: Fill out the travel form with origin, destination, dates, and preferences
3. **Select Budget Level**: Choose from Budget, Moderate, Luxury, or Premium options
4. **Generate Itinerary**: Click "Create My Personal Travel Itinerary" to generate your plan
5. **Review Results**: View your detailed itinerary with budget breakdown and interactive map
6. **Explore Maps**: Use the integrated map to visualize your travel route
7. **Save & Share**: Download or share your itinerary for offline access

## 🔑 API Key Setup

### Environment Configuration
Both frontend and backend use environment files for configuration:

1. **Backend Environment** (`backend/.env`)
   ```bash
   # Required
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   
   # Optional
   TAILVY_API_KEY=your_tailvy_api_key_here
   MONGODB_URI=your_mongodb_connection_string_here
   ```

2. **Frontend Environment** (`frontend/.env`)
   ```bash
   REACT_APP_API_BASE_URL=http://localhost:8000
   ```

### Required API Keys
- **Groq API Key**: Register at https://console.groq.com/

### Optional API Keys
- **Tailvy API Key**: For enhanced travel recommendations
- **MongoDB Connection URI**: For geo-based attraction search
- **OpenAI API Key**: For vector search of attractions
- **Google Maps API Key**: For enhanced map features (optional, OpenStreetMap works without it)

## 🗺️ MongoDB Integration

The app includes optional MongoDB integration for geo-based attraction recommendations:

1. Stores attraction data with geographical coordinates
2. Uses MongoDB's geospatial queries to find attractions near your destination
3. Implements vector search using OpenAI embeddings for semantic matching
4. Visualizes attractions on an interactive map

If you have a MongoDB Atlas account, you can:
- Enter your connection URI in the settings
- Provide an OpenAI API key for vector embeddings
- Initialize a sample dataset with Indian attractions
- Search for attractions near your destination based on your interests

## 📊 Architecture Evolution

Our project architecture has evolved through multiple versions:

### Hackathon Implementation (v0.1)
![Architecture v0.1](Architecture_of_travel_planner_v0.1.png)
*Enhanced architecture implemented during the hackathon with improved agent communication*


### Future Vision (v2) - Beyond Hackathon Scope
![Architecture v2](Architecture_of_travel_planner_v2.png)
*Planned future architecture with expanded capabilities and integrations*

## 📊 Current Project Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3002)                  │
│              TypeScript + Tailwind CSS + GSAP                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP API Calls
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                 │
│                    Python + Pydantic + Uvicorn                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ AI Processing
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Multi-Agent System                        │
└───┬───────┬───────┬───────┬───────┬───────┬───────┬─────────────┘
    │       │       │       │       │       │       │
    ▼       ▼       ▼       ▼       ▼       ▼       ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Research │ │Accomm.  │ │Transport│ │Activities│ │ Dining  │ │Itinerary│ │ Chatbot │
│  Agent  │ │ Agent   │ │ Agent   │ │  Agent   │ │ Agent   │ │ Agent   │ │  Agent  │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┴───────────┴───────────┘
                                        │
                                        ▼
┌────────────────┬────────────────┬─────────────────┬───────────────┐
│ Google Gemini  │  Tailvy API    │  MongoDB Atlas  │  OpenAI API   │
│   (Required)   │  (Optional)    │   (Optional)    │  (Optional)   │
└────────────────┴────────────────┴─────────────────┴───────────────┘
```

### Key Components:
- **Frontend**: React 19.1.1 with TypeScript, Tailwind CSS, Framer Motion, and GSAP animations
- **Backend**: FastAPI with Pydantic models and Uvicorn server
- **AI System**: LangChain with Google Gemini for multi-agent travel planning
- **Maps**: OpenStreetMap integration (no API key required)
- **Storage**: Session storage for persistent user data

The application follows a modern full-stack architecture where the React frontend communicates with the FastAPI backend through REST APIs. The backend orchestrates multiple AI agents that work collaboratively to create comprehensive travel itineraries tailored to user preferences.

## 🛠️ Technology Stack

### Frontend
- **React**: 19.1.1 with TypeScript
- **Styling**: Tailwind CSS 3.4.17
- **Animations**: Framer Motion 12.23.19 + GSAP 3.13.0
- **Icons**: Lucide React 0.544.0
- **Routing**: React Router DOM 7.9.1
- **Notifications**: React Hot Toast 2.6.0
- **HTTP Client**: Axios 1.12.2

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Validation**: Pydantic 2.5.0
- **AI Framework**: LangChain 0.1.0
- **Language Model**: Groq (`llama-3.1-8b-instant`)
- **Environment**: Python-dotenv 1.0.0

### Optional Integrations
- **MongoDB**: For geo-based recommendations
- **OpenAI**: For vector embeddings
- **Tailvy API**: For enhanced travel planning

## 🚀 Future Endeavours

Explore our comprehensive vision for integrating Travelian India into the Samsung ecosystem:

**[📖 Read Future Endeavours Document](FUTURE_ENDEAVOURS.md)**

### Key Highlights:
- **Payment Integration** 💳 - Direct travel bookings and expense tracking
- **Calendar Sync** 📅 - Automatic itinerary import with smart reminders
- **Wallet/Pass Integration** 🔐 - Secure storage of travel documents
- **Smart Watch Integration** ⌚ - Real-time travel updates on wearables
- **AI Voice Commands** 🤖 - Voice-activated travel planning
- **SmartThings Integration** 📺 - Smart home travel experience

*Vision: Empowering every Indian traveler with intelligent, connected, and personalized travel experiences through the Samsung ecosystem.*

## 📹 Submissions

### India Innovates Hackathon 2026

**Team**: BitWizards  
**Project**: Travelian India v2.0 - AI-Powered Travel Planning Platform  
**Tag**: `India Innovates'26`

#### 📋 Submission Files
- **Team Information**: [TeamName.md](TeamName.md)
- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Future Endeavours**: [FUTURE_ENDEAVOURS.md](FUTURE_ENDEAVOURS.md)

#### 🎥 Demo & Resources
- **Live Demo**: [GitHub Repository](https://github.com/Prateeeek7/Travelian_BitWizards_GenAI)
- **Demo Videos & Extra Files**: [Google Drive Folder](https://drive.google.com/drive/folders/13uLGxveZvIy2THDxlXiX7ZMsMXkpDNQ2?usp=sharing)
- **Documentation**: Complete setup and API documentation included
- **Architecture**: Modern React + FastAPI with AI integration
- **Features**: Rich text formatting, interactive maps, budget planning

#### 🏆 Key Achievements
- ✅ **Modern Architecture**: React 19.1.1 + FastAPI + TypeScript
- ✅ **AI Integration**: Multi-agent system with Google Gemini
- ✅ **Rich UI/UX**: GSAP animations and Tailwind CSS styling
- ✅ **Interactive Maps**: OpenStreetMap with Google Maps fallback
- ✅ **Budget Planning**: Smart budget parsing and allocation
- ✅ **Samsung Vision**: Comprehensive ecosystem integration roadmap










