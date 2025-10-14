#!/bin/bash

# Quick fix for cache table error
echo "Fixing cache table error..."

# Set environment variable to use memory cache temporarily
export USE_MEMORY_CACHE=true

echo "Environment variable set: USE_MEMORY_CACHE=true"
echo "This will use memory cache instead of database cache"
echo "Add this to your Render environment variables:"
echo "USE_MEMORY_CACHE=true"

# Try to create cache table
echo "Attempting to create cache table..."
python manage.py migrate
python manage.py createcachetable

echo "Cache fix completed!"
echo "The application should now work with memory cache fallback"
