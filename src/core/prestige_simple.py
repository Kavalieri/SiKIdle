"""
Sistema de Prestigio Simple para SiKIdle - Idle Clicker Tradicional.

Sistema básico de prestigio que resetea el progreso a cambio de cristales
que proporcionan multiplicadores permanentes.
"""

import logging
import math
from typing import Dict, Any


class PrestigeManager:
    """Gestor simple de prestigio para idle clicker."""
    
    def __init__(self, database):
        """Inicializa el gestor de prestigio.
        
        Args:
            database: Conexión a la base de datos
        """
        self.database = database
        
        # Estado del prestigio
        self.prestige_count = 0
        self.prestige_crystals = 0
        self.lifetime_coins = 0.0
        
        # Multiplicadores
        self.income_multiplier = 1.0
        self.click_multiplier = 1.0
        
        # Crear tablas y cargar datos
        self._create_tables()
        self.load_data()
        
        logging.info("Sistema de prestigio simple inicializado")
    
    def _create_tables(self):
        """Crea las tablas de prestigio en la base de datos."""
        try:
            self.database.execute('''
                CREATE TABLE IF NOT EXISTS prestige_simple (
                    id INTEGER PRIMARY KEY,
                    prestige_count INTEGER DEFAULT 0,
                    prestige_crystals INTEGER DEFAULT 0,
                    lifetime_coins REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar fila inicial si no existe
            self.database.execute('''
                INSERT OR IGNORE INTO prestige_simple (id) VALUES (1)
            ''')
            
            logging.debug("Tabla de prestigio simple creada/verificada")
            
        except Exception as e:
            logging.error(f"Error creando tabla de prestigio: {e}")
    
    def calculate_crystals_from_coins(self, total_coins: float) -> int:
        """Calcula cristales basado en monedas totales ganadas.
        
        Args:
            total_coins: Total de monedas ganadas en la vida
            
        Returns:
            Número de cristales que se ganarían
        """
        if total_coins < 100000:  # 100K mínimo para prestigio
            return 0
        
        # Fórmula simple: sqrt(total_coins / 100000)
        crystals = math.sqrt(total_coins / 100000)
        return max(1, int(crystals))
    
    def can_prestige(self, total_coins: float) -> bool:
        """Verifica si se puede hacer prestigio.
        
        Args:
            total_coins: Total de monedas ganadas
            
        Returns:
            True si se puede hacer prestigio
        """
        return total_coins >= 100000  # 100K mínimo
    
    def get_prestige_preview(self, total_coins: float) -> Dict[str, Any]:
        """Obtiene preview de lo que se ganaría con prestigio.
        
        Args:
            total_coins: Total de monedas ganadas
            
        Returns:
            Diccionario con información del prestigio
        """
        crystals_gained = self.calculate_crystals_from_coins(total_coins)
        new_total_crystals = self.prestige_crystals + crystals_gained
        new_multiplier = self.calculate_multiplier_from_crystals(new_total_crystals)
        
        return {
            'can_prestige': self.can_prestige(total_coins),
            'crystals_gained': crystals_gained,
            'total_crystals_after': new_total_crystals,
            'current_multiplier': self.income_multiplier,
            'new_multiplier': new_multiplier,
            'multiplier_increase': new_multiplier - self.income_multiplier
        }
    
    def calculate_multiplier_from_crystals(self, crystals: int) -> float:
        """Calcula multiplicador basado en cristales.
        
        Args:
            crystals: Número de cristales
            
        Returns:
            Multiplicador de ingresos
        """
        # Cada cristal da +20% de bonificación
        return 1.0 + (crystals * 0.20)
    
    def perform_prestige(self, total_coins: float) -> Dict[str, Any]:
        """Realiza el prestigio.
        
        Args:
            total_coins: Total de monedas ganadas
            
        Returns:
            Resultado del prestigio
        """
        if not self.can_prestige(total_coins):
            return {'success': False, 'reason': 'No cumple requisitos mínimos'}
        
        # Calcular cristales ganados
        crystals_gained = self.calculate_crystals_from_coins(total_coins)
        
        # Actualizar estado
        self.prestige_count += 1
        self.prestige_crystals += crystals_gained
        self.lifetime_coins += total_coins
        
        # Recalcular multiplicadores
        self.income_multiplier = self.calculate_multiplier_from_crystals(self.prestige_crystals)
        self.click_multiplier = self.income_multiplier  # Mismo multiplicador para clics
        
        # Guardar en base de datos
        self.save_data()
        
        logging.info(f"Prestigio realizado: +{crystals_gained} cristales, multiplicador: {self.income_multiplier:.2f}x")
        
        return {
            'success': True,
            'crystals_gained': crystals_gained,
            'total_crystals': self.prestige_crystals,
            'new_multiplier': self.income_multiplier,
            'prestige_count': self.prestige_count
        }
    
    def get_multipliers(self) -> Dict[str, float]:
        """Obtiene todos los multiplicadores actuales.
        
        Returns:
            Diccionario con multiplicadores
        """
        return {
            'income_multiplier': self.income_multiplier,
            'click_multiplier': self.click_multiplier,
            'building_multiplier': self.income_multiplier
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de prestigio.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'prestige_count': self.prestige_count,
            'prestige_crystals': self.prestige_crystals,
            'lifetime_coins': self.lifetime_coins,
            'income_multiplier': self.income_multiplier,
            'click_multiplier': self.click_multiplier
        }
    
    def save_data(self):
        """Guarda el estado de prestigio en la base de datos."""
        try:
            self.database.execute('''
                UPDATE prestige_simple 
                SET prestige_count = ?, prestige_crystals = ?, lifetime_coins = ?
                WHERE id = 1
            ''', (self.prestige_count, self.prestige_crystals, self.lifetime_coins))
            
            logging.debug("Datos de prestigio guardados")
            
        except Exception as e:
            logging.error(f"Error guardando datos de prestigio: {e}")
    
    def load_data(self):
        """Carga el estado de prestigio desde la base de datos."""
        try:
            result = self.database.execute('''
                SELECT prestige_count, prestige_crystals, lifetime_coins
                FROM prestige_simple WHERE id = 1
            ''').fetchone()
            
            if result:
                self.prestige_count, self.prestige_crystals, self.lifetime_coins = result
                
                # Recalcular multiplicadores
                self.income_multiplier = self.calculate_multiplier_from_crystals(self.prestige_crystals)
                self.click_multiplier = self.income_multiplier
                
                logging.info(f"Prestigio cargado: {self.prestige_crystals} cristales, {self.prestige_count} prestiges")
            
        except Exception as e:
            logging.error(f"Error cargando datos de prestigio: {e}")