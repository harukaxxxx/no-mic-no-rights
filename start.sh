#!/bin/bash

set -e

echo "=== No mic, no rights ==="
echo ""

if [ ! -f .env ]; then
  echo "Warning: .env file not found. Copying from .env.example..."
  cp .env.example .env
  echo "Please edit .env and add your Discord bot token."
  echo ""
fi

echo "Installing Python dependencies..."
uv sync

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building frontend..."
npm run build
cd ..

echo ""
echo "Starting server..."
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
echo "Access the web interface at: http://${IP}:8000"
echo "Or: http://localhost:8000"
echo ""

uv run python -m backend.main
