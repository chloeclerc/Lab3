#!/usr/bin/env bash
# Run migrations before starting (workaround when Pre-Deploy Command is paid-only)
set -o errexit
python manage.py migrate --no-input
exec gunicorn HandyRides.wsgi:application
