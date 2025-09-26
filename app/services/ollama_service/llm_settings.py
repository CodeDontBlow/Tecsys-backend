# setup_ollama.py
import os
import ollama
import subprocess

#line 39 in generate final_desc
# 
class Llm_settings:

    def check_model_exists(model_name):
        ollama_models = ollama.list().get('models', [])
        return any(model.model == model_name for model in ollama_models)

    def create_ollama_model():
        try:
            caminho = os.path.abspath('./app/services/ollama_service/modelfile')
            result = subprocess.run(
                ['ollama', 'create', 'descriptum', '-f', caminho],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")
            print("Stderr:", e.stderr)
            return None
        except FileNotFoundError:
            print("Erro: Comando 'ollama' não encontrado. Verifique se o Ollama está instalado.")
            return None
        
