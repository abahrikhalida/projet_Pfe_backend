#!/bin/sh

# Wait a few seconds for MySQL to be ready
sleep 5

# Apply Django migrations
python manage.py migrate --noinput

# (Optional) Collect static files if needed
# python manage.py collectstatic --noinput

# Start Django development server
exec python manage.py runserver 0.0.0.0:8000