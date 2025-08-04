import os

def save_csv(df, path: str):
    """
    Guarda un DataFrame en CSV, creando carpetas si es necesario.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
import json

def save_json(obj, path: str):
    """
    Guarda un objeto Python (dict, list…) en JSON, creando carpetas si es necesario.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
