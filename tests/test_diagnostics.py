import pandas as pd
from scripts.rules import infer_schema
from scripts.metrics import generate_diagnostics

def test_generate_diagnostics():
    # Data simple con null y duplicado
    data = {'a': [1,1,None], 'b': ['x','bad','x']}
    df = pd.DataFrame(data)
    schema = {
        'a': {'type': 'integer'},
        'b': {'type': 'string', 'pattern': r'^x$'}
    }
    diag = generate_diagnostics(df, schema, drift_report=None)
    issues = diag.issue.tolist()
    assert 'null_rate' in issues
    assert 'duplicate_rate' in issues
    assert 'pattern_mismatch' in issues
