@echo off
echo ==================================================
echo  SiKIdle v0.1.0 - Modern Android Build
echo  Stack: Python 3.11 + Kivy 2.3.1 + JDK 17
echo ==================================================

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está instalado o no está ejecutándose
    echo Asegúrate de que Docker Desktop esté funcionando
    pause
    exit /b 1
)

echo [INFO] Docker detectado correctamente

REM Verificar que existe el código fuente
if not exist "..\..\..\src\main.py" (
    echo [ERROR] No se encuentra el código fuente en ..\..\..\src\main.py
    echo Asegúrate de ejecutar este script desde releases\packaging\android\
    pause
    exit /b 1
)

echo [INFO] Código fuente verificado

REM Crear directorio de salida
if not exist "dist" mkdir dist

REM Limpiar builds anteriores para evitar problemas de cache
echo [INFO] Limpiando builds anteriores...
if exist ".buildozer" rmdir /s /q .buildozer

echo [INFO] Construyendo imagen Docker moderna...
docker build -t sikidle-android-modern -f Dockerfile ../../.. --no-cache

if %errorlevel% neq 0 (
    echo [ERROR] Error al construir la imagen Docker
    pause
    exit /b 1
)

echo [INFO] Compilando APK con Docker (Python 3.11 + Kivy 2.3.1)...
docker run --rm -v "%cd%\dist:/app/bin" sikidle-android-modern

if %errorlevel% neq 0 (
    echo [ERROR] Error al compilar el APK
    pause
    exit /b 1
)

echo [SUCCESS] Compilación completada!

REM Buscar y renombrar APK
for %%f in (dist\*.apk) do (
    echo [INFO] APK encontrado: %%f
    copy "%%f" "dist\SiKIdle-v0.1.0-android-modern.apk" >nul
    echo [SUCCESS] APK disponible como: SiKIdle-v0.1.0-android-modern.apk
)

echo ==================================================
echo  Build Android Moderno Completado
echo ==================================================
echo [INFO] Stack utilizado:
echo   - Python 3.11.13
echo   - Kivy 2.3.1
echo   - PyJNIus (latest compatible)
echo   - JDK 17 (requerido para Android Gradle Plugin 8.x)
echo   - Target SDK 35 (Google Play 2025)
echo   - Min SDK 23 (Android 6.0+)
echo   - NDK r25b
echo   - Arquitecturas: arm64-v8a, armeabi-v7a, x86_64 (emuladores)
echo ==================================================
echo [INFO] APK disponible en: %cd%\dist\
pause
