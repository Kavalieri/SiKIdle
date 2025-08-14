"""Sistema de gestión de assets visuales para SiKIdle.

Maneja el mapeo de mundos a fondos temáticos, efectos visuales,
y optimización de carga de assets para performance móvil.

Inspirado en los mejores idle clickers del mercado.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class BackgroundType(Enum):
    """Tipos de fondos disponibles en el juego."""
    # Fondos de mundos temáticos
    FOREST = "forest"
    DESERT = "desert" 
    SNOW = "snow"
    DUNGEON = "dungeon"
    BEACH = "beach"
    CITY = "city"
    INDUSTRIAL = "industrial"
    SPACE = "space"
    NETHER = "nether"
    
    # Fondos especiales de UI
    MAIN = "main"           # Fondo principal sin logo
    TITLE = "title"         # Pantalla de bienvenida con logo
    TITLE2 = "title2"       # Variante de título
    TITLE3 = "title3"       # Variante de título
    TITLE4 = "title4"       # Variante de título


class EffectType(Enum):
    """Tipos de efectos visuales disponibles."""
    FIRE = "fire"           # Efectos de fuego
    ICE = "ice"             # Efectos de hielo
    VENOM = "venom"         # Efectos de veneno
    SHOCK = "shock"         # Efectos eléctricos
    BLOOD = "blood"         # Efectos de sangre
    LIGHT = "light"         # Efectos de luz sagrada
    SLIME = "slime"         # Efectos viscosos
    MUD = "mud"             # Efectos terrestres


@dataclass
class WorldVisualTheme:
    """Tema visual completo para un mundo."""
    name: str
    background: BackgroundType
    primary_effect: EffectType
    secondary_effects: List[EffectType]
    color_scheme: Dict[str, str]        # Colores principales del tema
    ambient_description: str            # Descripción del ambiente
    ui_tint: str                       # Tinte para elementos UI
    
    # Configuración de efectos por tipo de enemigo
    basic_enemy_effects: List[EffectType]
    intermediate_enemy_effects: List[EffectType]
    advanced_enemy_effects: List[EffectType]
    elite_enemy_effects: List[EffectType]
    boss_effect: EffectType


@dataclass
class AssetInfo:
    """Información sobre un asset específico."""
    path: str
    size_kb: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    loaded: bool = False
    last_used: Optional[float] = None


class VisualAssetManager:
    """Gestor de assets visuales del juego."""
    
    def __init__(self):
        """Inicializa el gestor de assets visuales."""
        self.assets_base_path = Path("assets")
        self.background_path = self.assets_base_path / "background"
        self.effects_path = self.assets_base_path / "effects"
        
        # Cache de assets cargados
        self.loaded_backgrounds: Dict[BackgroundType, AssetInfo] = {}
        self.loaded_effects: Dict[EffectType, AssetInfo] = {}
        
        # Configuración de temas visuales por mundo
        self.world_themes: Dict[str, WorldVisualTheme] = {}
        
        # Inicializar temas
        self._initialize_world_themes()
        
        logger.info("VisualAssetManager inicializado")
    
    def _initialize_world_themes(self) -> None:
        """Inicializa los temas visuales para todos los mundos."""
        
        # Mundo 1: Bosque Encantado
        self.world_themes["enchanted_forest"] = WorldVisualTheme(
            name="Bosque Encantado",
            background=BackgroundType.FOREST,
            primary_effect=EffectType.VENOM,
            secondary_effects=[EffectType.LIGHT, EffectType.MUD],
            color_scheme={
                "primary": "#2E7D32",      # Verde bosque
                "secondary": "#4CAF50",    # Verde claro
                "accent": "#8BC34A",       # Verde lima
                "danger": "#795548"        # Marrón tierra
            },
            ambient_description="Un bosque mágico con luz filtrada y criaturas místicas",
            ui_tint="#2E7D32AA",
            basic_enemy_effects=[EffectType.MUD],
            intermediate_enemy_effects=[EffectType.VENOM],
            advanced_enemy_effects=[EffectType.LIGHT, EffectType.VENOM],
            elite_enemy_effects=[EffectType.LIGHT, EffectType.VENOM, EffectType.MUD],
            boss_effect=EffectType.LIGHT
        )
        
        # Mundo 2: Desierto Ardiente
        self.world_themes["burning_desert"] = WorldVisualTheme(
            name="Desierto Ardiente",
            background=BackgroundType.DESERT,
            primary_effect=EffectType.FIRE,
            secondary_effects=[EffectType.LIGHT, EffectType.MUD],
            color_scheme={
                "primary": "#FF5722",      # Naranja fuego
                "secondary": "#FF9800",    # Naranja
                "accent": "#FFC107",       # Amarillo arena
                "danger": "#D32F2F"        # Rojo intenso
            },
            ambient_description="Un desierto abrasador con tormentas de arena y mirajes",
            ui_tint="#FF5722AA",
            basic_enemy_effects=[EffectType.MUD],
            intermediate_enemy_effects=[EffectType.FIRE],
            advanced_enemy_effects=[EffectType.FIRE, EffectType.LIGHT],
            elite_enemy_effects=[EffectType.FIRE, EffectType.LIGHT, EffectType.MUD],
            boss_effect=EffectType.FIRE
        )
        
        # Mundo 3: Montañas Heladas
        self.world_themes["frozen_mountains"] = WorldVisualTheme(
            name="Montañas Heladas",
            background=BackgroundType.SNOW,
            primary_effect=EffectType.ICE,
            secondary_effects=[EffectType.LIGHT, EffectType.SHOCK],
            color_scheme={
                "primary": "#0277BD",      # Azul hielo
                "secondary": "#03A9F4",    # Azul claro
                "accent": "#81D4FA",       # Azul muy claro
                "danger": "#37474F"        # Gris oscuro
            },
            ambient_description="Montañas cubiertas de nieve eterna con vientos helados",
            ui_tint="#0277BDAA",
            basic_enemy_effects=[EffectType.ICE],
            intermediate_enemy_effects=[EffectType.ICE, EffectType.SHOCK],
            advanced_enemy_effects=[EffectType.ICE, EffectType.LIGHT],
            elite_enemy_effects=[EffectType.ICE, EffectType.LIGHT, EffectType.SHOCK],
            boss_effect=EffectType.ICE
        )
        
        # Mundo 4: Mazmorras Profundas
        self.world_themes["deep_dungeons"] = WorldVisualTheme(
            name="Mazmorras Profundas",
            background=BackgroundType.DUNGEON,
            primary_effect=EffectType.BLOOD,
            secondary_effects=[EffectType.SHOCK, EffectType.MUD],
            color_scheme={
                "primary": "#424242",      # Gris oscuro
                "secondary": "#616161",    # Gris medio
                "accent": "#9E9E9E",       # Gris claro
                "danger": "#B71C1C"        # Rojo sangre
            },
            ambient_description="Mazmorras subterráneas llenas de peligros y secretos oscuros",
            ui_tint="#424242AA",
            basic_enemy_effects=[EffectType.MUD],
            intermediate_enemy_effects=[EffectType.BLOOD],
            advanced_enemy_effects=[EffectType.BLOOD, EffectType.SHOCK],
            elite_enemy_effects=[EffectType.BLOOD, EffectType.SHOCK, EffectType.MUD],
            boss_effect=EffectType.BLOOD
        )
        
        # Mundo 5: Costa Tropical
        self.world_themes["tropical_coast"] = WorldVisualTheme(
            name="Costa Tropical",
            background=BackgroundType.BEACH,
            primary_effect=EffectType.LIGHT,
            secondary_effects=[EffectType.SLIME, EffectType.ICE],
            color_scheme={
                "primary": "#00BCD4",      # Cian océano
                "secondary": "#4DD0E1",    # Cian claro
                "accent": "#B2EBF2",       # Cian muy claro
                "danger": "#FF7043"        # Naranja coral
            },
            ambient_description="Una costa paradisíaca con aguas cristalinas y criaturas marinas",
            ui_tint="#00BCD4AA",
            basic_enemy_effects=[EffectType.SLIME],
            intermediate_enemy_effects=[EffectType.LIGHT, EffectType.SLIME],
            advanced_enemy_effects=[EffectType.LIGHT, EffectType.ICE],
            elite_enemy_effects=[EffectType.LIGHT, EffectType.ICE, EffectType.SLIME],
            boss_effect=EffectType.LIGHT
        )
        
        logger.info(f"Temas visuales inicializados: {len(self.world_themes)} mundos")
    
    def get_world_theme(self, world_id: str) -> Optional[WorldVisualTheme]:
        """Obtiene el tema visual de un mundo específico."""
        return self.world_themes.get(world_id)
    
    def get_background_path(self, background_type: BackgroundType) -> str:
        """Obtiene la ruta completa de un fondo."""
        return str(self.background_path / f"{background_type.value}.png")
    
    def get_effect_path(self, effect_type: EffectType) -> str:
        """Obtiene la ruta completa de un efecto."""
        return str(self.effects_path / f"{effect_type.value}.png")
    
    def preload_world_assets(self, world_id: str) -> bool:
        """Precarga todos los assets necesarios para un mundo."""
        theme = self.get_world_theme(world_id)
        if not theme:
            logger.warning(f"Tema no encontrado para mundo: {world_id}")
            return False
        
        try:
            # Precargar fondo
            bg_path = self.get_background_path(theme.background)
            if theme.background not in self.loaded_backgrounds:
                self.loaded_backgrounds[theme.background] = AssetInfo(
                    path=bg_path,
                    loaded=True
                )
            
            # Precargar efectos
            all_effects = [theme.primary_effect] + theme.secondary_effects
            for effect in all_effects:
                if effect not in self.loaded_effects:
                    effect_path = self.get_effect_path(effect)
                    self.loaded_effects[effect] = AssetInfo(
                        path=effect_path,
                        loaded=True
                    )
            
            logger.info(f"Assets precargados para mundo: {theme.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error precargando assets para {world_id}: {e}")
            return False
    
    def get_enemy_effects(self, world_id: str, enemy_tier: str) -> List[EffectType]:
        """Obtiene los efectos apropiados para un enemigo según su tier."""
        theme = self.get_world_theme(world_id)
        if not theme:
            return []
        
        effect_map = {
            "basic": theme.basic_enemy_effects,
            "intermediate": theme.intermediate_enemy_effects,
            "advanced": theme.advanced_enemy_effects,
            "elite": theme.elite_enemy_effects,
            "boss": [theme.boss_effect]
        }
        
        return effect_map.get(enemy_tier, [])
    
    def get_ui_theme_colors(self, world_id: str) -> Dict[str, str]:
        """Obtiene los colores del tema UI para un mundo."""
        theme = self.get_world_theme(world_id)
        if not theme:
            return {
                "primary": "#2196F3",
                "secondary": "#03DAC6", 
                "accent": "#FF4081",
                "danger": "#F44336"
            }
        
        return theme.color_scheme
    
    def cleanup_unused_assets(self) -> None:
        """Limpia assets no utilizados para liberar memoria."""
        import time
        current_time = time.time()
        cleanup_threshold = 300  # 5 minutos
        
        # Limpiar fondos no usados
        to_remove = []
        for bg_type, asset_info in self.loaded_backgrounds.items():
            if (asset_info.last_used and 
                current_time - asset_info.last_used > cleanup_threshold):
                to_remove.append(bg_type)
        
        for bg_type in to_remove:
            del self.loaded_backgrounds[bg_type]
        
        # Limpiar efectos no usados
        to_remove = []
        for effect_type, asset_info in self.loaded_effects.items():
            if (asset_info.last_used and 
                current_time - asset_info.last_used > cleanup_threshold):
                to_remove.append(effect_type)
        
        for effect_type in to_remove:
            del self.loaded_effects[effect_type]
        
        if to_remove:
            logger.info(f"Assets limpiados: {len(to_remove)} elementos")
    
    def get_all_available_worlds(self) -> List[Dict[str, str]]:
        """Obtiene lista de todos los mundos disponibles con su información visual."""
        worlds = []
        for world_id, theme in self.world_themes.items():
            worlds.append({
                "id": world_id,
                "name": theme.name,
                "background": theme.background.value,
                "primary_color": theme.color_scheme["primary"],
                "description": theme.ambient_description
            })
        
        return worlds
