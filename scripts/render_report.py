import json
import os
from jinja2 import Environment, FileSystemLoader

def render_html(json_path: str, template_dir: str, output_path: str):
    # 1. Carga el summary
    with open(json_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    dims = summary['dimensions']
    score = summary['score_global']
    sem = summary['semaforo']

    # 2. Semáforo: símbolo y clase CSS
    sem_map = {
        'VERDE':  ('✔', 'verde'),
        'AMBAR':  ('⚠', 'ambar'),
        'ROJO':   ('✖', 'rojo')
    }
    sym, cls = sem_map.get(sem, ('?', 'rojo'))

    # 3. Colores por dimensión
    default_colors = {
      'completitud': '#28a745',
      'duplicados':   '#17a2b8',
      'consistencia': '#ffc107',
      'outliers':     '#dc3545'
    }

    # 4. Monta el entorno Jinja
    env = Environment(loader=FileSystemLoader(template_dir))
    tpl = env.get_template('index.html')

    # 5. Genera el HTML
    html = tpl.render(
        semaforo_symbol=sym,
        semaforo_lower=cls,
        score_global=score,
        dimensions=dims,
        colors=default_colors
    )

    # 6. Guarda el output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
