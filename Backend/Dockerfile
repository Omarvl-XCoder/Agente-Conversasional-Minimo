# 1. Imagen base oficial ligera de Python
FROM python:3.11-slim

# 2. Evitar que Python escriba archivos .pyc y forzar salida inmediata en terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar e instalar requerimientos primero (para aprovechar el caché de Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del backend
COPY . /app/

# 6. Puerto que expondrá el servicio
EXPOSE 8000

# 7. Comando de arranque del servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]