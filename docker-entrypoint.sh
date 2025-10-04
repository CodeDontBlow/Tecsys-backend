#!/bin/sh
set -e

echo "=== Iniciando todos os serviços no mesmo container ==="

# Iniciar Ollama em background
echo "Iniciando Ollama..."
ollama serve &
OLLAMA_PID=$!

# Aguardar Ollama iniciar
echo "Aguardando Ollama ficar pronto..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "Ollama não está pronto, aguardando 3 segundos..."
  sleep 3
done

echo "Ollama está pronto!"

# Baixar o modelo de embedding se necessário
echo "Verificando modelo de embedding..."
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen3-embedding:0.6b"; then
  echo "Baixando modelo qwen3-embedding:0.6b..."
  curl -X POST http://localhost:11434/api/pull \
    -H "Content-Type: application/json" \
    -d '{"name": "qwen3-embedding:0.6b"}' \
  echo "Modelo baixado com sucesso!"
else
  echo "Modelo qwen3-embedding:0.6b já está disponível"
fi

# O ChromaDB agora roda inline com a aplicação Python
echo "Executando setup do chromadb..."
poetry run python -m app.scripts.setup

echo "Iniciando servidor FastAPI..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"