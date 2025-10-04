#!/bin/sh
set -e

echo "=== Checking Ollama ==="

if ! command -v ollama > /dev/null; then
    echo "err: ollama not found in PATH"
    exit 1
fi

echo " start pllama..."
ollama serve &
OLLAMA_PID=$!

echo "waiting ollama full start..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "Ollama is not ready, waiting 3 seconds..."
    sleep 3
done

echo "ollama started"


echo "checking model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "qwen3-embedding:0.6b"; then
    ollama pull qwen3-embedding:0.6b
else
    echo "model is available"
fi

echo "running chromadb setup..."
poetry run python -m app.scripts.setup

echo "start server..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"