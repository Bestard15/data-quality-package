import os
import re
import datetime
import json
import pandas as pd
import numpy as np
from scipy.spatial.distance import jensenshannon
from scripts.rules import infer_schema

def compute_quality_metrics(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    """
    Calcula métricas de calidad por columna según el esquema:
      - n_nulls, pct_nulls
      - n_duplicates, pct_duplicates
      - n_type_mismatch, pct_type_mismatch
      - n_pattern_mismatch, pct_pattern_mismatch
    Devuelve un DataFrame de pandas.
    """
    total = len(df)
    records = []
    for col in df.columns:
        s = df[col]
        # Básicas
        n_null = int(s.isnull().sum())
        n_dup  = int(s.duplicated().sum())
        pct_null  = round(n_null/total*100, 2) if total else 0.0
        pct_dup   = round(n_dup/total*100, 2)  if total else 0.0

        # Esquema para esta columna
        col_schema   = schema.get(col, {})
        expected_type = col_schema.get('type')
        pattern       = col_schema.get('pattern')
        date_format   = col_schema.get('format')

        # Desajustes de tipo
        n_type_mismatch = 0
        for v in s.dropna():
            if expected_type == 'integer' and not isinstance(v, int):
                n_type_mismatch += 1
            elif expected_type == 'number' and not isinstance(v, (int, float)):
                n_type_mismatch += 1
            elif expected_type == 'date':
                try:
                    datetime.datetime.strptime(str(v), date_format)
                except Exception:
                    n_type_mismatch += 1
        pct_type_mismatch = round(n_type_mismatch/total*100, 2) if total else 0.0

        # Desajustes de patrón
        n_pattern_mismatch = 0
        if pattern:
            regex = re.compile(pattern)
            for v in s.dropna().astype(str):
                if not regex.match(v):
                    n_pattern_mismatch += 1
        pct_pattern_mismatch = round(n_pattern_mismatch/total*100, 2) if total else 0.0

        records.append({
            'column': col,
            'n_nulls': n_null,
            'pct_nulls': pct_null,
            'n_duplicates': n_dup,
            'pct_duplicates': pct_dup,
            'n_type_mismatch': n_type_mismatch,
            'pct_type_mismatch': pct_type_mismatch,
            'n_pattern_mismatch': n_pattern_mismatch,
            'pct_pattern_mismatch': pct_pattern_mismatch
        })
    return pd.DataFrame(records)


def compute_statistical_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada columna numérica de df calcula:
      - mean, median
      - pct10, pct25, pct75, pct90
      - std, coef_var
      - n_outliers (IQR 1.5×), pct_outliers
    Devuelve un DataFrame con estas métricas.
    """
    total = len(df)
    records = []
    for col in df.select_dtypes(include=[np.number]).columns:
        s = df[col].dropna().astype(float)
        if s.empty:
            continue
        q10, q25, q75, q90 = np.percentile(s, [10, 25, 75, 90])
        iqr = q75 - q25
        lower, upper = q25 - 1.5*iqr, q75 + 1.5*iqr
        outliers = s[(s < lower) | (s > upper)]
        n_outliers = int(len(outliers))
        records.append({
            'column': col,
            'mean': round(s.mean(), 2),
            'median': round(s.median(), 2),
            'pct10': round(q10, 2),
            'pct25': round(q25, 2),
            'pct75': round(q75, 2),
            'pct90': round(q90, 2),
            'std': round(s.std(ddof=0), 2),
            'coef_var': round(s.std(ddof=0) / s.mean() if s.mean() else 0, 2),
            'n_outliers': n_outliers,
            'pct_outliers': round(n_outliers/total*100, 2) if total else 0.0
        })
    return pd.DataFrame(records)


def validate_patterns(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    """
    Para cada columna que tenga 'pattern' en el esquema:
      - n_matches, pct_matches
      - n_mismatches, pct_mismatches
    Devuelve un DataFrame con estas métricas.
    """
    total = len(df)
    records = []
    for col, rules in schema.items():
        pattern = rules.get('pattern')
        if not pattern or col not in df.columns:
            continue
        s = df[col].dropna().astype(str)
        regex = re.compile(pattern)
        n_matches = int(s.str.match(regex).sum())
        n_mismatches = int(len(s) - n_matches)
        pct_matches = round(n_matches/total*100, 2) if total else 0.0
        pct_mismatches = round(n_mismatches/total*100, 2) if total else 0.0
        records.append({
            'column': col,
            'n_matches': n_matches,
            'pct_matches': pct_matches,
            'n_mismatches': n_mismatches,
            'pct_mismatches': pct_mismatches
        })
    return pd.DataFrame(records)


def validate_referential_integrity(
    child_df: pd.DataFrame,
    parent_df: pd.DataFrame,
    key_child: str,
    key_parent: str
) -> pd.DataFrame:
    """
    Valida que todos los valores de key_child en child_df existan en key_parent de parent_df.
    Devuelve un DataFrame con:
      - key, n_total, n_missing, pct_missing, pct_valid
    """
    total = len(child_df)
    mask_missing = ~child_df[key_child].isin(parent_df[key_parent])
    n_missing = int(mask_missing.sum())
    n_valid   = total - n_missing
    pct_missing = round(n_missing/total*100, 2) if total else 0.0
    pct_valid   = round(n_valid/total*100, 2)   if total else 0.0

    return pd.DataFrame([{
        'key': key_child,
        'n_total': total,
        'n_missing': n_missing,
        'pct_missing': pct_missing,
        'pct_valid': pct_valid
    }])


def compute_drift(
    df: pd.DataFrame,
    hist_dir: str = "reports/histograms",
    bins: int = 10,
    threshold: float = 0.0
) -> dict:
    """
    - Calcula histograma para cada columna numérica actual.
    - Carga histograma previo de hist_dir/columna.json (si existe).
    - Calcula JS distance entre ellos.
    - Guarda histograma actual en hist_dir/columna.json.
    - Devuelve dict con { columna: {'js_distance', 'drift'} }.
    """
    os.makedirs(hist_dir, exist_ok=True)
    drift_report = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        data = df[col].dropna().astype(float)
        if data.empty:
            continue

        counts, edges = np.histogram(data, bins=bins, density=True)
        prev_path = os.path.join(hist_dir, f"{col}.json")

        if os.path.exists(prev_path):
            with open(prev_path, 'r') as f:
                prev = json.load(f)
            prev_counts = np.array(prev['counts'])
            if len(prev_counts) == len(counts):
                js = jensenshannon(prev_counts, counts)
            else:
                js = None
        else:
            js = None

        with open(prev_path, 'w') as f:
            json.dump({'counts': counts.tolist(), 'edges': edges.tolist()}, f)

        # Si js es None => no drift; si js es NaN => tratamos como drift cuando threshold=0
        if js is None:
            drift_flag = False
        elif np.isnan(js):
            drift_flag = True
        else:
            drift_flag = js >= threshold

        drift_report[col] = {
            'js_distance': round(js, 4) if js is not None else None,
            'drift': drift_flag
        }
    return drift_report
def generate_diagnostics(
    df: pd.DataFrame,
    schema: dict,
    drift_report: dict = None,
    parent_df: pd.DataFrame = None,
    key_child: str = None,
    key_parent: str = None
) -> pd.DataFrame:
    """
    Combina todas las métricas y devuelve un DataFrame con diagnósticos:
      - column, issue, value, message
    """
    diag = []

    # 1. Calidad básica
    qm = compute_quality_metrics(df, schema)
    for _, row in qm.iterrows():
        col = row['column']
        if row['pct_nulls'] > 0:
            diag.append({
                'column': col,
                'issue': 'null_rate',
                'value': row['pct_nulls'],
                'message': f"{row['pct_nulls']}% de valores nulos en '{col}'. Considerar imputación o eliminación."
            })
        if row['pct_duplicates'] > 0:
            diag.append({
                'column': col,
                'issue': 'duplicate_rate',
                'value': row['pct_duplicates'],
                'message': f"{row['pct_duplicates']}% de duplicados en '{col}'. Revisar claves o filtros."
            })

    # 2. Perfil estadístico
    sp = compute_statistical_profile(df)
    for _, row in sp.iterrows():
        if row['pct_outliers'] > 0:
            diag.append({
                'column': row['column'],
                'issue': 'outliers',
                'value': row['pct_outliers'],
                'message': f"{row['pct_outliers']}% de outliers en '{row['column']}'. Revisar valores extremos."
            })

    # 3. Patrones
    pt = validate_patterns(df, schema)
    for _, row in pt.iterrows():
        if row['pct_mismatches'] > 0:
            diag.append({
                'column': row['column'],
                'issue': 'pattern_mismatch',
                'value': row['pct_mismatches'],
                'message': f"{row['pct_mismatches']}% de valores en '{row['column']}' no cumplen el patrón."
            })

    # 4. Integridad referencial (opcional)
    if parent_df is not None and key_child and key_parent:
        ri = validate_referential_integrity(df, parent_df, key_child, key_parent)
        row = ri.iloc[0]
        if row['pct_missing'] > 0:
            diag.append({
                'column': key_child,
                'issue': 'referential_integrity',
                'value': row['pct_missing'],
                'message': f"{row['pct_missing']}% de claves '{key_child}' no existen en '{key_parent}'."
            })

    # 5. Drift
    if drift_report:
        for col, info in drift_report.items():
            if info.get('drift'):
                diag.append({
                    'column': col,
                    'issue': 'drift',
                    'value': info.get('js_distance'),
                    'message': f"Drift detectado en '{col}' (JS={info.get('js_distance')})."
                })

    return pd.DataFrame(diag)


if __name__ == "__main__":
    # Prueba rápida
    from scripts.load import load_data
    schema = infer_schema('schema.yml')
    df = load_data('data/client_data.csv')
    print("Quality metrics:")
    print(compute_quality_metrics(df, schema))
    print("\nStatistical profile:")
    print(compute_statistical_profile(df))
    print("\nPattern validation:")
    print(validate_patterns(df, schema))
    print("\nReferential integrity example:")
    # parent = pd.DataFrame({'id_parent': [1,2,3]})
    # child  = pd.DataFrame({'id_child': [1,4,2]})
    # print(validate_referential_integrity(child, parent, 'id_child', 'id_parent'))
    print("\nDrift report:")
    print(compute_drift(df))

