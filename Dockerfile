# Frontend build image
FROM node:24-alpine AS frontend-builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json .parcelrc ./
RUN npm ci --ignore-scripts

# Copy frontend sources and build the production bundles
COPY static ./static
RUN npm run build-all

# Runtime image with python 3.14
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# libmagic1 is required at runtime by python-magic
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application source code
COPY . .

# Replace static/dist with the compiled assets from the frontend-builder stage
RUN rm -rf static/dist
COPY --from=frontend-builder /app/static/dist ./static/dist

# STATICFILES_DIRS also references these node_modules packages directly, so
# bring just those over (not the full node_modules tree) from the builder.
COPY --from=frontend-builder /app/node_modules/bootstrap/dist/js ./node_modules/bootstrap/dist/js
COPY --from=frontend-builder /app/node_modules/jquery/dist ./node_modules/jquery/dist

# Run collectstatic once at build time so it doesn't need to run on every
# container startup. 
# Settings.py requires some env var to run
# Using some dummy vars to allow collectstatic to run
# The vars are only set for this command and will not be persisted in the final image.
RUN DEBUG=False \
    SECRET_KEY=build-time-dummy-secret \
    DATABASE_URL=sqlite://:memory: \
    EMAIL_HOST=localhost \
    EMAIL_PORT=25 \
    EMAIL_HOST_USER=dummy \
    EMAIL_HOST_PASSWORD=dummy \
    EMAIL_USE_TLS=False \
    EMAIL_USE_SSL=False \
    DEFAULT_FROM_EMAIL=dummy@example.com \
    CELERY_BROKER_URL=redis://localhost:6379 \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uwsgi", "--ini", "uwsgi.ini"]
