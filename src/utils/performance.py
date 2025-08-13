"""
Sistema de Optimización de Performance para SiKIdle.

Optimizaciones específicas para idle clickers móviles:
- Cálculos eficientes de producción
- Update intervals inteligentes
- Memory management
- Batch operations
"""

import logging
import time
from typing import Dict, List, Any, Optional
from collections import deque


class PerformanceMonitor:
	"""Monitor de performance para detectar problemas."""
	
	def __init__(self, max_samples: int = 100):
		self.max_samples = max_samples
		self.frame_times = deque(maxlen=max_samples)
		self.update_times = deque(maxlen=max_samples)
		self.last_frame_time = time.time()
		
	def record_frame(self):
		"""Registra el tiempo de un frame."""
		current_time = time.time()
		frame_time = current_time - self.last_frame_time
		self.frame_times.append(frame_time)
		self.last_frame_time = current_time
		
	def record_update(self, update_time: float):
		"""Registra el tiempo de una actualización."""
		self.update_times.append(update_time)
		
	def get_avg_fps(self) -> float:
		"""Obtiene el FPS promedio."""
		if not self.frame_times:
			return 0.0
		avg_frame_time = sum(self.frame_times) / len(self.frame_times)
		return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
		
	def get_avg_update_time(self) -> float:
		"""Obtiene el tiempo promedio de actualización."""
		if not self.update_times:
			return 0.0
		return sum(self.update_times) / len(self.update_times)
		
	def is_performance_good(self) -> bool:
		"""Verifica si el performance es bueno (>30 FPS)."""
		return self.get_avg_fps() > 30.0


class BatchCalculator:
	"""Calculadora optimizada para operaciones en lote."""
	
	@staticmethod
	def calculate_building_production_batch(buildings: Dict, time_delta: float) -> Dict[str, float]:
		"""Calcula producción de edificios en lote."""
		production = {}
		
		for building_type, building in buildings.items():
			if building.count > 0:
				# Cálculo optimizado: count * base_production * multipliers * time
				base_production = building.base_production_per_second
				total_production = building.count * base_production * time_delta
				
				# Aplicar multiplicadores solo si son diferentes de 1.0
				if hasattr(building, 'multiplier') and building.multiplier != 1.0:
					total_production *= building.multiplier
					
				if total_production > 0:
					production[building_type] = total_production
					
		return production
	
	@staticmethod
	def calculate_achievement_progress_batch(achievements: Dict, game_state) -> List[str]:
		"""Calcula progreso de achievements en lote."""
		completed = []
		
		# Pre-calcular valores comunes una sola vez
		total_clicks = getattr(game_state, 'total_clicks', 0)
		current_coins = getattr(game_state, 'coins', 0)
		
		total_buildings = 0
		if hasattr(game_state, 'building_manager'):
			total_buildings = sum(
				building.count for building in game_state.building_manager.buildings.values()
			)
		
		prestige_count = 0
		prestige_crystals = 0
		if hasattr(game_state, 'prestige_manager'):
			prestige_count = game_state.prestige_manager.prestige_count
			prestige_crystals = game_state.prestige_manager.prestige_crystals
		
		# Verificar achievements en lote
		for achievement_id, achievement in achievements.items():
			if achievement.completed:
				continue
				
			old_progress = achievement.current_progress
			new_progress = old_progress
			
			# Mapeo eficiente de valores según el tipo de achievement
			if 'click' in achievement_id:
				new_progress = total_clicks
			elif 'building' in achievement_id:
				new_progress = total_buildings
			elif 'coins' in achievement_id:
				new_progress = current_coins
			elif 'prestige' in achievement_id:
				new_progress = prestige_count
			elif 'crystal' in achievement_id:
				new_progress = prestige_crystals
			elif achievement_id == 'idle_master':
				# Contar achievements completados
				new_progress = sum(1 for a in achievements.values() if a.completed)
			
			# Solo actualizar si cambió
			if new_progress != old_progress:
				if achievement.update_progress(new_progress):
					completed.append(achievement_id)
		
		return completed


class UpdateScheduler:
	"""Programador inteligente de actualizaciones con diferentes frecuencias."""
	
	def __init__(self):
		self.schedules = {
			'critical': {'interval': 0.1, 'last_update': 0},    # 10 FPS - UI crítica
			'high': {'interval': 0.2, 'last_update': 0},        # 5 FPS - Producción
			'medium': {'interval': 0.5, 'last_update': 0},      # 2 FPS - UI general
			'low': {'interval': 1.0, 'last_update': 0},         # 1 FPS - Estadísticas
			'background': {'interval': 3.0, 'last_update': 0}   # 0.33 FPS - Achievements
		}
		
	def should_update(self, priority: str) -> bool:
		"""Verifica si es momento de actualizar según la prioridad."""
		if priority not in self.schedules:
			return True
			
		current_time = time.time()
		schedule = self.schedules[priority]
		
		if current_time - schedule['last_update'] >= schedule['interval']:
			schedule['last_update'] = current_time
			return True
			
		return False
	
	def adjust_intervals(self, performance_good: bool):
		"""Ajusta intervalos según el performance."""
		if not performance_good:
			# Reducir frecuencia si el performance es malo
			for schedule in self.schedules.values():
				schedule['interval'] *= 1.2  # 20% más lento
		else:
			# Restaurar frecuencias normales gradualmente
			base_intervals = {
				'critical': 0.1, 'high': 0.2, 'medium': 0.5, 
				'low': 1.0, 'background': 3.0
			}
			for priority, schedule in self.schedules.items():
				target = base_intervals[priority]
				if schedule['interval'] > target:
					schedule['interval'] = max(target, schedule['interval'] * 0.95)


