FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Requirements now live under django/. Install the dev set because the only
# compose service runs config.settings.dev (debug_toolbar/django_extensions).
# requirements-dev.txt pulls in the base requirements.txt via "-r".
COPY django/requirements.txt django/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

WORKDIR /app/django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]