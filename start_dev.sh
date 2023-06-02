#!/bin/bash
# Convince bash to start a local dev environment when all dependencies are installed

export HOST="127.0.0.1"
# Set the port for FastAPI
export FASTAPI_PORT="8000"
# Set the port for Next.js
export NEXT_PORT="3000"

# Check if PostgreSQL service is running
pg_status=$(brew services list | grep postgresql | awk '{print $2}')

# Start the service if it's not running
if [ "$pg_status" != "started" ]; then
  echo "Starting PostgreSQL service..."
  brew services start postgresql
  echo "PostgreSQL service started."
else
  echo "PostgreSQL service is already running."
fi

# Check if the FastAPI service is already running
fastapi_pid=$(pgrep -f "uvicorn webapp.main:app")

if [ -z "$fastapi_pid" ]; then
  # Start the FastAPI service using Uvicorn in the background
  echo "Starting FastAPI service..."
  uvicorn webapp.main:app --host $HOST --port $FASTAPI_PORT --reload >> webapp.log 2>&1 &
  echo "FastAPI service started with PID $!"
else
  echo "FastAPI service is already running with PID $fastapi_pid."
fi

# Check if the Next.js frontend is already running
next_pid=$(pgrep -f "npm run dev --port $NEXT_PORT")

if [ -z "$next_pid" ]; then
  # Start the Next.js frontend in the background from the root directory
  echo "Starting Next.js frontend..."
  npm run --prefix frontend dev -- --port $NEXT_PORT >> frontend.log 2>&1 &
  echo "Next.js frontend started with PID $!"
else
  echo "Next.js frontend is already running with PID $next_pid."
fi
