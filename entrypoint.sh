#!/bin/sh

echo "🟡 Waiting for database to be ready..."
# Wait for PostgreSQL to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is ready!"

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files (for staging/prod)
echo "🧩 Collecting static files..."
python manage.py collectstatic --noinput

# Run development or production server
if [ "$DJANGO_ENV" = "staging" ]; then
  echo "🚀 Starting Django development server..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "🚀 Starting Gunicorn production server..."
  exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
fi
