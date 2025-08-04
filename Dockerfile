# 1. Partimos de Python slim
FROM python:3.11-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiamos archivos de requisitos (si los tienes)
#    Si no, instalamos directamente pandas, etc.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos la aplicación
COPY . .

# 5. Exponemos puerto si tuvieras servicio web (no es el caso aquí)
# EXPOSE 8000

# 6. Comando por defecto: lanza el auditor semáforo
ENTRYPOINT ["python", "-m", "scripts.main", "--input", "data/client_data.csv", "--rules", "rules.yml", "--outdir", "reports"]
