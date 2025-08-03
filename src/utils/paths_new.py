"""Sistema centralizado para gestionar rutas del sistema.

Este módulo proporciona funciones para obtener rutas específicas del usuario
según el sistema operativo, siguiendo las convenciones de cada plataforma.
"""

import os
import sys
from pathlib import Path


def get_user_data_dir() -> Path:
	"""Obtiene el directorio de datos del usuario según el sistema operativo.
	
	Returns:
		Path: Ruta al directorio de datos del usuario
	"""
	if sys.platform == "win32":
		# Windows: %APPDATA%
		return Path(os.environ.get("APPDATA", "")) / "SiKIdle"
	elif sys.platform == "darwin":
		# macOS: ~/Library/Application Support
		return Path.home() / "Library" / "Application Support" / "SiKIdle"
	else:
		# Linux/Unix: ~/.local/share o $XDG_DATA_HOME
		xdg_data = os.environ.get("XDG_DATA_HOME")
		if xdg_data:
			return Path(xdg_data) / "SiKIdle"
		return Path.home() / ".local" / "share" / "SiKIdle"


def get_config_dir() -> Path:
	"""Obtiene el directorio de configuración.
	
	Returns:
		Path: Ruta al directorio de configuración
	"""
	return get_user_data_dir() / "config"


def get_savegames_dir() -> Path:
	"""Obtiene el directorio de partidas guardadas.
	
	Returns:
		Path: Ruta al directorio de savegames
	"""
	return get_user_data_dir() / "savegames"


def get_data_dir() -> Path:
	"""Obtiene el directorio de datos generados por el usuario.
	
	Returns:
		Path: Ruta al directorio de datos
	"""
	return get_user_data_dir() / "data"


def get_logs_dir() -> Path:
	"""Obtiene el directorio de logs.
	
	Returns:
		Path: Ruta al directorio de logs
	"""
	return get_user_data_dir() / "logs"


def get_cache_dir() -> Path:
	"""Obtiene el directorio de caché.
	
	Returns:
		Path: Ruta al directorio de caché
	"""
	return get_user_data_dir() / "cache"


def ensure_directories() -> None:
	"""Crea todos los directorios necesarios si no existen."""
	directories = [
		get_user_data_dir(),
		get_config_dir(),
		get_savegames_dir(),
		get_data_dir(),
		get_logs_dir(),
		get_cache_dir()
	]
	
	for directory in directories:
		directory.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
	"""Obtiene la ruta raíz del proyecto.
	
	Returns:
		Path: Ruta al directorio raíz del proyecto
	"""
	# Buscar desde el archivo actual hacia arriba hasta encontrar pyproject.toml
	current_path = Path(__file__).resolve()
	for parent in current_path.parents:
		if (parent / "pyproject.toml").exists():
			return parent
	
	# Fallback: directorio padre del src
	return Path(__file__).resolve().parent.parent.parent


def get_assets_dir() -> Path:
	"""Obtiene el directorio de assets del proyecto.
	
	Returns:
		Path: Ruta al directorio de assets
	"""
	return get_project_root() / "src" / "assets"
