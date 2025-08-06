import pandas as pd
from scripts.metrics import validate_referential_integrity

def test_validate_referential_integrity():
    # Tabla padre con IDs válidos
    parent = pd.DataFrame({'id_parent': [1,2,3,4]})
    # Tabla hija, con un id faltante (5)
    child  = pd.DataFrame({'id_child': [1,2,5,3,2]})

    result = validate_referential_integrity(
        child_df=child,
        parent_df=parent,
        key_child='id_child',
        key_parent='id_parent'
    )
    row = result.iloc[0]
    assert row['key'] == 'id_child'
    assert row['n_total'] == 5
    assert row['n_missing'] == 1
    assert row['pct_missing'] == round(1/5*100, 2)
    assert row['pct_valid']   == round(4/5*100, 2)
