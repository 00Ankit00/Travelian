#!/bin/bash

set -e

echo "Starting Travelian setup..."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required (3.8+)."
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js 18+ and npm are required."
  exit 1
fi

echo "Setting up backend..."
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp env.example .env
  echo "Created backend/.env from env.example. Add GEMINI_API_KEY before running."
fi

echo "Setting up frontend..."
cd "$FRONTEND_DIR"
npm install

if [ ! -f .env ]; then
  cp env.example .env
  echo "Created frontend/.env from env.example."
fi

echo ""
echo "Setup complete."
echo "Start backend: cd backend && source venv/bin/activate && python main.py"
echo "Start frontend: cd frontend && npm start"
echo "Open app at: http://localhost:3002"
