---
type: "always_apply"
---

# 📌 Convenciones de Código Python — Configuración Profesional

Este documento define la **configuración óptima y moderna** para proyectos Python, usando herramientas integradas y ampliamente aceptadas por la comunidad.

---

## ✅ Herramientas esenciales

| Propósito                    | Herramienta | Justificación                                      |
|-----------------------------|-------------|---------------------------------------------------|
| Estilo y linting            | `ruff`      | Reemplaza `flake8`, `isort`, `black`, `pylint`   |
| Tipado estático             | `mypy`      | Revisa tipos sin ejecutar el código               |
| Tests                       | `pytest`    | Framework de pruebas más usado                    |
| Cobertura de tests          | `coverage`  | Mide cuánto código cubren tus pruebas             |
| Seguridad (opcional)        | `bandit`    | Analiza fallos de seguridad comunes en Python     |

---

## 🧠 `pyproject.toml` de ejemplo

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
extend-select = ["I", "D", "C4", "UP", "N", "B", "A", "SIM", "F", "E", "S"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

---

## 📁 Estructura del proyecto

```plaintext
mi_proyecto/
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── mi_modulo/
│       ├── __init__.py
│       ├── utils.py
│       └── main.py
├── tests/
│   └── test_main.py
└── scripts/
```

---

## 🧾 Nombres recomendados

| Elemento         | Formato       | Ejemplo              |
|------------------|---------------|-----------------------|
| Módulo/script    | `snake_case`  | `procesar_datos.py`   |
| Clase            | `CamelCase`   | `GestorUsuarios`      |
| Función/método   | `snake_case`  | `obtener_total()`     |
| Constante        | `UPPER_CASE`  | `MAX_REINTENTOS`      |
| Variable         | `snake_case`  | `usuario_activo`      |

---

## 📚 Docstrings (estilo Google)

```python
def sumar(a: int, b: int) -> int:
    """Suma dos enteros.

    Args:
        a (int): Primer número.
        b (int): Segundo número.

    Returns:
        int: Resultado de la suma.
    """
    return a + b
```

---

## ✅ Comandos útiles

```bash
# Validar estilo y errores
ruff check .

# Corregir formato automáticamente
ruff format .

# Validar tipado
mypy src/

# Ejecutar tests
pytest

# Medir cobertura
coverage run -m pytest
coverage report -m
```

---

## 🔐 Seguridad (opcional)

```bash
# Analizar vulnerabilidades
bandit -r src/
```

---

## 🏁 Recomendación final

> Usa `ruff` + `mypy` como **mínimo obligatorio**.  
> Añade `pytest` y `coverage` si vas a testear bien.  
> Usa `bandit` si trabajas en entornos donde la seguridad sea crítica.

Esta combinación ofrece **velocidad, cobertura y profesionalismo** con herramientas modernas y sin dependencias innecesarias.

