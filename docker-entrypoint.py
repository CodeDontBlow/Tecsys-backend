#!/usr/bin/env python3
import subprocess
import sys
import time
import requests

def run_command(cmd, shell=False):
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=True)
        else:
            result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

def check_ollama_ready():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    
    if not run_command(["which", "ollama"]):
        print("ERROR: Ollama not found")
        sys.exit(1)
    
    ollama_process = subprocess.Popen(["ollama", "serve"])
    
    for i in range(10):  
        if check_ollama_ready():
            break
        print(f"Waiting... ({i+1}/10)")
        time.sleep(3)
    else:
        print("ERROR: Ollama failed to start")
        ollama_process.terminate()
        sys.exit(1)
    
    print("Running ChromaDB setup...")
    run_command(["poetry", "run", "python", "-m", "app.scripts.setup"])
    
    print("Starting server...")
    run_command(["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()