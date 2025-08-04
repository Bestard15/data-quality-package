import pandas as pd
import os

def load_data(path: str) -> pd.DataFrame:
    """
    Lee un CSV desde la ruta dada y devuelve un DataFrame.
    Lanza FileNotFoundError si el archivo no existe.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    return pd.read_csv(path)
