"""
Sistema de Prestigio Dimensional para SiKIdle.

Sistema de ascensión dimensional donde los exploradores pueden reiniciar su progreso
para acceder a dimensiones superiores, ganando fragmentos de esencia y bonificaciones permanentes.
"""

import logging
import math
import time
from enum import Enum
from typing import Optional, Dict, List, Tuple

from core.resources import ResourceType, ResourceManager


class AscensionType(Enum):
    """Tipos de ascensión dimensional disponibles."""
    MINOR = "minor"           # Ascensión Menor - nivel 50+, requiere derrotar boss dimensión actual
    MAJOR = "major"           # Ascensión Mayor - nivel 100+, requiere boss + completar mazmorra secreta  
    DIMENSION = "dimension"   # Ascensión Dimensional - nivel 200+, requiere boss final + acceso nueva dimensión


class DimensionalReward:
    """Representa una recompensa de ascensión dimensional."""
    
    def __init__(self, essence_fragments: int, stat_bonus: float, special_unlock: Optional[str] = None):
        """Inicializa una recompensa de ascensión.
        
        Args:
            essence_fragments: Fragmentos de esencia dimensional ganados
            stat_bonus: Bonificación porcentual de estadísticas (+25%, +50%, etc.)
            special_unlock: Desbloqueo especial (nueva mazmorra, dimensión, etc.)
        """
        self.essence_fragments = essence_fragments
        self.stat_bonus = stat_bonus
        self.special_unlock = special_unlock


