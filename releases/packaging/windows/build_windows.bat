@echo off
echo ==================================================
echo  SiKIdle v0.1.0 - Modern Windows Build
echo  Stack: Python 3.11 + Kivy 2.3.1 + PyInstaller
echo ==================================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo Instala Python 3.11+ desde https://python.org
    pause
    exit /b 1
)

echo [INFO] Python detectado correctamente

REM Verificar que existe el código fuente
if not exist "..\..\..\src\main.py" (
    echo [ERROR] No se encuentra el código fuente en ..\..\..\src\main.py
    echo Asegúrate de ejecutar este script desde releases\packaging\windows\
    pause
    exit /b 1
)

echo [INFO] Código fuente verificado

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias de build
echo [INFO] Instalando dependencias de build...
pip install pyinstaller==6.3.0
pip install kivy==2.3.1
pip install pillow
pip install upx-windows-binaries

REM Instalar dependencias del juego
echo [INFO] Instalando dependencias del juego...
pip install -r ..\..\..\requirements.txt 2>nul || echo [WARNING] No se encontró requirements.txt

REM Crear directorio de salida
if not exist "dist" mkdir dist

REM Limpiar builds anteriores
echo [INFO] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist\SiKIdle-v0.1.0-Windows-Modern" rmdir /s /q "dist\SiKIdle-v0.1.0-Windows-Modern"

REM Crear icono si no existe
if not exist "..\..\..\src\assets\icon.ico" (
    echo [INFO] Creando icono placeholder...
    if not exist "..\..\..\src\assets" mkdir "..\..\..\src\assets"
    echo. > "..\..\..\src\assets\icon.ico"
)

echo [INFO] Compilando ejecutable con PyInstaller...
echo [INFO] Configuración:
echo   - Modo: One Directory (más rápido)
echo   - Compresión: UPX habilitado
echo   - Consola: Deshabilitada (GUI pura)
echo   - Assets: Incluidos automáticamente
echo   - Optimizaciones: Máximas

pyinstaller sikidle.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo [ERROR] Error al compilar el ejecutable
    pause
    exit /b 1
)

echo [SUCCESS] Compilación completada!

REM Verificar que se creó el ejecutable
if exist "dist\SiKIdle-v0.1.0-Windows-Modern\SiKIdle.exe" (
    echo [SUCCESS] Ejecutable creado: SiKIdle.exe
    
    REM Crear archivo de información
    echo SiKIdle v0.1.0 - Windows Modern Build > "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo. >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo Stack utilizado: >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo - Python 3.11+ >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo - Kivy 2.3.1 >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo - PyInstaller 6.3.0 >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo - UPX Compression >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo. >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    echo Fecha de build: %date% %time% >> "dist\SiKIdle-v0.1.0-Windows-Modern\BUILD_INFO.txt"
    
    REM Mostrar tamaño del ejecutable
    for %%A in ("dist\SiKIdle-v0.1.0-Windows-Modern\SiKIdle.exe") do (
        set size=%%~zA
        set /a size_mb=!size!/1024/1024
        echo [INFO] Tamaño del ejecutable: !size_mb! MB
    )
    
) else (
    echo [ERROR] No se pudo crear el ejecutable
    pause
    exit /b 1
)

echo ==================================================
echo  Build Windows Moderno Completado
echo ==================================================
echo [INFO] Stack utilizado:
echo   - Python 3.11+
echo   - Kivy 2.3.1 (Framework UI moderno)
echo   - PyInstaller 6.3.0 (Empaquetador profesional)
echo   - UPX Compression (Reducción de tamaño)
echo ==================================================
echo [INFO] Ejecutable disponible en:
echo   %cd%\dist\SiKIdle-v0.1.0-Windows-Modern\
echo.
echo [INFO] Para probar: ejecuta SiKIdle.exe
echo [INFO] Para distribuir: comprime toda la carpeta
echo ==================================================

REM Preguntar si ejecutar el juego
set /p run_game="¿Ejecutar el juego ahora? (s/n): "
if /i "%run_game%"=="s" (
    echo [INFO] Ejecutando SiKIdle...
    start "" "dist\SiKIdle-v0.1.0-Windows-Modern\SiKIdle.exe"
)

pause
