import pandas as pd
from scripts.rules import infer_schema
from scripts.metrics import validate_patterns

def test_validate_patterns():
    data = {
        'email': ['good@mail.com', 'bad-mail', 'also@good.org'],
        'other': ['x', 'y', 'z']
    }
    df = pd.DataFrame(data)
    schema = {
        'email': {'pattern': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'}
    }
    pat_df = validate_patterns(df, schema)
    # Only one row for 'email'
    assert len(pat_df) == 1
    row = pat_df.iloc[0]
    assert row['column'] == 'email'
    assert row['n_matches'] == 2
    assert row['n_mismatches'] == 1
    assert row['pct_matches'] == round(2/3*100, 2)
