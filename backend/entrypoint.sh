#!/bin/sh

set -e

if [ "$#" -gt 0 ]; then
exec "$@"
fi

echo "Waiting for PostgreSQL..."

while ! pg_isready -h db -p 5432 -U postgres; do
sleep 1
done

echo "PostgreSQL is ready."

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
