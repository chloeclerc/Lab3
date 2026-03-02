#!/usr/bin/env bash
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
python -c "import psycopg2; print('psycopg2 OK')"
python manage.py collectstatic --no-input
python manage.py migrate
