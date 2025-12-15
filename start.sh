#!/bin/bash

echo "Activating Python virtual environment..."
source venv/bin/activate

echo "Starting Django backend..."
cd backend
python manage.py runserver &
BACK_PID=$!

echo "Starting Vue frontend..."
cd ../frontend
npm run serve &


open http://localhost:8080/
wait $BACK_PID