class DimensionalPrestigeManager:
    """Gestiona el sistema de prestigio dimensional del juego."""
    
    def __init__(self, resource_manager: ResourceManager, database):
        """Inicializa el gestor de prestigio dimensional.
        
        Args:
            resource_manager: Gestor de recursos del juego
            database: Conexión a la base de datos
        """
        self.resource_manager = resource_manager
        self.database = database
        
        # Estado del prestigio dimensional
        self.total_ascensions = 0
        self.minor_ascensions = 0
        self.major_ascensions = 0
        self.dimension_ascensions = 0
        
        # Fragmentos de esencia y bonificaciones
        self.essence_fragments = 0
        self.current_dimension = 1
        
        # Multiplicadores dimensionales actuales
        self.dimensional_stat_bonus = 1.0      # Bonificación base de stats (+25%, +50%, etc.)
        self.exploration_bonus = 1.0           # Bonificación de exploración
        self.experience_bonus = 1.0            # Bonificación de experiencia dimensional
        self.essence_gain_bonus = 1.0          # Bonificación de ganancia de esencia
        
        # Bonificaciones específicas de ascensión (FASE 5.2)
        self.damage_bonus = 1.0                # +15% daño base permanente por ascensión
        self.health_bonus = 1.0                # +10% salud máxima permanente por ascensión
        self.exp_speed_bonus = 1.0             # +20% velocidad de obtención de experiencia
        self.rare_loot_bonus = 0.0             # +5% probabilidad de loot raro por ascensión
        
        # Unlocks especiales
        self.unlocked_secret_dungeons = []
        self.unlocked_dimensions = [1]  # Dimensión 1 siempre disponible
        
        # Inicializar tablas de base de datos
        self._create_tables()
        
        # Cargar estado guardado
        self.load_dimensional_data()
        
        logging.info(f"Sistema de prestigio dimensional inicializado - Dimensión {self.current_dimension}")
    
    def _create_tables(self):
        """Crea las tablas de prestigio dimensional en la base de datos."""
        try:
            # Tabla de estadísticas de ascensión dimensional
            self.database.execute('''
                CREATE TABLE IF NOT EXISTS dimensional_stats (
                    id INTEGER PRIMARY KEY,
                    total_ascensions INTEGER DEFAULT 0,
                    minor_ascensions INTEGER DEFAULT 0,
                    major_ascensions INTEGER DEFAULT 0,
                    dimension_ascensions INTEGER DEFAULT 0,
                    essence_fragments INTEGER DEFAULT 0,
                    current_dimension INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de bonificaciones dimensionales activas
            self.database.execute('''
                CREATE TABLE IF NOT EXISTS dimensional_bonuses (
                    id INTEGER PRIMARY KEY,
                    dimensional_stat_bonus REAL DEFAULT 1.0,
                    exploration_bonus REAL DEFAULT 1.0,
                    experience_bonus REAL DEFAULT 1.0,
                    essence_gain_bonus REAL DEFAULT 1.0,
                    damage_bonus REAL DEFAULT 1.0,
                    health_bonus REAL DEFAULT 1.0,
                    exp_speed_bonus REAL DEFAULT 1.0,
                    rare_loot_bonus REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de unlocks especiales
            self.database.execute('''
                CREATE TABLE IF NOT EXISTS dimensional_unlocks (
                    id INTEGER PRIMARY KEY,
                    unlock_type TEXT NOT NULL,
                    unlock_name TEXT NOT NULL,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar fila inicial si no existe
            self.database.execute('''
                INSERT OR IGNORE INTO dimensional_stats (id) VALUES (1)
            ''')
            
            self.database.execute('''
                INSERT OR IGNORE INTO dimensional_bonuses (id) VALUES (1)
            ''')
            
            logging.debug("Tablas de prestigio dimensional creadas/verificadas")
        
        except Exception as e:
            logging.error(f"Error creando tablas de prestigio dimensional: {e}")
    
    def calculate_essence_gained(self, player_level: int, ascension_type: AscensionType) -> int:
        """Calcula los fragmentos de esencia que se ganarían con una ascensión.
        
        Args:
            player_level: Nivel actual del jugador
            ascension_type: Tipo de ascensión a realizar
            
        Returns:
            Número de fragmentos de esencia que se ganarían
        """
        base_essence = {
            AscensionType.MINOR: 5,      # 5 fragmentos base
            AscensionType.MAJOR: 15,     # 15 fragmentos base
            AscensionType.DIMENSION: 50  # 50 fragmentos base
        }
        
        # Bonificación por nivel: cada 10 niveles = +1 fragmento
        level_bonus = player_level // 10
        
        # Bonificación por dimensión actual: +2 fragmentos por dimensión
        dimension_bonus = (self.current_dimension - 1) * 2
        
        total_essence = base_essence[ascension_type] + level_bonus + dimension_bonus
        
        # Aplicar bonificación de ganancia de esencia
        total_essence = int(total_essence * self.essence_gain_bonus)
        
        return max(1, total_essence)
    
    def get_stat_bonus_from_essence(self, essence_fragments: int) -> float:
        """Calcula la bonificación de estadísticas basada en fragmentos de esencia.
        
        Args:
            essence_fragments: Número de fragmentos de esencia
            
        Returns:
            Multiplicador de estadísticas (1.0 = sin bonificación)
        """
        # Cada 10 fragmentos otorga +5% de bonificación
        bonus_percentage = (essence_fragments // 10) * 0.05
        return 1.0 + bonus_percentage
    
    def can_ascend(self, ascension_type: AscensionType, player_level: int, 
                   boss_defeated: bool = False, secret_dungeon_completed: bool = False) -> Tuple[bool, str]:
        """Verifica si se puede realizar una ascensión.
        
        Args:
            ascension_type: Tipo de ascensión a verificar
            player_level: Nivel actual del jugador
            boss_defeated: Si se derrotó al boss de la dimensión actual
            secret_dungeon_completed: Si se completó la mazmorra secreta (para ascensión mayor)
            
        Returns:
            Tupla (puede_ascender, mensaje_error)
        """
        level_requirements = {
            AscensionType.MINOR: 50,
            AscensionType.MAJOR: 100,
            AscensionType.DIMENSION: 200
        }
        
        required_level = level_requirements[ascension_type]
        
        # Verificar nivel mínimo
        if player_level < required_level:
            return False, f"Necesitas nivel {required_level} para esta ascensión (actual: {player_level})"
        
        # Verificar boss derrotado (requerido para todas las ascensiones)
        if not boss_defeated:
            return False, "Debes derrotar al boss de la dimensión actual antes de ascender"
        
        # Verificar requisitos específicos para ascensión mayor
        if ascension_type == AscensionType.MAJOR and not secret_dungeon_completed:
            return False, "Debes completar la mazmorra secreta para realizar una Ascensión Mayor"
        
        return True, ""
    
    def perform_ascension(self, ascension_type: AscensionType, player_level: int, 
                         boss_defeated: bool = False, secret_dungeon_completed: bool = False) -> Optional[DimensionalReward]:
        """Realiza una ascensión dimensional.
        
        Args:
            ascension_type: Tipo de ascensión a realizar
            player_level: Nivel actual del jugador
            boss_defeated: Si se derrotó al boss de la dimensión actual
            secret_dungeon_completed: Si se completó la mazmorra secreta
            
        Returns:
            DimensionalReward si la ascensión fue exitosa, None si falló
        """
        can_ascend, error_message = self.can_ascend(ascension_type, player_level, boss_defeated, secret_dungeon_completed)
        
        if not can_ascend:
            logging.warning(f"Ascensión fallida: {error_message}")
            return None
        
        # Calcular recompensas
        essence_gained = self.calculate_essence_gained(player_level, ascension_type)
        
        stat_bonuses = {
            AscensionType.MINOR: 0.25,   # +25% stats permanentes
            AscensionType.MAJOR: 0.50,   # +50% stats + nueva mazmorra secreta
            AscensionType.DIMENSION: 1.0 # +100% stats + nueva dimensión completa
        }
        
        stat_bonus = stat_bonuses[ascension_type]
        special_unlock = None
        
        # Determinar unlock especial
        if ascension_type == AscensionType.MAJOR:
            secret_dungeon_name = f"Cripta Dimensional {self.current_dimension}"
            special_unlock = f"secret_dungeon_{self.current_dimension}"
            self.unlocked_secret_dungeons.append(secret_dungeon_name)
            
        elif ascension_type == AscensionType.DIMENSION:
            new_dimension = self.current_dimension + 1
            special_unlock = f"dimension_{new_dimension}"
            self.unlocked_dimensions.append(new_dimension)
            self.current_dimension = new_dimension
        
        # Aplicar cambios
        self.essence_fragments += essence_gained
        self.total_ascensions += 1
        
        if ascension_type == AscensionType.MINOR:
            self.minor_ascensions += 1
        elif ascension_type == AscensionType.MAJOR:
            self.major_ascensions += 1
        elif ascension_type == AscensionType.DIMENSION:
            self.dimension_ascensions += 1
        
        # Recalcular bonificaciones
        self._update_bonuses()
        
        # Guardar cambios
        self.save_dimensional_data()
        
        # Crear recompensa
        reward = DimensionalReward(essence_gained, stat_bonus, special_unlock)
        
        logging.info(f"Ascensión {ascension_type.value} completada: +{essence_gained} fragmentos, +{stat_bonus*100}% stats")
        
        return reward
    
    def _update_bonuses(self):
        """Actualiza todas las bonificaciones basadas en el estado actual."""
        # Bonificación base de stats por fragmentos de esencia
        self.dimensional_stat_bonus = self.get_stat_bonus_from_essence(self.essence_fragments)
        
        # Bonificación de exploración por ascensiones mayores (cada una +10%)
        self.exploration_bonus = 1.0 + (self.major_ascensions * 0.10)
        
        # Bonificación de experiencia por dimensión actual (+20% por dimensión)
        self.experience_bonus = 1.0 + ((self.current_dimension - 1) * 0.20)
        
        # Bonificación de ganancia de esencia por ascensiones dimensionales (+25% cada una)
        self.essence_gain_bonus = 1.0 + (self.dimension_ascensions * 0.25)
        
        # FASE 5.2: Bonificaciones específicas de ascensión
        # +15% daño base permanente por ascensión total
        self.damage_bonus = 1.0 + (self.total_ascensions * 0.15)
        
        # +10% salud máxima permanente por ascensión total
        self.health_bonus = 1.0 + (self.total_ascensions * 0.10)
        
        # +20% velocidad de obtención de experiencia por ascensión mayor y dimensional
        elite_ascensions = self.major_ascensions + self.dimension_ascensions
        self.exp_speed_bonus = 1.0 + (elite_ascensions * 0.20)
        
        # +5% probabilidad de loot raro por ascensión (acumulativo)
        self.rare_loot_bonus = self.total_ascensions * 0.05
    
    def get_dimensional_stats(self) -> Dict:
        """Obtiene estadísticas completas del sistema dimensional.
        
        Returns:
            Diccionario con todas las estadísticas dimensionales
        """
        return {
            'total_ascensions': self.total_ascensions,
            'minor_ascensions': self.minor_ascensions,
            'major_ascensions': self.major_ascensions,
            'dimension_ascensions': self.dimension_ascensions,
            'essence_fragments': self.essence_fragments,
            'current_dimension': self.current_dimension,
            'dimensional_stat_bonus': self.dimensional_stat_bonus,
            'exploration_bonus': self.exploration_bonus,
            'experience_bonus': self.experience_bonus,
            'essence_gain_bonus': self.essence_gain_bonus,
            # FASE 5.2: Bonificaciones específicas de ascensión
            'damage_bonus': self.damage_bonus,
            'health_bonus': self.health_bonus,
            'exp_speed_bonus': self.exp_speed_bonus,
            'rare_loot_bonus': self.rare_loot_bonus,
            'unlocked_secret_dungeons': self.unlocked_secret_dungeons.copy(),
            'unlocked_dimensions': self.unlocked_dimensions.copy()
        }
    
    def load_dimensional_data(self):
        """Carga el estado dimensional desde la base de datos."""
        try:
            # Cargar estadísticas
            stats_result = self.database.execute('''
                SELECT total_ascensions, minor_ascensions, major_ascensions, 
                       dimension_ascensions, essence_fragments, current_dimension
                FROM dimensional_stats WHERE id = 1
            ''').fetchone()
            
            if stats_result:
                (self.total_ascensions, self.minor_ascensions, self.major_ascensions,
                 self.dimension_ascensions, self.essence_fragments, self.current_dimension) = stats_result
            
            # Cargar bonificaciones
            bonus_result = self.database.execute('''
                SELECT dimensional_stat_bonus, exploration_bonus, experience_bonus, essence_gain_bonus
                FROM dimensional_bonuses WHERE id = 1
            ''').fetchone()
            
            if bonus_result:
                (self.dimensional_stat_bonus, self.exploration_bonus, 
                 self.experience_bonus, self.essence_gain_bonus) = bonus_result
            
            # Cargar unlocks especiales
            unlocks_result = self.database.execute('''
                SELECT unlock_type, unlock_name FROM dimensional_unlocks
            ''').fetchall()
            
            for unlock_type, unlock_name in unlocks_result:
                if unlock_type == "secret_dungeon":
                    self.unlocked_secret_dungeons.append(unlock_name)
                elif unlock_type == "dimension":
                    dimension_num = int(unlock_name.split('_')[-1])
                    if dimension_num not in self.unlocked_dimensions:
                        self.unlocked_dimensions.append(dimension_num)
            
            # Actualizar bonificaciones
            self._update_bonuses()
            
            logging.info(f"Prestigio dimensional cargado: {self.essence_fragments} fragmentos, dimensión {self.current_dimension}")
        
        except Exception as e:
            logging.error(f"Error cargando datos dimensionales: {e}")
    
    def save_dimensional_data(self):
        """Guarda el estado dimensional en la base de datos."""
        try:
            # Guardar estadísticas
            self.database.execute('''
                UPDATE dimensional_stats SET 
                total_ascensions = ?, minor_ascensions = ?, major_ascensions = ?,
                dimension_ascensions = ?, essence_fragments = ?, current_dimension = ?
                WHERE id = 1
            ''', (self.total_ascensions, self.minor_ascensions, self.major_ascensions,
                  self.dimension_ascensions, self.essence_fragments, self.current_dimension))
            
            # Guardar bonificaciones
            self.database.execute('''
                UPDATE dimensional_bonuses SET 
                dimensional_stat_bonus = ?, exploration_bonus = ?, 
                experience_bonus = ?, essence_gain_bonus = ?
                WHERE id = 1
            ''', (self.dimensional_stat_bonus, self.exploration_bonus,
                  self.experience_bonus, self.essence_gain_bonus))
            
            logging.debug("Datos dimensionales guardados exitosamente")
        
        except Exception as e:
            logging.error(f"Error guardando datos dimensionales: {e}")
    
    def get_ascension_preview(self, ascension_type: AscensionType, player_level: int) -> Dict:
        """Obtiene una preview de las recompensas de una ascensión.
        
        Args:
            ascension_type: Tipo de ascensión a previsualizar
            player_level: Nivel actual del jugador
            
        Returns:
            Diccionario con información de la preview
        """
        essence_gain = self.calculate_essence_gained(player_level, ascension_type)
        
        stat_bonuses = {
            AscensionType.MINOR: 0.25,
            AscensionType.MAJOR: 0.50,
            AscensionType.DIMENSION: 1.0
        }
        
        special_unlocks = {
            AscensionType.MINOR: None,
            AscensionType.MAJOR: f"Cripta Dimensional {self.current_dimension}",
            AscensionType.DIMENSION: f"Dimensión {self.current_dimension + 1}"
        }
        
        return {
            'essence_fragments_gain': essence_gain,
            'stat_bonus_percentage': stat_bonuses[ascension_type] * 100,
            'special_unlock': special_unlocks[ascension_type],
            'new_total_essence': self.essence_fragments + essence_gain,
            'new_stat_bonus': self.get_stat_bonus_from_essence(self.essence_fragments + essence_gain)
        }
    
    def get_combat_bonuses(self) -> Dict[str, float]:
        """Obtiene todas las bonificaciones aplicables al combate.
        
        Returns:
            Diccionario con bonificaciones para el sistema de combate
        """
        return {
            'damage_multiplier': self.damage_bonus,           # +15% por ascensión
            'health_multiplier': self.health_bonus,           # +10% por ascensión
            'stat_multiplier': self.dimensional_stat_bonus,   # Por fragmentos de esencia
            'exploration_speed': self.exploration_bonus,      # Por ascensiones mayores
            'experience_gain': self.exp_speed_bonus           # +20% por ascensiones elite
        }
    
    def get_loot_bonuses(self) -> Dict[str, float]:
        """Obtiene todas las bonificaciones aplicables al sistema de loot.
        
        Returns:
            Diccionario con bonificaciones para el sistema de loot
        """
        return {
            'rare_loot_chance': self.rare_loot_bonus,         # +5% por ascensión
            'exploration_bonus': self.exploration_bonus,      # Afecta loot en mazmorras
            'essence_gain_multiplier': self.essence_gain_bonus # Para futuros drops de esencia
        }
    
    def apply_dimensional_bonuses_to_stats(self, base_stats: Dict[str, float]) -> Dict[str, float]:
        """Aplica todas las bonificaciones dimensionales a estadísticas base.
        
        Args:
            base_stats: Estadísticas base del jugador
            
        Returns:
            Estadísticas modificadas con bonificaciones dimensionales
        """
        modified_stats = base_stats.copy()
        
        # Aplicar bonificaciones multiplicativas
        if 'damage' in modified_stats:
            modified_stats['damage'] *= self.damage_bonus
        
        if 'max_health' in modified_stats:
            modified_stats['max_health'] *= self.health_bonus
        
        # Aplicar bonificación general de stats por fragmentos de esencia
        for stat_name in ['damage', 'defense', 'speed']:
            if stat_name in modified_stats:
                modified_stats[stat_name] *= self.dimensional_stat_bonus
        
        return modified_stats
