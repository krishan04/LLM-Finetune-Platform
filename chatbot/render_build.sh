#!/usr/bin/env bash
# Render runs this script automatically on every deploy.
# Set it in Render dashboard → Build Command: ./render_build.sh

set -o errexit   # exit on any error

pip install --upgrade pip
pip install -r requirements/production.txt

# Run migrations (safe to run on every deploy — Django is idempotent)
python manage.py migrate --noinput

# Collect static files to Cloudflare R2
python manage.py collectstatic --noinput