#!/usr/bin/env python3
import subprocess
import sys
import time
import requests
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_command(cmd, shell=False):
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=True)
        else:
            result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[DOCKER] Command failed: {e}")
        return False

def check_ollama_ready():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

import os

def create_database():
    """Create descriptum database if it doesn't exist"""
    try:
        db_host = os.getenv('DB_HOST', 'db')
        db_user = os.getenv('POSTGRES_USER', 'user')
        db_password = os.getenv('POSTGRES_PASSWORD', 'password')
        db_port = os.getenv('DB_PORT', '5432')
        
        conn = psycopg2.connect(
            host=db_host,
            database="postgres",  # Connect to default database
            user=db_user,
            password=db_password,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'descriptum'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE descriptum")
            logger.info("[DOCKER] Database 'descriptum' created successfully")
        else:
            logger.info("[DOCKER] Database 'descriptum' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[DOCKER] Error creating database: {e}")
        return False

def main():
    logger.info("[DOCKER] Checking/Creating descriptum database...")
    if not create_database():
        logger.warning("[DOCKER] Could not create descriptum database")
    
    if not run_command(["which", "ollama"]):
        print("[DOCKER] Ollama not found")
        sys.exit(1)
    
    ollama_process = subprocess.Popen(["ollama", "serve"])
    
    for i in range(10):  
        if check_ollama_ready():
            break
        logger.info(f"[DOCKER] Waiting for Ollama to start... ({i+1}/10)")
        time.sleep(3)
    else:
        print("[DOCKER] Ollama failed to start")
        ollama_process.terminate()
        sys.exit(1)
    
    logger.info("[DOCKER] Running ChromaDB setup...")
    run_command(["poetry", "run", "python", "-m", "app.scripts.setup"])
    
    # Add Alembic migration
    logger.info("[DOCKER] Running database migrations...")
    if not run_command(["poetry", "run", "alembic", "upgrade", "head"]):
        logger.warning("[DOCKER] Alembic migration failed")
    
    logger.info("[DOCKER] Starting server...")
    run_command(["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()