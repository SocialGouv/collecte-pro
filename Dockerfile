FROM node:24.22.1-trixie-slim AS front
WORKDIR /app
COPY package.json package-lock.json .parcelrc ./
COPY static/src ./static/src
COPY static/css ./static/css
RUN npm ci --no-audit --no-fund

FROM python:3.14.9-slim-trixie AS python
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev locales \
 && sed -i 's/^# *fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN python -m venv /app/venv \
 && /app/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.14.9-slim-trixie
RUN apt-get update \
 && apt-get install -y --no-install-recommends libmagic1 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 1000 app \
 && useradd --uid 1000 --gid 1000 --home-dir /app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
ENV PATH=/app/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=fr_FR.UTF-8 \
    LC_ALL=fr_FR.UTF-8 \
    PORT=8000
COPY --from=python /usr/lib/locale/locale-archive /usr/lib/locale/locale-archive
COPY --from=python /app/venv /app/venv
COPY --from=front /app/static/dist ./static/dist
COPY --from=front /app/node_modules/bootstrap/dist/js ./node_modules/bootstrap/dist/js
COPY --from=front /app/node_modules/jquery/dist ./node_modules/jquery/dist
COPY . .
RUN SECRET_KEY=build \
    DATABASE_URL=sqlite:////tmp/build.sqlite3 \
    CELERY_BROKER_URL=redis://localhost:6379 \
    EMAIL_HOST=localhost \
    EMAIL_PORT=25 \
    EMAIL_HOST_USER= \
    EMAIL_HOST_PASSWORD= \
    DEFAULT_FROM_EMAIL=build@localhost \
    python manage.py collectstatic --noinput --link \
 && python -m compileall -q -x '/app/venv/' /app \
 && mkdir -p /app/media \
 && chown 1000:1000 /app/media
USER 1000:1000
EXPOSE 8000
CMD ["uwsgi", "--ini", "uwsgi.ini"]
