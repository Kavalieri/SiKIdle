# SiKIdle

**SiKIdle** es un videojuego incremental (idle clicker) desarrollado en Python con Kivy, completamente asistido por inteligencia artificial. El objetivo es construir, automatizar y escalar una fábrica de producción que genera recursos incluso cuando no estás jugando.

## Características

- Interfaz moderna con Kivy (sin archivos `.kv`)
- Persistencia de datos en SQLite
- Guardado automático por usuario
- Modular, limpio y escalable
- Validación con `ruff` y `mypy`
- Compatible con compilación `.exe` y `.apk`

## Ejecutar en local

```bash
poetry install
poetry run python src/main.py
```

## Compilar para distribución

- **Windows**: PyInstaller
- **Android**: Buildozer

## Estado

- 🛠️ Versión: `0.1.0-alpha`
- 🚧 En desarrollo activo

---

© Clan SiK - 2025
