#!/bin/sh

set -e

SERVICE_TYPE=${1:-$SERVICE_TYPE}

echo "🔧 Service Type: $SERVICE_TYPE"
echo "🟡 Waiting for database to be ready..."

# Wait for PostgreSQL to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  echo "⏳ Waiting for database..."
  sleep 2
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "🟡 Waiting for Redis to be ready..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  echo "⏳ Waiting for Redis..."
  sleep 2
done
echo "✅ Redis is ready!"

case "$SERVICE_TYPE" in
  web)
    echo "🌐 Starting Web Service..."
    
    # Run migrations
    echo "📦 Running migrations..."
    python manage.py migrate --noinput
    
    # Collect static files
    echo "🧩 Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Run development or production server
    if [ "$DJANGO_ENV" = "staging" ] || [ "$DJANGO_ENV" = "development" ]; then
      echo "🚀 Starting Django development server..."
      exec python manage.py runserver 0.0.0.0:8000
    else
      echo "🚀 Starting Gunicorn production server..."
      exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
    fi
    ;;
    
  celery)
    echo "⚙️ Starting Celery Worker..."
    exec celery -A backend worker -l info --pool=solo
    ;;
    
  bot)
    echo "🤖 Starting Telegram Bot..."
    exec python bot.py
    ;;
    
  *)
    echo "❌ Unknown service type: $SERVICE_TYPE"
    echo "Usage: entrypoint.sh [web|celery|bot]"
    exit 1
    ;;
esac
