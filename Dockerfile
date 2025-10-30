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
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libxi6 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-bin \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN which ollama && ollama --version

COPY pyproject.toml ./

RUN poetry install --no-interaction --no-ansi

COPY . .

RUN playwright install chromium
RUN playwright install-deps

COPY docker-entrypoint.py /docker-entrypoint.py
RUN chmod +x /docker-entrypoint.py

EXPOSE 8000
ENTRYPOINT ["python", "/docker-entrypoint.py"]