class MemoryManager:
	"""Gestor de memoria para evitar leaks en sesiones largas."""
	
	def __init__(self):
		self.cached_calculations = {}
		self.cache_max_size = 100
		self.cache_access_count = {}
		
	def get_cached_calculation(self, key: str) -> Optional[Any]:
		"""Obtiene un cálculo cacheado."""
		if key in self.cached_calculations:
			self.cache_access_count[key] = self.cache_access_count.get(key, 0) + 1
			return self.cached_calculations[key]
		return None
		
	def cache_calculation(self, key: str, value: Any):
		"""Cachea un cálculo."""
		# Limpiar cache si está lleno
		if len(self.cached_calculations) >= self.cache_max_size:
			self._cleanup_cache()
			
		self.cached_calculations[key] = value
		self.cache_access_count[key] = 1
		
	def _cleanup_cache(self):
		"""Limpia el cache eliminando elementos menos usados."""
		# Ordenar por frecuencia de acceso
		sorted_items = sorted(
			self.cache_access_count.items(), 
			key=lambda x: x[1]
		)
		
		# Eliminar el 25% menos usado
		items_to_remove = len(sorted_items) // 4
		for key, _ in sorted_items[:items_to_remove]:
			self.cached_calculations.pop(key, None)
			self.cache_access_count.pop(key, None)
			
	def clear_cache(self):
		"""Limpia completamente el cache."""
		self.cached_calculations.clear()
		self.cache_access_count.clear()
		
	def get_memory_stats(self) -> Dict[str, int]:
		"""Obtiene estadísticas de memoria."""
		return {
			'cached_items': len(self.cached_calculations),
			'cache_max_size': self.cache_max_size,
			'total_accesses': sum(self.cache_access_count.values())
		}


class PerformanceOptimizer:
	"""Optimizador principal de performance."""
	
	def __init__(self):
		self.monitor = PerformanceMonitor()
		self.scheduler = UpdateScheduler()
		self.memory_manager = MemoryManager()
		self.batch_calculator = BatchCalculator()
		
		# Configuración
		self.optimization_enabled = True
		self.debug_mode = False
		
		logging.info("PerformanceOptimizer initialized")
		
	def optimize_building_production(self, building_manager, time_delta: float) -> Dict:
		"""Optimiza el cálculo de producción de edificios."""
		if not self.optimization_enabled:
			return building_manager.collect_all_production()
			
		start_time = time.time()
		
		# Usar cálculo en lote optimizado
		production = self.batch_calculator.calculate_building_production_batch(
			building_manager.buildings, time_delta
		)
		
		# Aplicar a los recursos
		for resource_type, amount in production.items():
			if hasattr(building_manager, 'resource_manager'):
				building_manager.resource_manager.add_resource(resource_type, amount)
		
		# Monitorear performance
		calculation_time = time.time() - start_time
		self.monitor.record_update(calculation_time)
		
		if self.debug_mode and calculation_time > 0.01:  # >10ms
			logging.warning(f"Slow building calculation: {calculation_time:.3f}s")
			
		return production
		
	def optimize_achievement_check(self, achievement_manager, game_state) -> List:
		"""Optimiza la verificación de achievements."""
		if not self.scheduler.should_update('background'):
			return []
			
		start_time = time.time()
		
		# Usar verificación en lote
		completed = self.batch_calculator.calculate_achievement_progress_batch(
			achievement_manager.achievements, game_state
		)
		
		calculation_time = time.time() - start_time
		self.monitor.record_update(calculation_time)
		
		if self.debug_mode and completed:
			logging.info(f"Achievements completed: {len(completed)} in {calculation_time:.3f}s")
			
		return completed
		
	def should_update_ui(self, priority: str = 'medium') -> bool:
		"""Verifica si se debe actualizar la UI según prioridad."""
		return self.scheduler.should_update(priority)
		
	def record_frame(self):
		"""Registra un frame para monitoreo."""
		self.monitor.record_frame()
		
	def adjust_performance(self):
		"""Ajusta la performance según las métricas actuales."""
		performance_good = self.monitor.is_performance_good()
		self.scheduler.adjust_intervals(performance_good)
		
		if not performance_good and self.debug_mode:
			avg_fps = self.monitor.get_avg_fps()
			logging.warning(f"Low performance detected: {avg_fps:.1f} FPS")
			
	def get_performance_stats(self) -> Dict[str, Any]:
		"""Obtiene estadísticas de performance."""
		return {
			'avg_fps': self.monitor.get_avg_fps(),
			'avg_update_time': self.monitor.get_avg_update_time(),
			'performance_good': self.monitor.is_performance_good(),
			'memory_stats': self.memory_manager.get_memory_stats(),
			'optimization_enabled': self.optimization_enabled
		}
		
	def enable_debug_mode(self):
		"""Activa el modo debug para performance."""
		self.debug_mode = True
		logging.info("Performance debug mode enabled")
		
	def disable_debug_mode(self):
		"""Desactiva el modo debug."""
		self.debug_mode = False
		
	def cleanup(self):
		"""Limpia recursos para evitar memory leaks."""
		self.memory_manager.clear_cache()
		logging.info("Performance optimizer cleaned up")


# Instancia global del optimizador
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
	"""Obtiene la instancia global del optimizador de performance."""
	global _performance_optimizer
	if _performance_optimizer is None:
		_performance_optimizer = PerformanceOptimizer()
	return _performance_optimizer