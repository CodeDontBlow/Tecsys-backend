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


RUN curl -L -o ollama.tar.gz https://github.com/jmorganca/ollama/releases/download/v0.1.32/ollama-linux-amd64.tar.gz && \
    tar -xzf ollama.tar.gz && \
    mv ollama /usr/local/bin/ && \
    chmod +x /usr/local/bin/ollama && \
    rm ollama.tar.gz


RUN which ollama && ollama --version

COPY pyproject.toml ./

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]