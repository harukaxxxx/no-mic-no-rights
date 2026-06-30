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
PORT=$(grep '^PORT=' .env 2>/dev/null | cut -d= -f2 || echo "8000")
echo "Access the web interface at: http://${IP}:${PORT}"
echo "Or: http://localhost:${PORT}"
echo ""

uv run python -m backend.main
