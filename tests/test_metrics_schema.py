import pandas as pd
from scripts.rules import infer_schema
from scripts.metrics import compute_quality_metrics

def test_type_and_pattern_mismatch():
    # Data de prueba: un mal tipo y un mal email
    data = {
        'edad': [25, 'treinta', 40],
        'email': ['a@b.com', 'invalid-email', 'c@d.com']
    }
    df = pd.DataFrame(data)

    schema = {
        'edad': {'type': 'integer'},
        'email': {'type': 'string', 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'}
    }

    mdf = compute_quality_metrics(df, schema)

    # Para la columna 'edad': 1 tipo mismatched
    row_edad = mdf.loc[mdf.column == 'edad'].iloc[0]
    assert row_edad['n_type_mismatch'] == 1
    assert row_edad['pct_type_mismatch'] == round(1/3*100, 2)

    # Para la columna 'email': 1 pattern mismatched
    row_email = mdf.loc[mdf.column == 'email'].iloc[0]
    assert row_email['n_pattern_mismatch'] == 1
    assert row_email['pct_pattern_mismatch'] == round(1/3*100, 2)
