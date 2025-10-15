#!/bin/bash
# Simple uptime monitor for ZtionSec
# Run this on a VPS or local machine

SERVICE_URL="https://ztionsec-api.onrender.com"
HEALTH_ENDPOINT="$SERVICE_URL/api/v1/health/"

while true; do
    echo "$(date): Checking service..."
    
    if curl -f -m 30 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        echo "✅ Service is up"
    else
        echo "❌ Service is down - attempting to wake up..."
        
        # Try multiple endpoints
        curl -f -m 45 "$SERVICE_URL/api/v1/stats/" > /dev/null 2>&1
        curl -f -m 45 "$HEALTH_ENDPOINT" > /dev/null 2>&1
        
        sleep 30
        
        # Check again
        if curl -f -m 30 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            echo "✅ Service woke up"
        else
            echo "❌ Service still down"
        fi
    fi
    
    # Wait 5 minutes
    sleep 300
done
