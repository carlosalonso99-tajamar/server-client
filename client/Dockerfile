# Usa una imagen base de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de código fuente al contenedor
COPY . /app

# Instalar las dependencias necesarias (si las tienes en un requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt



# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
