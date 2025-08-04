import pandas as pd

def compute_quality_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas de calidad por columna:
      - n_nulls, pct_nulls
      - n_duplicates, pct_duplicates
    Devuelve un DataFrame de pandas.
    """
    total = len(df)
    records = []
    for col in df.columns:
        s = df[col]
        n_null = s.isnull().sum()
        n_dup  = s.duplicated().sum()
        records.append({
            'column': col,
            'n_nulls': int(n_null),
            'pct_nulls': round(n_null/total*100, 2) if total else 0.0,
            'n_duplicates': int(n_dup),
            'pct_duplicates': round(n_dup/total*100, 2) if total else 0.0
        })
    return pd.DataFrame(records)
