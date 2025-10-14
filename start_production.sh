#!/bin/bash

# Production startup script for ZtionSec
echo "Starting ZtionSec Production Server..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=ztionsec.settings
export PYTHONPATH=/app:$PYTHONPATH

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create cache table if it doesn't exist
echo "Setting up cache..."
python manage.py createcachetable || true

# Start Gunicorn with optimized settings
echo "Starting Gunicorn server..."
exec gunicorn ztionsec.wsgi:application \
    --config gunicorn.conf.py \
    --log-file - \
    --access-logfile - \
    --error-logfile - \
    --log-level info
