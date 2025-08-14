"""Sistema de optimización de performance visual para SiKIdle.

Optimiza la carga y renderizado de assets visuales para dispositivos móviles,
implementa caching inteligente y ajustes de calidad dinámicos.
"""

import logging
import time
import gc
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Niveles de performance disponibles."""
    LOW = "low"           # Dispositivos de gama baja
    MEDIUM = "medium"     # Dispositivos de gama media
    HIGH = "high"         # Dispositivos de gama alta
    ULTRA = "ultra"       # Dispositivos premium


class AssetQuality(Enum):
    """Calidades de assets disponibles."""
    COMPRESSED = "compressed"    # Máxima compresión
    STANDARD = "standard"        # Calidad estándar
    HIGH = "high"               # Alta calidad
    ORIGINAL = "original"       # Calidad original


@dataclass
class PerformanceMetrics:
    """Métricas de performance del sistema."""
    fps: float = 0.0
    memory_usage_mb: float = 0.0
    asset_load_time_ms: float = 0.0
    active_effects_count: int = 0
    cached_assets_count: int = 0
    last_gc_time: float = 0.0


@dataclass
class DeviceProfile:
    """Perfil de dispositivo para optimización."""
    performance_level: PerformanceLevel
    max_memory_mb: int
    max_concurrent_effects: int
    asset_quality: AssetQuality
    enable_animations: bool
    enable_particles: bool
    cache_size_mb: int


class AssetCache:
    """Cache inteligente de assets visuales."""
    
    def __init__(self, max_size_mb: int = 50):
        """Inicializa el cache de assets."""
        self.max_size_mb = max_size_mb
        self.cached_assets: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.asset_sizes: Dict[str, float] = {}
        self.current_size_mb = 0.0
        
        logger.info(f"AssetCache inicializado con límite de {max_size_mb}MB")
    
    def get_asset(self, asset_path: str) -> Optional[Any]:
        """Obtiene un asset del cache."""
        if asset_path in self.cached_assets:
            self.access_times[asset_path] = time.time()
            return self.cached_assets[asset_path]
        return None
    
    def cache_asset(self, asset_path: str, asset_data: Any, size_mb: float):
        """Cachea un asset."""
        # Verificar si hay espacio suficiente
        if self.current_size_mb + size_mb > self.max_size_mb:
            self._cleanup_cache(size_mb)
        
        # Cachear el asset
        self.cached_assets[asset_path] = asset_data
        self.access_times[asset_path] = time.time()
        self.asset_sizes[asset_path] = size_mb
        self.current_size_mb += size_mb
        
        logger.debug(f"Asset cacheado: {asset_path} ({size_mb:.2f}MB)")
    
    def _cleanup_cache(self, required_space_mb: float):
        """Limpia el cache para hacer espacio."""
        # Ordenar por tiempo de acceso (LRU)
        sorted_assets = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        freed_space = 0.0
        assets_to_remove = []
        
        for asset_path, _ in sorted_assets:
            if freed_space >= required_space_mb:
                break
            
            asset_size = self.asset_sizes[asset_path]
            freed_space += asset_size
            assets_to_remove.append(asset_path)
        
        # Remover assets
        for asset_path in assets_to_remove:
            self._remove_asset(asset_path)
        
        logger.info(f"Cache limpiado: {len(assets_to_remove)} assets, {freed_space:.2f}MB liberados")
    
    def _remove_asset(self, asset_path: str):
        """Remueve un asset del cache."""
        if asset_path in self.cached_assets:
            size = self.asset_sizes[asset_path]
            del self.cached_assets[asset_path]
            del self.access_times[asset_path]
            del self.asset_sizes[asset_path]
            self.current_size_mb -= size
    
    def clear_cache(self):
        """Limpia completamente el cache."""
        self.cached_assets.clear()
        self.access_times.clear()
        self.asset_sizes.clear()
        self.current_size_mb = 0.0
        logger.info("Cache completamente limpiado")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        return {
            'cached_assets': len(self.cached_assets),
            'current_size_mb': self.current_size_mb,
            'max_size_mb': self.max_size_mb,
            'usage_percentage': (self.current_size_mb / self.max_size_mb) * 100
        }


class PerformanceOptimizer:
    """Optimizador principal de performance visual."""
    
    def __init__(self):
        """Inicializa el optimizador de performance."""
        self.device_profile = self._detect_device_profile()
        self.asset_cache = AssetCache(self.device_profile.cache_size_mb)
        self.metrics = PerformanceMetrics()
        
        # Configuración dinámica
        self.dynamic_quality_enabled = True
        self.auto_gc_enabled = True
        self.performance_monitoring_enabled = True
        
        # Contadores
        self.frame_count = 0
        self.last_fps_update = time.time()
        
        logger.info(f"PerformanceOptimizer inicializado - Nivel: {self.device_profile.performance_level.value}")
    
    def _detect_device_profile(self) -> DeviceProfile:
        """Detecta el perfil del dispositivo automáticamente."""
        # Detección básica (en un juego real usarías APIs del sistema)
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            if memory_gb >= 8:
                performance_level = PerformanceLevel.ULTRA
            elif memory_gb >= 4:
                performance_level = PerformanceLevel.HIGH
            elif memory_gb >= 2:
                performance_level = PerformanceLevel.MEDIUM
            else:
                performance_level = PerformanceLevel.LOW
                
        except ImportError:
            # Fallback si psutil no está disponible
            performance_level = PerformanceLevel.MEDIUM
            memory_gb = 4
        
        # Configurar perfil basado en el nivel detectado
        profiles = {
            PerformanceLevel.LOW: DeviceProfile(
                performance_level=PerformanceLevel.LOW,
                max_memory_mb=512,
                max_concurrent_effects=5,
                asset_quality=AssetQuality.COMPRESSED,
                enable_animations=False,
                enable_particles=False,
                cache_size_mb=20
            ),
            PerformanceLevel.MEDIUM: DeviceProfile(
                performance_level=PerformanceLevel.MEDIUM,
                max_memory_mb=1024,
                max_concurrent_effects=10,
                asset_quality=AssetQuality.STANDARD,
                enable_animations=True,
                enable_particles=False,
                cache_size_mb=40
            ),
            PerformanceLevel.HIGH: DeviceProfile(
                performance_level=PerformanceLevel.HIGH,
                max_memory_mb=2048,
                max_concurrent_effects=20,
                asset_quality=AssetQuality.HIGH,
                enable_animations=True,
                enable_particles=True,
                cache_size_mb=80
            ),
            PerformanceLevel.ULTRA: DeviceProfile(
                performance_level=PerformanceLevel.ULTRA,
                max_memory_mb=4096,
                max_concurrent_effects=50,
                asset_quality=AssetQuality.ORIGINAL,
                enable_animations=True,
                enable_particles=True,
                cache_size_mb=150
            )
        }
        
        return profiles[performance_level]
    
    def should_enable_effect(self, effect_type: str) -> bool:
        """Determina si un efecto debe habilitarse según la performance."""
        if effect_type == "particles" and not self.device_profile.enable_particles:
            return False
        
        if effect_type == "animations" and not self.device_profile.enable_animations:
            return False
        
        # Verificar límite de efectos concurrentes
        if self.metrics.active_effects_count >= self.device_profile.max_concurrent_effects:
            return False
        
        return True
    
    def get_optimal_asset_quality(self, asset_type: str) -> AssetQuality:
        """Obtiene la calidad óptima para un tipo de asset."""
        base_quality = self.device_profile.asset_quality
        
        # Ajuste dinámico basado en performance actual
        if self.dynamic_quality_enabled:
            if self.metrics.fps < 30:
                # Reducir calidad si FPS es bajo
                quality_levels = list(AssetQuality)
                current_index = quality_levels.index(base_quality)
                if current_index > 0:
                    base_quality = quality_levels[current_index - 1]
            elif self.metrics.fps > 55 and self.metrics.memory_usage_mb < self.device_profile.max_memory_mb * 0.7:
                # Aumentar calidad si performance es buena
                quality_levels = list(AssetQuality)
                current_index = quality_levels.index(base_quality)
                if current_index < len(quality_levels) - 1:
                    base_quality = quality_levels[current_index + 1]
        
        return base_quality
    
    def update_performance_metrics(self, dt: float):
        """Actualiza las métricas de performance."""
        if not self.performance_monitoring_enabled:
            return
        
        self.frame_count += 1
        current_time = time.time()
        
        # Actualizar FPS cada segundo
        if current_time - self.last_fps_update >= 1.0:
            self.metrics.fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
        
        # Actualizar uso de memoria
        try:
            import psutil
            process = psutil.Process()
            self.metrics.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        except ImportError:
            pass
        
        # Actualizar estadísticas del cache
        cache_stats = self.asset_cache.get_cache_stats()
        self.metrics.cached_assets_count = cache_stats['cached_assets']
        
        # Garbage collection automático
        if self.auto_gc_enabled and current_time - self.metrics.last_gc_time > 30:
            if self.metrics.memory_usage_mb > self.device_profile.max_memory_mb * 0.8:
                gc.collect()
                self.metrics.last_gc_time = current_time
                logger.debug("Garbage collection ejecutado automáticamente")
    
    def optimize_asset_loading(self, asset_path: str, asset_data: Any, size_mb: float) -> Any:
        """Optimiza la carga de un asset."""
        # Verificar cache primero
        cached_asset = self.asset_cache.get_asset(asset_path)
        if cached_asset is not None:
            return cached_asset
        
        # Procesar asset según la calidad configurada
        quality = self.get_optimal_asset_quality("image")
        processed_asset = self._process_asset_quality(asset_data, quality)
        
        # Cachear si hay espacio
        if size_mb <= self.device_profile.cache_size_mb * 0.1:  # No cachear assets muy grandes
            self.asset_cache.cache_asset(asset_path, processed_asset, size_mb)
        
        return processed_asset
    
    def _process_asset_quality(self, asset_data: Any, quality: AssetQuality) -> Any:
        """Procesa un asset según la calidad especificada."""
        # En una implementación real, aquí redimensionarías/comprimirías la imagen
        # Por ahora, simplemente retornamos el asset original
        return asset_data
    
    def register_active_effect(self):
        """Registra un efecto activo."""
        self.metrics.active_effects_count += 1
    
    def unregister_active_effect(self):
        """Desregistra un efecto activo."""
        self.metrics.active_effects_count = max(0, self.metrics.active_effects_count - 1)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Obtiene un reporte completo de performance."""
        cache_stats = self.asset_cache.get_cache_stats()
        
        return {
            'device_profile': {
                'performance_level': self.device_profile.performance_level.value,
                'max_memory_mb': self.device_profile.max_memory_mb,
                'asset_quality': self.device_profile.asset_quality.value,
                'animations_enabled': self.device_profile.enable_animations,
                'particles_enabled': self.device_profile.enable_particles
            },
            'current_metrics': {
                'fps': round(self.metrics.fps, 1),
                'memory_usage_mb': round(self.metrics.memory_usage_mb, 1),
                'active_effects': self.metrics.active_effects_count,
                'cached_assets': self.metrics.cached_assets_count
            },
            'cache_stats': cache_stats,
            'optimization_status': {
                'dynamic_quality_enabled': self.dynamic_quality_enabled,
                'auto_gc_enabled': self.auto_gc_enabled,
                'performance_monitoring_enabled': self.performance_monitoring_enabled
            }
        }
    
    def adjust_settings_for_performance(self):
        """Ajusta configuraciones automáticamente basado en performance."""
        if not self.dynamic_quality_enabled:
            return
        
        # Si FPS es muy bajo, reducir efectos
        if self.metrics.fps < 20:
            self.device_profile.max_concurrent_effects = max(3, self.device_profile.max_concurrent_effects - 2)
            self.device_profile.enable_particles = False
            logger.warning("Performance baja detectada - Reduciendo efectos visuales")
        
        # Si memoria es alta, limpiar cache
        if self.metrics.memory_usage_mb > self.device_profile.max_memory_mb * 0.9:
            self.asset_cache.clear_cache()
            gc.collect()
            logger.warning("Uso de memoria alto - Limpiando cache")
    
    def cleanup(self):
        """Limpia recursos del optimizador."""
        self.asset_cache.clear_cache()
        gc.collect()
        logger.info("PerformanceOptimizer limpiado")


# Instancia global del optimizador
_performance_optimizer_instance = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Obtiene la instancia global del optimizador de performance."""
    global _performance_optimizer_instance
    if _performance_optimizer_instance is None:
        _performance_optimizer_instance = PerformanceOptimizer()
    return _performance_optimizer_instance
