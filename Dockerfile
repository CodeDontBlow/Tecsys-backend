FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN which ollama && ollama --version

COPY pyproject.toml ./

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY docker-entrypoint.py /docker-entrypoint.py
RUN chmod +x /docker-entrypoint.py

EXPOSE 8000
ENTRYPOINT ["python", "/docker-entrypoint.py"]