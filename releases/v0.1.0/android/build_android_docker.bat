@echo off
echo ==================================================
echo  SiKIdle v0.1.0 - Android Build con Docker
echo ==================================================

REM Verificar que Docker esté instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [INFO] Docker detectado correctamente

REM Crear directorio de salida si no existe
if not exist "dist" mkdir dist

echo [INFO] Construyendo imagen Docker...
docker build -t sikilde-android .

if %errorlevel% neq 0 (
    echo [ERROR] Error al construir la imagen Docker
    pause
    exit /b 1
)

echo [INFO] Compilando APK...
docker run --rm -v "%cd%\dist:/app/bin" sikilde-android

if %errorlevel% neq 0 (
    echo [ERROR] Error al compilar el APK
    pause
    exit /b 1
)

echo [SUCCESS] APK compilado exitosamente!
echo [INFO] Archivo disponible en: %cd%\dist\

REM Buscar el APK generado y renombrarlo
for %%f in (dist\*.apk) do (
    echo [INFO] APK encontrado: %%f
    copy "%%f" "dist\SiKIdle-v0.1.0-android.apk"
    echo [SUCCESS] APK renombrado a: SiKIdle-v0.1.0-android.apk
)

echo ==================================================
echo  Build Android Completado
echo ==================================================
pause
