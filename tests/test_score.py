import pandas as pd
from scripts.score import normalize, compute_dimensions, compute_overall_score

def test_normalize_bounds():
    assert normalize(0, 0, 100) == 1.0
    assert normalize(100, 0, 100) == 0.0

def test_normalize_middle():
    # 50% en rango 0–100 => (100-50)/100 = 0.5
    assert normalize(50, 0, 100) == 0.5

def test_compute_dimensions_minimal():
    # DataFrames vacíos => completitud=0, duplicados=0, consistencia=0
    dims = compute_dimensions(pd.DataFrame(), pd.DataFrame())
    assert dims['completitud'] == 0.0
    assert dims['duplicados'] == 0.0
    assert dims['consistencia'] == 0.0

def test_compute_dimensions_with_data():
    metrics = pd.DataFrame({'pct_nulls':[10,20], 'pct_duplicates':[5,5]})
    rules = pd.DataFrame({'success':[True, False, True]})
    dims = compute_dimensions(metrics, rules)
    # completitud = normalize(avg_null=15) = (100-15)/100 = 0.85
    assert dims['completitud'] == 0.85
    # duplicados = normalize(avg_dup=5) = 0.95
    assert dims['duplicados'] == 0.95
    # consistencia = avg([1,0,1]) = 0.667
    assert round(dims['consistencia'],3) == 0.667

def test_compute_overall_score_default_weights():
    dims = {'completitud':1, 'duplicados':0.5, 'consistencia':0, 'outliers':0.5}
    score = compute_overall_score(dims)
    # =1*0.25 +0.5*0.25+0*0.25+0.5*0.25 = 0.5
    assert score == 0.5

