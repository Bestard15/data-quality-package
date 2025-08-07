import os
import json
import shutil
import datetime

import pandas as pd

def save_csv(df: pd.DataFrame, path: str):
    """
    Guarda un DataFrame como CSV en la ruta dada, creando carpetas si es necesario.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)

def save_json(data: dict, path: str):
    """
    Guarda un diccionario como JSON en la ruta dada, creando carpetas si es necesario.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def archive_reports(outdir: str) -> str:
    """
    Mueve todo el contenido de outdir a una subcarpeta timestamped dentro de outdir/archive.
    Devuelve la ruta destino.
    """
    ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(outdir, "archive", ts)
    os.makedirs(dest, exist_ok=True)
    for fname in os.listdir(outdir):
        src = os.path.join(outdir, fname)
        if src == dest or fname == "archive":
            continue
        shutil.move(src, dest)
    return dest

def write_manifest(outdir: str, input_csv: str, schema_version: str, row_count: int):
    """
    Crea en outdir/history_manifest.json un JSON con:
      - timestamp (ISO)
      - schema_version (git tag)
      - input_source (ruta CSV)
      - row_count (número de filas procesadas)
    """
    manifest = {
        "timestamp": datetime.datetime.now().isoformat(),
        "schema_version": schema_version,
        "input_source": input_csv,
        "row_count": row_count
    }
    manifest_path = os.path.join(outdir, "history_manifest.json")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

