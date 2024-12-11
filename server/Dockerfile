# Usa una imagen base de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de código fuente al contenedor
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que utilizará el servidor (65432 por defecto)
EXPOSE 65432

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
