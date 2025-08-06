import pandas as pd
import numpy as np
from scripts.metrics import compute_statistical_profile

def test_statistical_profile_basic():
    data = {
        'a': [1, 2, 3, 4, 100],  # 100 es un outlier
        'b': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    stats = compute_statistical_profile(df)

    # Columna 'a'
    row_a = stats.loc[stats.column=='a'].iloc[0]
    assert row_a['mean'] == round(np.mean(data['a']), 2)
    assert row_a['n_outliers'] == 1

    # Columna 'b'
    row_b = stats.loc[stats.column=='b'].iloc[0]
    assert row_b['mean'] == round(np.mean(data['b']), 2)
    assert row_b['n_outliers'] == 0

