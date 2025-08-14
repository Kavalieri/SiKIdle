#!/usr/bin/env python3
"""
Script de Análisis del Entorno - SiKIdle Pre-Alfa Testing.

Analiza la configuración del entorno de desarrollo y detecta
problemas potenciales antes del testing exhaustivo.
"""

import sys
import os
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


class EnvironmentAnalyzer:
	"""Analizador del entorno de desarrollo."""
	
	def __init__(self):
		self.project_root = Path(__file__).parent.parent.parent
		self.src_path = self.project_root / "src"
		self.results = {
			'python_version': None,
			'dependencies': {},
			'imports': {},
			'structure': {},
			'issues': []
		}
	
	def analyze_python_version(self) -> Dict[str, Any]:
		"""Analiza la versión de Python."""
		version_info = sys.version_info
		version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
		
		result = {
			'version': version_str,
			'major': version_info.major,
			'minor': version_info.minor,
			'micro': version_info.micro,
			'is_compatible': version_info >= (3, 11)
		}
		
		if not result['is_compatible']:
			self.results['issues'].append({
				'type': 'critical',
				'component': 'python',
				'message': f"Python {version_str} < 3.11 requerido"
			})
		
		return result
	
	def analyze_dependencies(self) -> Dict[str, Any]:
		"""Analiza las dependencias instaladas."""
		try:
			# Leer requirements.txt
			req_file = self.project_root / "requirements.txt"
			required_packages = {}
			
			if req_file.exists():
				with open(req_file, 'r') as f:
					for line in f:
						line = line.strip()
						if line and not line.startswith('#'):
							if '>=' in line:
								pkg, version = line.split('>=')
								required_packages[pkg] = version
			
			# Verificar paquetes instalados
			installed = {}
			missing = []
			
			for pkg, min_version in required_packages.items():
				try:
					module = importlib.import_module(pkg.replace('-', '_'))
					if hasattr(module, '__version__'):
						installed[pkg] = module.__version__
					else:
						installed[pkg] = 'unknown'
				except ImportError:
					missing.append(pkg)
					self.results['issues'].append({
						'type': 'critical',
						'component': 'dependencies',
						'message': f"Paquete requerido no instalado: {pkg}"
					})
			
			return {
				'required': required_packages,
				'installed': installed,
				'missing': missing
			}
			
		except Exception as e:
			self.results['issues'].append({
				'type': 'error',
				'component': 'dependencies',
				'message': f"Error analizando dependencias: {e}"
			})
			return {}
	
	def analyze_imports(self) -> Dict[str, Any]:
		"""Analiza las importaciones del proyecto."""
		import_issues = []
		circular_imports = []
		
		# Verificar importaciones críticas
		critical_imports = [
			'kivy',
			'kivy.app',
			'kivy.uix.boxlayout',
			'sqlite3',
			'pathlib'
		]
		
		for imp in critical_imports:
			try:
				importlib.import_module(imp)
			except ImportError as e:
				import_issues.append(f"No se puede importar {imp}: {e}")
				self.results['issues'].append({
					'type': 'critical',
					'component': 'imports',
					'message': f"Import crítico falla: {imp}"
				})
		
		# Verificar estructura src/
		if self.src_path.exists():
			sys.path.insert(0, str(self.src_path))
			
			# Intentar importar módulos principales
			main_modules = [
				'core.game',
				'core.achievements_idle',
				'core.prestige_simple',
				'core.premium_shop',
				'utils.save',
				'utils.paths'
			]
			
			for module in main_modules:
				try:
					importlib.import_module(module)
				except ImportError as e:
					import_issues.append(f"No se puede importar {module}: {e}")
					self.results['issues'].append({
						'type': 'high',
						'component': 'imports',
						'message': f"Módulo principal falla: {module}"
					})
		
		return {
			'critical_imports': critical_imports,
			'import_issues': import_issues,
			'circular_imports': circular_imports
		}
	
	def analyze_project_structure(self) -> Dict[str, Any]:
		"""Analiza la estructura del proyecto."""
		expected_structure = {
			'src/': ['core/', 'ui/', 'utils/', 'assets/', 'main.py'],
			'src/core/': ['game.py', 'achievements_idle.py', 'prestige_simple.py'],
			'src/ui/': ['navigation/', 'screens/'],
			'src/utils/': ['save.py', 'paths.py', 'mobile_optimization.py'],
			'docs/': ['resumen/', 'checklist/', 'README.md'],
			'dev-tools/': ['tests/', 'scripts/']
		}
		
		structure_issues = []
		missing_files = []
		
		for directory, expected_files in expected_structure.items():
			dir_path = self.project_root / directory
			
			if not dir_path.exists():
				missing_files.append(directory)
				self.results['issues'].append({
					'type': 'high',
					'component': 'structure',
					'message': f"Directorio faltante: {directory}"
				})
				continue
			
			for expected_file in expected_files:
				file_path = dir_path / expected_file
				if not file_path.exists():
					missing_files.append(f"{directory}{expected_file}")
					
					# Determinar severidad
					severity = 'critical' if expected_file in ['main.py', 'game.py'] else 'medium'
					self.results['issues'].append({
						'type': severity,
						'component': 'structure',
						'message': f"Archivo faltante: {directory}{expected_file}"
					})
		
		return {
			'expected_structure': expected_structure,
			'missing_files': missing_files,
			'structure_issues': structure_issues
		}
	
	def check_code_quality(self) -> Dict[str, Any]:
		"""Verifica calidad del código con ruff y mypy."""
		quality_results = {}
		
		# Verificar con ruff
		try:
			result = subprocess.run(
				['ruff', 'check', str(self.src_path)],
				capture_output=True,
				text=True,
				cwd=self.project_root
			)
			
			quality_results['ruff'] = {
				'exit_code': result.returncode,
				'stdout': result.stdout,
				'stderr': result.stderr,
				'issues_found': result.returncode != 0
			}
			
			if result.returncode != 0:
				self.results['issues'].append({
					'type': 'medium',
					'component': 'code_quality',
					'message': f"Ruff encontró {result.stdout.count('error')} errores de estilo"
				})
		
		except FileNotFoundError:
			quality_results['ruff'] = {'error': 'ruff no encontrado'}
		
		# Verificar con mypy
		try:
			result = subprocess.run(
				['mypy', str(self.src_path)],
				capture_output=True,
				text=True,
				cwd=self.project_root
			)
			
			quality_results['mypy'] = {
				'exit_code': result.returncode,
				'stdout': result.stdout,
				'stderr': result.stderr,
				'issues_found': result.returncode != 0
			}
			
			if result.returncode != 0:
				self.results['issues'].append({
					'type': 'low',
					'component': 'code_quality',
					'message': f"MyPy encontró issues de tipos"
				})
		
		except FileNotFoundError:
			quality_results['mypy'] = {'error': 'mypy no encontrado'}
		
		return quality_results
	
	def run_full_analysis(self) -> Dict[str, Any]:
		"""Ejecuta análisis completo del entorno."""
		print("🔍 Iniciando análisis del entorno...")
		
		# Análisis de Python
		print("  📍 Analizando versión de Python...")
		self.results['python_version'] = self.analyze_python_version()
		
		# Análisis de dependencias
		print("  📦 Analizando dependencias...")
		self.results['dependencies'] = self.analyze_dependencies()
		
		# Análisis de importaciones
		print("  🔗 Analizando importaciones...")
		self.results['imports'] = self.analyze_imports()
		
		# Análisis de estructura
		print("  🏗️ Analizando estructura del proyecto...")
		self.results['structure'] = self.analyze_project_structure()
		
		# Análisis de calidad de código
		print("  ✨ Analizando calidad del código...")
		self.results['code_quality'] = self.check_code_quality()
		
		return self.results
	
	def generate_report(self) -> str:
		"""Genera reporte del análisis."""
		report = []
		report.append("# 📊 Reporte de Análisis del Entorno - SiKIdle")
		report.append(f"**Fecha:** {Path(__file__).stat().st_mtime}")
		report.append("")
		
		# Resumen de issues
		critical = len([i for i in self.results['issues'] if i['type'] == 'critical'])
		high = len([i for i in self.results['issues'] if i['type'] == 'high'])
		medium = len([i for i in self.results['issues'] if i['type'] == 'medium'])
		low = len([i for i in self.results['issues'] if i['type'] == 'low'])
		
		report.append("## 🚨 Resumen de Issues")
		report.append(f"- **Críticos:** {critical}")
		report.append(f"- **Altos:** {high}")
		report.append(f"- **Medios:** {medium}")
		report.append(f"- **Bajos:** {low}")
		report.append("")
		
		# Detalles por componente
		if self.results['issues']:
			report.append("## 📋 Issues Detallados")
			for issue in self.results['issues']:
				icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(issue['type'], '⚪')
				report.append(f"- {icon} **{issue['component']}**: {issue['message']}")
			report.append("")
		
		# Estado de Python
		py_info = self.results.get('python_version', {})
		status = "✅" if py_info.get('is_compatible', False) else "❌"
		report.append(f"## 🐍 Python: {status} {py_info.get('version', 'unknown')}")
		report.append("")
		
		# Estado de dependencias
		deps = self.results.get('dependencies', {})
		missing = len(deps.get('missing', []))
		status = "✅" if missing == 0 else "❌"
		report.append(f"## 📦 Dependencias: {status} ({missing} faltantes)")
		report.append("")
		
		return "\n".join(report)


def main():
	"""Función principal."""
	analyzer = EnvironmentAnalyzer()
	results = analyzer.run_full_analysis()
	
	# Generar reporte
	report = analyzer.generate_report()
	
	# Guardar reporte
	report_file = analyzer.project_root / "tmp" / "environment_analysis_report.md"
	report_file.parent.mkdir(exist_ok=True)
	
	with open(report_file, 'w', encoding='utf-8') as f:
		f.write(report)
	
	print(f"\n📄 Reporte guardado en: {report_file}")
	
	# Mostrar resumen
	critical_issues = len([i for i in results['issues'] if i['type'] == 'critical'])
	if critical_issues > 0:
		print(f"\n🔴 ATENCIÓN: {critical_issues} issues críticos encontrados")
		return 1
	else:
		print("\n✅ Análisis completado sin issues críticos")
		return 0


if __name__ == "__main__":
	sys.exit(main())