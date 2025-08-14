# Dockerfile moderno para SiKIdle con Python 3.11 y JDK 17
FROM ubuntu:22.04

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Configurar variables de entorno para Android con JDK 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Instalar dependencias del sistema con Python 3.11 y JDK 17
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    build-essential \
    libssl-dev \
    libffi-dev \
    libltdl-dev \
    cmake \
    autotools-dev \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crear enlaces simbólicos para python3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3
RUN ln -sf /usr/bin/python3.11 /usr/bin/python

# Instalar pip para Python 3.11 manualmente
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.11 get-pip.py \
    && rm get-pip.py \
    && python3.11 -m pip install --upgrade pip setuptools wheel

# Instalar stack moderno para Android con versiones específicas
RUN python3.11 -m pip install \
    buildozer==1.5.0 \
    cython==3.0.10 \
    virtualenv==20.26.6

# Crear directorio de trabajo
WORKDIR /app

# Copiar buildozer.spec
COPY releases/packaging/android/buildozer.spec .

# Copiar código fuente completo
COPY src ./

# Comando para compilar (aceptar todas las licencias automáticamente)
CMD ["sh", "-c", "yes | buildozer android debug"]
