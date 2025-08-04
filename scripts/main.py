import os
import click
import pandas as pd

from scripts.load import load_data
from scripts.metrics import compute_quality_metrics
from scripts.rules import load_rules, apply_business_rules
from scripts.io_utils import save_csv, save_json
from scripts.score import compute_dimensions, compute_overall_score
from scripts.render_report import render_html

@click.command()
@click.option('--input',  'input_csv',  required=True, help='Ruta al CSV de datos')
@click.option('--rules',  'rules_yml',  required=True, help='Ruta a rules.yml')
@click.option('--outdir','outdir',      default='reports', help='Carpeta de salida')
def main(input_csv, rules_yml, outdir):
    # 1. Carga datos
    df = load_data(input_csv)

    # 2. Métricas básicas
    mdf = compute_quality_metrics(df)
    save_csv(mdf, os.path.join(outdir, 'quality_metrics.csv'))

    # 3. Carga reglas y aplica
    rules = load_rules(rules_yml)
    rdf = apply_business_rules(df, rules)
    save_csv(rdf, os.path.join(outdir, 'business_rules.csv'))

    # 4. Detecta outliers si existe el módulo
    try:
        from scripts.outliers import detect_outliers
        odf = detect_outliers(df)
    except ImportError:
        odf = None

    # 5. Calcula dimensiones y score global
    dims = compute_dimensions(mdf, rdf, odf)
    score = compute_overall_score(dims)

    # 6. Determina semáforo
    if score >= 0.85:
        semaforo = 'VERDE'
    elif score >= 0.70:
        semaforo = 'AMBAR'
    else:
        semaforo = 'ROJO'

    # 7. Exporta summary.json
    summary = {
        'dimensions': dims,
        'score_global': score,
        'semaforo': semaforo
    }
    save_json(summary, os.path.join(outdir, 'summary.json'))

    # 8. Renderiza página HTML con semáforo
    render_html(
        json_path=os.path.join(outdir, 'summary.json'),
        template_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'templates')),
        output_path=os.path.join(outdir, 'index.html')
    )

    # 9. Mensaje final
    click.echo(f"✅ Reportes generados en {outdir}/ (Score: {score}, Semáforo: {semaforo})")

if __name__ == '__main__':
    main()
