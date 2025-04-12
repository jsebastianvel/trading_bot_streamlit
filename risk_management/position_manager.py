"""
Módulo para gestión de riesgo y manejo de posiciones
"""

class PositionManager:
    def __init__(self, config=None):
        """
        Inicializa el gestor de posiciones con configuración personalizable
        
        Args:
            config: Diccionario con configuración de gestión de riesgo
        """
        default_config = {
            'stop_loss_pct': 0.02,      # 2% stop loss
            'take_profit_pct': 0.04,    # 4% take profit
            'trailing_stop_pct': 0.015,  # 1.5% trailing stop
            'max_position_size': 0.05    # 5% del capital (cambiado de 0.95)
        }
        
        config = config or {}
        self.stop_loss_pct = config.get('stop_loss_pct', default_config['stop_loss_pct'])
        self.take_profit_pct = config.get('take_profit_pct', default_config['take_profit_pct'])
        self.trailing_stop_pct = config.get('trailing_stop_pct', default_config['trailing_stop_pct'])
        self.max_position_size = config.get('max_position_size', default_config['max_position_size'])
        
        # Estado de la posición actual
        self.current_position = None
    
    def calculate_position_size(self, capital, entry_price):
        """
        Calcula el tamaño óptimo de la posición basado en el capital disponible
        """
        return (capital * self.max_position_size) / entry_price
    
    def open_position(self, position_type, entry_price, entry_time, capital, signals=None):
        """
        Abre una nueva posición
        
        Args:
            position_type: 'long' o 'short'
            entry_price: Precio de entrada
            entry_time: Timestamp de entrada
            capital: Capital disponible
            signals: Señales que generaron la entrada
        """
        size = self.calculate_position_size(capital, entry_price)
        
        self.current_position = {
            'type': position_type,
            'entry_price': entry_price,
            'entry_time': entry_time,
            'size': size,
            'signals': signals or [],
            'highest_price': entry_price,
            'lowest_price': entry_price,
            'trailing_stop': self._calculate_trailing_stop(position_type, entry_price)
        }
        
        return self.current_position
    
    def _calculate_trailing_stop(self, position_type, reference_price):
        """Calcula el nivel de trailing stop"""
        if position_type == 'long':
            return reference_price * (1 - self.trailing_stop_pct)
        return reference_price * (1 + self.trailing_stop_pct)
    
    def check_exit_signals(self, current_price, current_time=None):
        """
        Verifica todas las condiciones de salida
        
        Returns:
            tuple: (debe_salir, razón, precio_salida)
        """
        if not self.current_position:
            return False, None, None
            
        # Actualizar precios máximos/mínimos
        if self.current_position['type'] == 'long':
            if current_price > self.current_position['highest_price']:
                self.current_position['highest_price'] = current_price
                self.current_position['trailing_stop'] = self._calculate_trailing_stop('long', current_price)
        else:  # short
            if current_price < self.current_position['lowest_price']:
                self.current_position['lowest_price'] = current_price
                self.current_position['trailing_stop'] = self._calculate_trailing_stop('short', current_price)
        
        # Verificar stop loss
        stop_loss_hit = self._check_stop_loss(current_price)
        if stop_loss_hit:
            return True, 'stop_loss', current_price
            
        # Verificar take profit
        take_profit_hit = self._check_take_profit(current_price)
        if take_profit_hit:
            return True, 'take_profit', current_price
            
        # Verificar trailing stop
        trailing_stop_hit = self._check_trailing_stop(current_price)
        if trailing_stop_hit:
            return True, 'trailing_stop', current_price
            
        return False, None, None
    
    def _check_stop_loss(self, current_price):
        """Verifica si se ha alcanzado el stop loss"""
        if self.current_position['type'] == 'long':
            stop_price = self.current_position['entry_price'] * (1 - self.stop_loss_pct)
            return current_price <= stop_price
        else:  # short
            stop_price = self.current_position['entry_price'] * (1 + self.stop_loss_pct)
            return current_price >= stop_price
    
    def _check_take_profit(self, current_price):
        """Verifica si se ha alcanzado el take profit"""
        if self.current_position['type'] == 'long':
            take_profit_price = self.current_position['entry_price'] * (1 + self.take_profit_pct)
            return current_price >= take_profit_price
        else:  # short
            take_profit_price = self.current_position['entry_price'] * (1 - self.take_profit_pct)
            return current_price <= take_profit_price
    
    def _check_trailing_stop(self, current_price):
        """Verifica si se ha alcanzado el trailing stop"""
        if self.current_position['type'] == 'long':
            return current_price <= self.current_position['trailing_stop']
        else:  # short
            return current_price >= self.current_position['trailing_stop']
    
    def close_position(self, exit_price, exit_time, exit_reason='signal', exit_signals=None):
        """
        Cierra la posición actual
        
        Returns:
            dict: Detalles de la operación cerrada
        """
        if not self.current_position:
            return None
            
        trade = {
            'type': self.current_position['type'],
            'entry_time': self.current_position['entry_time'],
            'exit_time': exit_time,
            'entry_price': self.current_position['entry_price'],
            'exit_price': exit_price,
            'size': self.current_position['size'],
            'pnl': self._calculate_pnl(exit_price),
            'exit_reason': exit_reason,
            'entry_signals': self.current_position['signals'],
            'exit_signals': exit_signals or [],
            'stop_loss_price': self.current_position.get('stop_loss_price'),
            'take_profit_price': self.current_position.get('take_profit_price')
        }
        
        self.current_position = None
        return trade
    
    def _calculate_pnl(self, exit_price):
        """Calcula el P&L de la operación"""
        if self.current_position['type'] == 'long':
            return self.current_position['size'] * (exit_price - self.current_position['entry_price'])
        else:  # short
            return self.current_position['size'] * (self.current_position['entry_price'] - exit_price)
    
    def get_current_position(self):
        """Retorna la posición actual"""
        return self.current_position 