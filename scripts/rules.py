import os
import yaml
import pandas as pd

def load_rules(path: str):
    """
    Lee el fichero YAML de reglas y devuelve la lista de reglas.
    """
    with open(path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return cfg.get('rules', [])

def apply_business_rules(df: pd.DataFrame, rules) -> pd.DataFrame:
    """
    Aplica cada regla configurada:
      - not_null, unique, range, non_empty_string
    Devuelve un DataFrame con columnas: rule, column, success, observed.
    """
    records = []
    for rule in rules:
        col = rule['column']
        cols = df.columns if col == 'any' else [col]
        for c in cols:
            s = df[c]
            t = rule['type']
            if t == 'not_null':
                n = s.isnull().sum(); ok = (n==0); obs = f"{n} nulls"
            elif t == 'unique':
                n = s.duplicated().sum(); ok = (n==0); obs = f"{n} duplicates"
            elif t == 'range':
                lo, hi = rule['min'], rule['max']
                below = (s < lo).sum(); above = (s > hi).sum()
                ok = (below==0 and above==0)
                obs = f"{below}<{lo}, {above}>{hi}"
            elif t == 'non_empty_string':
                empty = s.astype(str).str.strip().eq('').sum()
                ok = (empty==0); obs = f"{empty} empty"
            else:
                ok, obs = True, ''
            records.append({
                'rule': rule['name'],
                'column': c,
                'success': ok,
                'observed': obs
            })
    return pd.DataFrame(records)

def infer_schema(schema_path: str) -> dict:
    """
    Carga schema.yml y devuelve un dict con las reglas:
    {
      'edad': {'type':'integer','range':[18,99], ...},
      ...
    }
    """
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
    schema = content.get('columns')
    if not isinstance(schema, dict):
        raise ValueError("schema.yml debe tener sección 'columns'")
    return schema

