FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copiar arquivos de dependências primeiro para aproveitar cache do Docker
COPY pyproject.toml ./

# Instalar dependências Python
RUN poetry install --no-interaction --no-ansi

# Criar entrypoint DENTRO do container (evita problemas de Windows)
RUN echo '#!/bin/bash' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'echo "Running setup scripts..."' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'poetry run python -m app.scripts.setup' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'echo "Starting server..."' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'exec "$@"' >> /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

# Copiar o restante da aplicação
COPY . .

# Criar diretórios necessários para a aplicação
RUN mkdir -p /app/data /app/db/chroma_db

# Criar usuário não-root e ajustar permissões
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Usar entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

# Comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]