# Compilación de APK con Docker en Windows

Este directorio contiene los archivos necesarios para compilar el APK de SiKIdle usando Docker en Windows.

## Requisitos

1. **Docker Desktop** instalado y funcionando
   - Descargar desde: https://www.docker.com/products/docker-desktop
   - Asegúrate de que Docker esté ejecutándose

2. **Git Bash** o **PowerShell** (recomendado)

## Métodos de Compilación

### Método 1: Script Automático (Recomendado)

```bash
# Ejecutar el script de build automático
cd releases/v0.1.0
python build_all.py --platforms android
```

### Método 2: Script Batch Manual

```bash
# Ir al directorio de Android
cd releases/v0.1.0/android

# Ejecutar el script batch
build_android_docker.bat
```

### Método 3: Comandos Docker Manuales

```bash
# Ir al directorio de Android
cd releases/v0.1.0/android

# Construir la imagen Docker
docker build -t sikilde-android .

# Crear directorio de salida
mkdir dist

# Compilar el APK
docker run --rm -v "%cd%\dist:/app/bin" sikilde-android
```

## Estructura de Archivos

```
android/
├── Dockerfile              # Configuración de Docker
├── buildozer.spec          # Configuración de Buildozer
├── build_android_docker.bat # Script batch para Windows
├── dist/                   # APKs generados (se crea automáticamente)
└── README-Docker.md        # Este archivo
```

## Solución de Problemas

### Error: "Docker no encontrado"
- Instala Docker Desktop
- Reinicia tu terminal después de la instalación
- Verifica con: `docker --version`

### Error: "Permission denied"
- En Windows, ejecuta el terminal como administrador
- Asegúrate de que Docker Desktop esté ejecutándose

### Error: "No space left on device"
- Limpia imágenes Docker no utilizadas: `docker system prune`
- Libera espacio en disco

### APK no se genera
- Revisa los logs de Docker
- Verifica que el directorio `dist` se haya creado
- Comprueba que no haya errores en `buildozer.spec`

## Notas Importantes

1. **Primera compilación**: Puede tardar 20-30 minutos debido a la descarga de dependencias
2. **Compilaciones posteriores**: Serán más rápidas gracias al cache de Docker
3. **Tamaño de imagen**: La imagen Docker ocupa aproximadamente 2-3 GB
4. **APK generado**: Se encuentra en `dist/SiKIdle-v0.1.0-android.apk`

## Alternativas

Si Docker no funciona, puedes usar:

1. **GitHub Actions**: Push tu código y usa el workflow automático
2. **WSL2**: Instala Ubuntu en Windows y usa Buildozer nativo
3. **Máquina virtual**: Ubuntu en VirtualBox/VMware

## Soporte

Si tienes problemas:
1. Revisa los logs de Docker
2. Verifica que Docker Desktop esté actualizado
3. Consulta la documentación de Buildozer: https://buildozer.readthedocs.io/
