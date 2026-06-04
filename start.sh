#!/bin/bash
# Startup script for Hermes + Dashboard

# Start Hermes in the background
echo "Starting Hermes Agent..."
hermes daemon start &

# Give Hermes a moment to start
sleep 5

# Start the simple HTTP server for the dashboard on port 8080
echo "Starting dashboard server..."
cd /app/dashboard
python3 -m http.server 8080 --bind 0.0.0.0

# Keep the script running
wait