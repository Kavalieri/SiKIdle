# 🧠 GitHub Copilot Instructions

Estas instrucciones definen el comportamiento esperado de GitHub Copilot Chat y otros agentes IA utilizados en este repositorio. Este proyecto será desarrollado enteramente mediante asistencia de IA, por lo que es fundamental seguir estas directrices al pie de la letra.

---

## 🎯 Objetivo General

Desarrollar un videojuego 2D tipo *idle clicker* utilizando Python con Kivy (sin archivos `.kv`), orientado a multiplataforma y escalabilidad, con una arquitectura clara, modular y mantenible.

---

## ✅ Comportamiento Esperado del Agente IA

- Sé **crítico, no complaciente**. Cuestiona y mejora las soluciones propuestas.
- **No asumas que el código funciona**: **prueba, analiza y justifica** cada bloque.
- Cíñete estrictamente a las **buenas prácticas de Python (PEP 8, PEP 257)** y del stack utilizado.
- **No escribas código en la raíz del proyecto**. Respeta la arquitectura del repositorio.
- Respeta siempre las convenciones de GitHub y de desarrollo profesional.
- Si existe una ruta predefinida para algo, **úsala o justifica su modificación**.
- **Toda la documentación y comentarios estarán en español.**
- **Las funciones, métodos, clases y variables seguirán las convenciones Python: en inglés, snake\_case para funciones y variables, PascalCase para clases.**

---

## 🗂 Estructura esperada del proyecto

- `src/`: todo el código fuente.
  - `core/`: lógica del juego.
  - `ui/`: interfaz y widgets.
  - `utils/`: guardado, paths, helpers.
  - `assets/`: solo lectura, recursos.
- `dev-tools/`: documentación estructurada.
  - `scripts/`: scripts de desarrollo y automatización.
  - `tests/`: pruebas unitarias y de integración.
- `docs/`: documentación estructurada.
  - `resumen/`: resúmenes de cada bloque de trabajo (ver abajo).
  - `checklist/`: listas de tareas por bloque o proceso.
- `.github/`: instrucciones para agentes IA, acciones, plantillas.
- `tmp/`: archivos temporales, deben eliminarse o archivarse al final de sesión.
- `ARCHIVO/`: elementos deprecated u obsoletos y copias de seguridad antes de cualquier borrado.

---

## 🧾 Documentación automática por la IA

### 📋 `docs/checklist/`

- Antes de iniciar cualquier proceso mayor (clase nueva, refactor, sistema...), genera un checklist con:
  - Fecha y hora (timestamp).
  - Objetivo del bloque.
  - Tareas desglosadas (1 por línea).
  - Casillas para marcar (usando `- [ ]`).
- Actualiza el estado de ese checklist a medida que avances.

### 🧠 `docs/resumen/`

- Al finalizar cada bloque de trabajo (por checklist o fase), genera un resumen técnico con:
  - Fecha y hora.
  - Descripción detallada del trabajo realizado.
  - Archivos modificados.
  - Decisiones tomadas y su justificación.
  - Elementos pendientes, si los hay.

### 📚 `README.md` en cada directorio importante

- Generar un `README.md` por cada subdirectorio (`core`, `ui`, `utils`, etc.) con:
  - Propósito del módulo.
  - Lista de clases o scripts.
  - Breve explicación de cómo interactúan.

### 📌 `README.md` raíz del proyecto

- Mantener actualizado con:
  - Descripción general.
  - Stack técnico.
  - Estructura de carpetas.
  - Instrucciones para ejecución y desarrollo.

### 👥 `CONTRIBUTING.md`

- Crear y mantener actualizado con:
  - Requisitos para colaborar.
  - Cómo clonar, ejecutar, testear.
  - Normas de estilo de código.
  - Enlaces a herramientas recomendadas.
  - Flujo de trabajo esperado (ramas, PR, validación).

---

## ⚠️ Restricciones

- 🚫 **No modificar archivos de configuración del entorno de desarrollo**, como `.vscode/settings.json`.
- 🚫 **No generar código experimental sin justificarlo primero.**
- 🚫 **No introducir dependencias sin declararlas en **``** o **``**.**
- 🚫 **Nunca empujar directamente a **``**. Siempre trabajar en ramas nuevas y usar PR para merge.**
- 🚫 **No dejar archivos temporales o pruebas en raíz. Usar **``** y limpiar al finalizar.**

---

## 🛠️ Herramientas y convenciones activas

- 🐍 Python 3.11+
- 🪟 Kivy (sin archivos `.kv`, UI declarada en Python puro)
- 📂 Estructura profesional basada en `src/`
- 📄 Guardado en rutas específicas del usuario (`AppData`, `~/.config`, etc.)
- 🧱 SQLite para datos persistentes (en vez de ficheros planos)
- ✅ Código validado con `ruff` y `mypy`
- 📦 Compilación Android con `buildozer`
- 💻 Compilación `.exe` en Windows con `PyInstaller`

---

## 🗃️ Estructura de datos en el directorio del usuario

Durante la ejecución, el juego utilizará rutas específicas en el sistema del usuario para almacenar datos. Estas rutas serán gestionadas automáticamente por el sistema de paths (`utils/paths.py`) según el sistema operativo.

### Estructura prevista:

```
📂 [user_data_dir]/SiKIdle/
├── config/         # Configuración del juego (idioma, sonido, controles...)
├── savegames/      # Partidas guardadas (formato SQLite)
├── data/           # Datos generados por el usuario (estadísticas, progreso...)
├── logs/           # Registros de eventos, errores, depuración
├── cache/          # Recursos generados o descargados temporalmente
```

### Reglas:

- Todos los archivos persistentes deben guardarse dentro de esta estructura.
- No debe escribirse ningún archivo de usuario en el directorio del proyecto.
- Las rutas se construirán dinámicamente usando `pathlib.Path` y resolviendo desde `utils/paths.py`.
- Evitar archivos sueltos o rutas absolutas.

---

## 📐 Buenas prácticas

- 🧠 Código modular, scripts de máximo 200 líneas.
- 🔧 Funciones de máximo 30 líneas y baja complejidad.
- 📌 Indentación con TABULADORES (no espacios).
- 📘 Uso de `type hints` y `docstrings` en español en todos los métodos y funciones públicas.
- 🔗 Importaciones absolutas desde `src/`.
- 📎 Rutas relativas siempre con `pathlib`, nunca hardcodeadas.
- 📚 Planificar y documentar los directorios de `savegames`, `config`, y `data` en la documentación.

---

## 🔀 Gestión de repositorio Git

- Utilizar `git` CLI o `gh` CLI según convenga.
- Crear nuevas ramas para cada desarrollo.
- Lanzar pull request contra `main`, nunca empujar directamente.
- Confirmar validaciones (`ruff`, `mypy`) antes de mergear.
- Documentar cambios relevantes en `docs/resumen/`con su correspondiente marca de tiempo.

---

## 🔄 Última actualización

`{{ timestamp dinámico generado por agente }}`

