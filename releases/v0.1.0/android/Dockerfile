# Dockerfile para compilar APK de SiKIdle en Windows
FROM kivy/buildozer:latest

# Instalar dependencias adicionales
RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Configurar JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY ../../../src ./src
COPY buildozer.spec .

# Configurar permisos
RUN chmod +x /usr/bin/buildozer

# Comando por defecto
CMD ["buildozer", "android", "debug"]
