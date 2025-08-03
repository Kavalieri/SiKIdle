# Guía de colaboración - SiKIdle

Gracias por tu interés en colaborar con SiKIdle.

## Requisitos

- Python 3.11+
- Poetry instalado (`pip install poetry`)
- Conocimiento básico de Git y GitHub
- Familiaridad con PEP8, type hints y docstrings

## Configuración del entorno

```bash
poetry install
```

## Flujo de trabajo

1. Crear una rama a partir de `main`:
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
