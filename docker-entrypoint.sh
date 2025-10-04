
set -e

while ! curl -s http://ollama:11434/api/tags > /dev/null; do
  echo "Ollama não está pronto, aguardando 5 segundos..."
  sleep 5
done

echo "Executando setup do chromadb..."
poetry run python -m app.scripts.setup

echo "Iniciando servidor..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"