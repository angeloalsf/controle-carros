"""Configuração da conexão com o MongoDB.

Ordem de prioridade da URI:
1. Variável de ambiente MONGODB_URI (se estiver definida no terminal).
2. Arquivo .env na pasta do projeto (linha MONGODB_URI=...).
3. MongoDB local (mongodb://localhost:27017).
"""
import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"
DEFAULT_URI = "mongodb://localhost:27017"


def _read_env_file():
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_mongodb_uri():
    return os.getenv("MONGODB_URI") or _read_env_file().get("MONGODB_URI") or DEFAULT_URI
