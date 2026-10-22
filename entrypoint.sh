#!/bin/sh
set -e

# Apply database migrations. 
python manage.py migrate --noinput

# Start Celery in the background, using the option of the service file deploy/conf/celery.service.
# The logs end up in the container stdout
celery -A ecc worker --beat -l info \
    --scheduler=django_celery_beat.schedulers:DatabaseScheduler &

exec "$@"
