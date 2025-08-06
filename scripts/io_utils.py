import os
import shutil
import datetime
import json
import pandas as pd

def save_csv(df: pd.DataFrame, path: str):
    """
    Guarda un DataFrame en CSV, creando la carpeta si no existe.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

def save_json(obj, path: str):
    """
    Guarda un objeto serializable a JSON, creando la carpeta si no existe.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def archive_reports(src_reports: str = "reports", archive_root: str = "reports\\archive") -> str:
    """
    Mueve o copia todos los informes de `src_reports` (CSV, JSON, subcarpetas)
    a una nueva carpeta timestamp bajo `archive_root`.
    Devuelve la ruta del directorio destino.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(archive_root, timestamp)
    os.makedirs(dest, exist_ok=True)

    for entry in os.listdir(src_reports):
        if entry == os.path.basename(archive_root):
            continue
        src_path = os.path.join(src_reports, entry)
        dst_path = os.path.join(dest, entry)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

    return dest
