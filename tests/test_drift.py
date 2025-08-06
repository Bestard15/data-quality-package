import pandas as pd
import numpy as np
import os
import shutil
from scripts.metrics import compute_drift

def test_compute_drift(tmp_path):
    # Directorio limpio
    hist_dir = tmp_path/"hist"
    # Primer df
    df1 = pd.DataFrame({'x': [1,2,3,4,5]})
    rpt1 = compute_drift(df1, hist_dir=str(hist_dir), bins=5, threshold=0.0)
    assert rpt1['x']['js_distance'] is None
    assert rpt1['x']['drift'] is False

    # Cambia distribución
    df2 = pd.DataFrame({'x': [100,200,300,400,500]})
    rpt2 = compute_drift(df2, hist_dir=str(hist_dir), bins=5, threshold=0.0)
    # Ahora hay hist previo y js_distance calculado
    assert isinstance(rpt2['x']['js_distance'], float)
    assert rpt2['x']['drift'] is True
