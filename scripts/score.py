def normalize(value: float, best: float = 0.0, worst: float = 100.0) -> float:
    """
    Mapea `value` en el rango [best, worst] a un float en [1.0, 0.0].
    Si value <= best => 1.0; si >= worst => 0.0; línea recta intermedia.
    """
    if value <= best:
        return 1.0
    if value >= worst:
        return 0.0
    return round((worst - value) / (worst - best), 3)

def compute_dimensions(metrics_df, rules_df, outliers_df=None) -> dict:
    """
    Devuelve un dict con dimensiones normalizadas [0–1]:
      - completitud: 1 - avg(pct_nulls)
      - duplicados:   1 - avg(pct_duplicates)
      - consistencia: avg(success)
      - outliers:     1 - pct_outliers/100  (si outliers_df proporcionado)
    """
    # Completitud
    avg_null = metrics_df['pct_nulls'].mean() if not metrics_df.empty else 100.0
    completitud = normalize(avg_null, best=0.0, worst=100.0)

    # Duplicados
    avg_dup = metrics_df['pct_duplicates'].mean() if not metrics_df.empty else 100.0
    duplicados = normalize(avg_dup, best=0.0, worst=100.0)

    # Consistencia
    consis = rules_df['success'].mean() if not rules_df.empty else 0.0

    dims = {
        'completitud': completitud,
        'duplicados': duplicados,
        'consistencia': round(consis, 3)
    }

    # Outliers (opcional)
    if outliers_df is not None:
        pct_out = (len(outliers_df) / len(metrics_df)) * 100 if len(metrics_df) else 100.0
        dims['outliers'] = normalize(pct_out, best=0.0, worst=10.0)

    return dims

def compute_overall_score(dims: dict, weights: dict = None) -> float:
    """
    dims: dict de {dimension: valor [0–1]}
    weights: dict de {dimension: peso}, suma de pesos = 1.0
    Devuelve score_global = sum(dims[dim]*peso)
    """
    if weights is None:
        weights = {
            'completitud': 0.25,
            'duplicados':   0.25,
            'consistencia': 0.25,
            'outliers':     0.25
        }
    score = sum(dims.get(k, 0.0) * weights.get(k, 0.0) for k in dims)
    return round(score, 3)
