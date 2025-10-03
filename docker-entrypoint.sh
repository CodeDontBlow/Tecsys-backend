set -e  

echo "Running setup scripts..."

poetry run python -m app.services.ollama_service.main


# Iniciar servidor
exec "$@"