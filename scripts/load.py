import os
import pandas as pd

def load_data(path: str, since: str = None) -> pd.DataFrame:
    """
    Lee un CSV desde la ruta dada y devuelve un DataFrame.
    Si existe columna 'updated_at' y se pasa 'since', filtra filas posteriores.
    Lanza FileNotFoundError si el archivo no existe.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    # Intentamos parsear 'updated_at' si existe
    try:
        df = pd.read_csv(path, parse_dates=["updated_at"])
    except ValueError:
        df = pd.read_csv(path)

    # Filtrado incremental si updated_at y since proporcionados
    if since and "updated_at" in df.columns:
        df = df[df["updated_at"] > since]
    return df
