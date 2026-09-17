FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

CMD ["sh", "-c", "alembic upgrade head && exec python -m app.main"]
