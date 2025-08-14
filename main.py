#!/usr/bin/env python3
"""
SiKIdle - Punto de entrada principal para Android
Stack moderno: Python 3.11 + Kivy 2.3.1
"""

import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Importar y ejecutar el main del proyecto
if __name__ == "__main__":
	# Import directo desde el módulo main en src/
	from main import main

	main()
