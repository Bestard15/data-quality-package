import os
import click
from scripts.load import load_data
from scripts.rules import infer_schema
from scripts.metrics import (
    compute_quality_metrics,
    compute_statistical_profile,
    validate_patterns,
    validate_referential_integrity,
    compute_drift,
    generate_diagnostics
)
from scripts.io_utils import save_csv, save_json, archive_reports

@click.command()
@click.option('--input',    'input_csv',  required=True, help='Ruta al CSV de datos')
@click.option('--rules',    'rules_yml',  required=True, help='Ruta a schema.yml o rules.yml')
@click.option('--outdir',   'outdir',     default='reports', help='Carpeta de salida')
@click.option('--parent',   'parent_csv', default=None,    help='(Opcional) CSV de tabla padre para integridad referencial')
@click.option('--key-child','key_child', default=None,    help='Nombre columna en child para integridad')
@click.option('--key-parent','key_parent',default=None,    help='Nombre columna en parent para integridad')
@click.option('--drift-th', 'drift_th',  default=0.2,      help='Umbral JS para drift', type=float)
def main(input_csv, rules_yml, outdir, parent_csv, key_child, key_parent, drift_th):
    os.makedirs(outdir, exist_ok=True)

    # 1. Carga datos y esquema
    df = load_data(input_csv)
    schema = infer_schema(rules_yml)

    # 2. Métricas de calidad
    qm = compute_quality_metrics(df, schema)
    save_csv(qm, os.path.join(outdir, 'quality_metrics.csv'))

    # 3. Perfil estadístico
    sp = compute_statistical_profile(df)
    save_csv(sp, os.path.join(outdir, 'statistical_profile.csv'))

    # 4. Validación de patrones
    pt = validate_patterns(df, schema)
    save_csv(pt, os.path.join(outdir, 'pattern_validation.csv'))

    # 5. Integridad referencial (si se proporcionan parent y claves)
    ri = None
    if parent_csv and key_child and key_parent:
        parent_df = load_data(parent_csv)
        ri = validate_referential_integrity(df, parent_df, key_child, key_parent)
        save_csv(ri, os.path.join(outdir, 'referential_integrity.csv'))

    # 6. Detección de drift
    drift = compute_drift(df, hist_dir=os.path.join(outdir, 'histograms'), threshold=drift_th)
    save_json(drift, os.path.join(outdir, 'drift_report.json'))

    # 7. Generar diagnósticos
    diag = generate_diagnostics(df, schema, drift_report=drift,
                                parent_df=parent_df if ri is not None else None,
                                key_child=key_child, key_parent=key_parent)
    save_csv(diag, os.path.join(outdir, 'diagnostics.csv'))

    # 8. Archivo summary con score y semáforo
    # Ejemplo simple: semáforo verde si <5% nulls global, ámbar si <10%, rojo si más
    global_null = qm['pct_nulls'].mean()
    if global_null < 5:
        semaforo = 'VERDE'
    elif global_null < 10:
        semaforo = 'AMBAR'
    else:
        semaforo = 'ROJO'
    summary = {
        'overall_null_rate': round(global_null, 2),
        'semaforo': semaforo
    }
    save_json(summary, os.path.join(outdir, 'summary.json'))

    # 9. Archivado histórico
    archive_path = archive_reports(src_reports=outdir, archive_root=os.path.join(outdir, 'archive'))
    click.echo(f"🔖 Reports archived to: {archive_path}")

    # 10. Mensaje final
    click.echo(f"✅ Reportes generados en {outdir}/ (NullRate: {global_null}%, Semáforo: {semaforo})")

if __name__ == '__main__':
    main()

