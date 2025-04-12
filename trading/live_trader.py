# -*- coding: utf-8 -*-
"""
Módulo para trading en vivo con Binance
"""

import time
from datetime import datetime
import threading
from queue import Queue
import pandas as pd
from strategy.macd_strategy import check_macd_signal
from utils.api_data import get_price_data
from utils.telegram_notifications import TelegramNotifier
from config import TIMEFRAMES, SIGNAL_WEIGHTS, SIGNAL_THRESHOLD

class LiveTrader:
    def __init__(self, exchange_client, symbol, risk_config=None):
        """
        Inicializa el trader en vivo
        
        Args:
            exchange_client: Cliente del exchange (Binance)
            symbol: Par de trading (ej. 'BTC/USDT')
            risk_config: Configuración de gestión de riesgo
        """
        self.exchange = exchange_client
        self.symbol = symbol
        self.risk_config = risk_config or {}
        self.is_running = False
        self.trading_thread = None
        self.signal_queue = Queue()
        self.notifier = TelegramNotifier()
        
        # Estado del trader
        self.current_position = None
        self.last_signal_time = {}
        self.trading_enabled = False
    
    def start(self):
        """Inicia el proceso de trading"""
        if not self.is_running:
            self.is_running = True
            self.trading_thread = threading.Thread(target=self._trading_loop)
            self.trading_thread.start()
            self.notifier.send_message("🟢 Trading Bot iniciado")
    
    def stop(self):
        """Detiene el proceso de trading"""
        if self.is_running:
            self.is_running = False
            if self.trading_thread:
                self.trading_thread.join()
            self.notifier.send_message("🔴 Trading Bot detenido")
    
    def enable_trading(self):
        """Activa la ejecución de operaciones"""
        self.trading_enabled = True
        self.notifier.send_message("✅ Ejecución de operaciones activada")
    
    def disable_trading(self):
        """Desactiva la ejecución de operaciones"""
        self.trading_enabled = False
        self.notifier.send_message("⛔ Ejecución de operaciones desactivada")
    
    def _trading_loop(self):
        """Bucle principal de trading"""
        while self.is_running:
            try:
                # Analizar mercado cada minuto
                self._analyze_market()
                time.sleep(60)
            except Exception as e:
                self.notifier.send_error(str(e), "Error en bucle de trading")
                time.sleep(60)  # Esperar antes de reintentar
    
    def _analyze_market(self):
        """Analiza el mercado y genera señales"""
        signals = []
        
        for tf in TIMEFRAMES:
            try:
                # Evitar análisis muy frecuente en timeframes mayores
                current_time = datetime.now()
                if tf in self.last_signal_time:
                    time_diff = (current_time - self.last_signal_time[tf]).total_seconds()
                    min_interval = self._get_min_interval(tf)
                    if time_diff < min_interval:
                        continue
                
                # Obtener datos y analizar
                df = get_price_data(self.symbol, tf)
                signal, strength = check_macd_signal(df, tf)
                
                if signal != 'hold':
                    signals.append({
                        'timeframe': tf,
                        'signal': signal,
                        'strength': strength,
                        'weight': TIMEFRAMES[tf]
                    })
                    self.last_signal_time[tf] = current_time
                    
                    # Notificar señal
                    self.notifier.send_trade_signal(
                        timeframe=tf,
                        signal=signal,
                        strength=strength,
                        price=df['close'].iloc[-1]
                    )
            
            except Exception as e:
                self.notifier.send_error(str(e), f"Error en análisis de {tf}")
        
        # Procesar señales si el trading está habilitado
        if self.trading_enabled and signals:
            self._process_signals(signals)
    
    def _process_signals(self, signals):
        """Procesa las señales y ejecuta operaciones si es apropiado"""
        peso_buy = 0
        peso_sell = 0
        
        for signal in signals:
            peso_signal = SIGNAL_WEIGHTS.get(signal['signal'], 0) * signal['strength']
            
            if signal['signal'] in ['buy', 'valley_buy']:
                peso_buy += signal['weight'] * peso_signal
            elif signal['signal'] in ['sell', 'top_sell']:
                peso_sell += signal['weight'] * peso_signal
        
        # Ejecutar operación si se supera el umbral
        if peso_buy - peso_sell >= SIGNAL_THRESHOLD:
            self._execute_trade('buy')
        elif peso_sell - peso_buy >= SIGNAL_THRESHOLD:
            self._execute_trade('sell')
    
    def _execute_trade(self, direction):
        """Ejecuta una operación en el mercado"""
        if not self.trading_enabled:
            return
        
        try:
            # Aquí iría la lógica de ejecución de órdenes
            # Por ahora solo notificamos
            self.notifier.send_message(
                f"🔄 Señal de {direction.upper()} detectada en {self.symbol}\n"
                "⚠️ Ejecución automática pendiente de implementar"
            )
        
        except Exception as e:
            self.notifier.send_error(str(e), "Error al ejecutar operación")
    
    def _get_min_interval(self, timeframe):
        """Obtiene el intervalo mínimo entre análisis según el timeframe"""
        # Convertir timeframe a segundos
        tf_multipliers = {
            '15m': 900,    # 15 * 60
            '30m': 1800,   # 30 * 60
            '1h': 3600,    # 60 * 60
            '4h': 14400,   # 4 * 60 * 60
            '1d': 86400,   # 24 * 60 * 60
            '3d': 259200   # 3 * 24 * 60 * 60
        }
        
        # Retornar 1/4 del timeframe como intervalo mínimo
        return tf_multipliers.get(timeframe, 3600) / 4 