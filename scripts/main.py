import os
import subprocess
import datetime
import click
import pandas as pd

from scripts.load import load_data
from scripts.rules import infer_schema, load_rules, apply_business_rules
from scripts.metrics import (
    compute_quality_metrics,
    compute_statistical_profile,
    validate_patterns,
)
from scripts.io_utils import save_csv, save_json, archive_reports, write_manifest
from scripts.alerts import send_slack
from scripts.remediation import apply_remediation

@click.command()
@click.option('--input',  'input_csv',  required=True, help='Ruta al CSV de datos')
@click.option('--rules',  'rules_yml',  required=True, help='Ruta a rules.yml')
@click.option('--outdir','outdir',      default='reports', help='Carpeta de salida')
@click.option(
    '--remediate',
    is_flag=True,
    help='Aplicar correcciones automáticas según reglas configuradas'
)
def main(input_csv, rules_yml, outdir, remediate):
    # 0. Prepara directorios
    os.makedirs(outdir, exist_ok=True)

    # 0.1 Estado incremental
    state_file = os.path.join('.state', 'last_run.txt')
    last_run = None
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            last_run = f.read().strip()

    # 1. Carga datos incremental
    df = load_data(input_csv, since=last_run)

    # 2. Carga esquema y reglas
    schema = infer_schema(rules_yml)
    rules = load_rules(rules_yml)

    # 3. Métricas de calidad básicas
    mdf = compute_quality_metrics(df, schema)
    save_csv(mdf, os.path.join(outdir, 'quality_metrics.csv'))

    # 3.1 Remediación automática
    if remediate:
        df_clean, log_df = apply_remediation(df, schema)
        save_csv(df_clean, os.path.join(outdir, 'cleaned_data.csv'))
        save_csv(log_df, os.path.join(outdir, 'remediation_log.csv'))
        click.echo('🧹 Remediación aplicada: cleaned_data.csv y remediation_log.csv generados')
        df = df_clean
        # (Opcional) Recalcular métricas
        mdf = compute_quality_metrics(df, schema)

    # 4. Validaciones de negocio
    rdf = apply_business_rules(df, rules)
    save_csv(rdf, os.path.join(outdir, 'business_rules.csv'))

    # 5. Perfil estadístico
    spf = compute_statistical_profile(df)
    save_csv(spf, os.path.join(outdir, 'statistical_profile.csv'))

    # 6. Validación de patrones
    pvf = validate_patterns(df, schema)
    save_csv(pvf, os.path.join(outdir, 'pattern_validation.csv'))

    # 7. Alertas Slack
    for _, row in rdf.iterrows():
        if row.get('issue') == 'null_rate' and row.get('value', 0) > 20:
            send_slack(f":warning: Null Rate alto en '{row['column']}': {row['value']}%")

    # 8. Versionado y linaje
    try:
        schema_version = subprocess.check_output(
            ['git', 'describe', '--tags'], cwd=os.getcwd()
        ).strip().decode()
    except Exception:
        schema_version = 'unknown'
    write_manifest(outdir, input_csv, schema_version, row_count=len(df))
    click.echo(f"🔖 Manifest generado con version: {schema_version}")

    # 9. Generar summary y semáforo
    avg_null = mdf['pct_nulls'].mean()
    score = round(100 - avg_null, 2)
    semaforo = 'VERDE' if score >= 85 else 'AMBAR' if score >= 70 else 'ROJO'
    summary = {
        'dimensions': {},          # opcional: compute_dimensions(mdf, rdf, ...)
        'score_global': score,
        'semaforo': semaforo
    }
    save_json(summary, os.path.join(outdir, 'summary.json'))

    # 10. Render HTML (si existe)
    try:
        from scripts.render_report import render_html
        render_html(
            json_path=os.path.join(outdir, 'summary.json'),
            template_dir=os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.pardir, 'templates')
            ),
            output_path=os.path.join(outdir, 'index.html')
        )
    except ImportError:
        pass

    # 11. Archivado histórico
    archive_dest = archive_reports(outdir)
    click.echo(f"🔖 Reports archived to: {archive_dest}")
    click.echo(f"✅ Reportes generados en {outdir}/ (Score: {score}, Semáforo: {semaforo})")

    # 12. Actualizar last_run timestamp
    new_run = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, 'w') as f:
        f.write(new_run)
    click.echo(f"🕒 Updated last_run to {new_run}")


if __name__ == '__main__':
    main()
