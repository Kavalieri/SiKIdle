# Guía de Contribución - SiKIdle

¡Gracias por tu interés en contribuir a SiKIdle! Este documento establece las pautas y convenciones para mantener la calidad y consistencia del proyecto.

## 🛠️ Tecnologías y Convenciones

### Lenguaje y Frameworks
- **Python 3.11+** estrictamente
- **Kivy** para la interfaz (sin archivos `.kv`)
- **SQLite** para persistencia
- **pathlib** para manejo de rutas (no `os.path`)

### Estilo de Código

#### Nomenclatura
- `snake_case` para funciones y variables
- `PascalCase` para clases
- `UPPER_SNAKE_CASE` para constantes

#### Indentación y Formato
- **Tabulaciones** (no espacios) para indentación
- Máximo 200 líneas por archivo
- Máximo 30 líneas por función
- Líneas de máximo 100 caracteres

#### Type Hints y Documentación
- **Type hints obligatorios** en todas las funciones públicas
- **Docstrings en español** para todas las funciones
   ```bash
   git checkout -b feature/nombre
   ```

2. Realiza tus cambios siguiendo la arquitectura del proyecto.
3. Valida tu código:
   ```bash
   poetry run ruff check .
   poetry run mypy src/
   ```

4. Envía un Pull Request hacia `main`.
5. Describe claramente los cambios en el PR.

## Convenciones

- Código y nombres en inglés
- Comentarios y documentación en español
- Usar `tab` para la indentación
- Máximo 200 líneas por archivo, 30 líneas por función

¡Gracias por contribuir!
