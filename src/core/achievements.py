"""
Sistema de logros para SiKIdle - Versión simplificada para pruebas.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any


class AchievementCategory(Enum):
    """Categorías de logros disponibles en el juego."""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    LOOT = "loot"
    SURVIVAL = "survival"
    SPECIAL = "special"


@dataclass
class AchievementReward:
    """Recompensa obtenida al completar un logro."""
    talent_points: int = 0
    essence_fragments: int = 0
    special_item: Optional[str] = None


@dataclass
class Achievement:
    """Definición de un logro del juego."""
    id: str
    name: str
    description: str
    category: AchievementCategory
    target_value: int
    reward: AchievementReward
    current_progress: int = 0
    completed: bool = False
    completion_date: Optional[datetime] = None
    
    def update_progress(self, increment: int = 1) -> bool:
        """Actualiza el progreso del logro."""
        if self.completed:
            return False
        
        self.current_progress += increment
        
        if self.current_progress >= self.target_value:
            self.completed = True
            self.completion_date = datetime.now()
            return True
        
        return False
    
    def get_progress_percentage(self) -> float:
        """Obtiene el porcentaje de progreso del logro."""
        if self.target_value <= 0:
            return 0.0
        
        return min(100.0, (self.current_progress / self.target_value) * 100.0)
    
    def get_symbol(self) -> str:
        """Obtiene el símbolo emoji del logro basado en su categoría."""
        category_symbols = {
            AchievementCategory.COMBAT: "⚔️",
            AchievementCategory.EXPLORATION: "🗺️",
            AchievementCategory.LOOT: "💰",
            AchievementCategory.SURVIVAL: "🛡️",
            AchievementCategory.SPECIAL: "⭐"
        }
        
        return category_symbols.get(self.category, "🏆")


class AchievementManager:
    """Gestor del sistema de logros del juego."""
    
    def __init__(self, database_manager=None):
        """Inicializa el gestor de logros."""
        self.database_manager = database_manager
        self.achievements: Dict[str, Achievement] = {}
        self.completion_callbacks: List[Callable[[Achievement], None]] = []
        
        # Crear logros predefinidos
        self._create_default_achievements()
        
        logging.info(f"AchievementManager initialized with {len(self.achievements)} achievements")
    
    def _create_default_achievements(self):
        """Crea los logros predefinidos del juego."""
        default_achievements = [
            Achievement(
                id="first_kill",
                name="Primera Sangre",
                description="Derrota tu primer enemigo",
                category=AchievementCategory.COMBAT,
                target_value=1,
                reward=AchievementReward(talent_points=1, essence_fragments=5)
            ),
            Achievement(
                id="kill_100_enemies",
                name="Cazador",
                description="Derrota 100 enemigos",
                category=AchievementCategory.COMBAT,
                target_value=100,
                reward=AchievementReward(talent_points=3, essence_fragments=25)
            ),
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement
        
        logging.info(f"Created {len(default_achievements)} default achievements")
    
    def update_progress(self, achievement_id: str, increment: int = 1) -> bool:
        """Actualiza el progreso de un logro específico."""
        if achievement_id not in self.achievements:
            logging.warning(f"Achievement {achievement_id} not found")
            return False
        
        achievement = self.achievements[achievement_id]
        return achievement.update_progress(increment)
    
    def get_all_achievements(self) -> List[Achievement]:
        """Obtiene todos los logros del juego."""
        return list(self.achievements.values())
    
    def get_achievements_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Obtiene todos los logros de una categoría específica."""
        return [
            achievement for achievement in self.achievements.values()
            if achievement.category == category
        ]
    
    def get_completed_achievements(self) -> List[Achievement]:
        """Obtiene todos los logros completados."""
        return [
            achievement for achievement in self.achievements.values()
            if achievement.completed
        ]
    
    def get_completion_percentage(self) -> float:
        """Calcula el porcentaje de logros completados."""
        if not self.achievements:
            return 0.0
        
        completed_count = len(self.get_completed_achievements())
        total_count = len(self.achievements)
        
        return (completed_count / total_count) * 100.0
