# -*- coding: utf-8 -*-
"""
Motor de backtesting para estrategias de trading
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy.macd_strategy import check_macd_signal
from utils.api_data import get_price_data
from config import TIMEFRAMES, SIGNAL_WEIGHTS, SIGNAL_THRESHOLD
from .metrics import calculate_statistics
from risk_management.position_manager import PositionManager
import pandas_ta as ta

class BacktestEngine:
    """
    Motor de backtesting para simular estrategias de trading en datos históricos
    """
    
    def __init__(self, symbol, start_date, end_date, initial_capital=1000.0, timeframes=None, risk_config=None):
        """
        Inicializa el motor de backtesting
        
        Args:
            symbol: Par de trading (ej. 'BTC/USDT')
            start_date: Fecha de inicio (datetime)
            end_date: Fecha de fin (datetime)
            initial_capital: Capital inicial para la simulación (por defecto 1000.0)
            timeframes: Lista de temporalidades a analizar (por defecto ['4h'])
            risk_config: Configuración de gestión de riesgo (por defecto None)
        """
        self.symbol = symbol
        self.start_date = start_date - timedelta(days=2)  # 2 días extra para cálculo de MACD
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.timeframes = timeframes or ['4h']
        
        # Inicializar gestor de posiciones
        self.position_manager = PositionManager(risk_config)
        
        # Cargar datos históricos
        self.data = self._load_historical_data()
        
        if not self.data:
            raise ValueError(f"No se pudieron obtener datos históricos para {symbol}")

    def _load_historical_data(self):
        """
        Carga todos los datos históricos necesarios de una sola vez
        """
        data = {}
        print("\n🔄 Descargando datos históricos...")
        
        for tf in self.timeframes:
            print(f"📊 Descargando {tf} para {self.symbol}")
            df = get_price_data(
                symbol=self.symbol,
                start_date=self.start_date,
                end_date=self.end_date,
                timeframe=tf
            )
            
            if df is not None and not df.empty:
                if len(df) >= 35:  # Verificar datos suficientes para MACD
                    # Calcular MACD usando pandas_ta
                    macd = df.ta.macd(close='close', fast=12, slow=26, signal=9)
                    df['MACD_12_26_9'] = macd['MACD_12_26_9']
                    df['MACDs_12_26_9'] = macd['MACDs_12_26_9']
                    df['MACDh_12_26_9'] = macd['MACDh_12_26_9']
                    data[tf] = df
                    print(f"✅ {len(df)} períodos cargados para {tf}")
                else:
                    print(f"⚠️ Insuficientes datos para {tf} ({len(df)} períodos)")
            else:
                print(f"❌ No hay datos disponibles para {tf}")
        
        return data

    def run(self):
        """
        Ejecuta el backtesting y retorna los resultados
        """
        print("\n🔄 Ejecutando backtesting...")
        
        trades = []
        price_data = {}
        drawdown_data = {}
        balance_history = {}
        current_capital = self.initial_capital
        max_capital = current_capital
        
        # Registrar balance inicial
        balance_history[self.start_date.isoformat()] = current_capital
        
        # Obtener timestamps únicos del primer timeframe
        main_tf = self.timeframes[0]
        if main_tf not in self.data:
            raise ValueError(f"No hay datos disponibles para {main_tf}")
        
        timestamps = self.data[main_tf].index
        
        # Iterar sobre cada timestamp
        for timestamp in timestamps:
            current_price = self.data[main_tf].loc[timestamp, 'close']
            
            # Si hay una posición abierta, verificar señales de salida
            if self.position_manager.get_current_position():
                should_exit, exit_reason, _ = self.position_manager.check_exit_signals(current_price)
                
                if should_exit:
                    trade = self.position_manager.close_position(
                        exit_price=current_price,
                        exit_time=timestamp,
                        exit_reason=exit_reason
                    )
                    
                    trades.append(trade)
                    current_capital += trade['pnl']
                    
                    if current_capital > max_capital:
                        max_capital = current_capital
                    
                    print(f"\n📊 Cerrada posición {trade['type']} por {exit_reason} a {current_price:.2f} (P&L: {trade['pnl']:.2f})")
                    continue

            # Generar señales para cada timeframe
            signals = []
            for tf in self.timeframes:
                if tf in self.data:
                    df_slice = self.data[tf][self.data[tf].index <= timestamp].copy()
                    if len(df_slice) >= 35:
                        signal, strength = check_macd_signal(df_slice, tf)
                        if signal:
                            signals.append({
                                'timestamp': timestamp,
                                'timeframe': tf,
                                'signal': signal,
                                'strength': strength
                            })
                        
                        # Guardar datos de precio y MACD
                        if tf == main_tf:
                            last_row = df_slice.iloc[-1]
                            price_data[timestamp] = {
                                'open': last_row['open'],
                                'high': last_row['high'],
                                'low': last_row['low'],
                                'close': last_row['close'],
                                'MACD_12_26_9': last_row['MACD_12_26_9'],
                                'MACDs_12_26_9': last_row['MACDs_12_26_9'],
                                'MACDh_12_26_9': last_row['MACDh_12_26_9']
                            }
            
            # Procesar señales de entrada
            if not self.position_manager.get_current_position():
                for signal in signals:
                    if signal['signal'] in ['buy', 'valley_buy']:
                        position = self.position_manager.open_position(
                            position_type='long',
                            entry_price=current_price,
                            entry_time=timestamp,
                            capital=current_capital,
                            signals=signals
                        )
                        # Añadir stop loss y take profit a la posición
                        position['stop_loss_price'] = current_price * (1 - self.position_manager.stop_loss_pct)
                        position['take_profit_price'] = current_price * (1 + self.position_manager.take_profit_pct)
                        print(f"\n📈 Abierta posición long a {current_price:.2f}")
                        print(f"🛑 Stop Loss: {position['stop_loss_price']:.2f}")
                        print(f"✅ Take Profit: {position['take_profit_price']:.2f}")
                        break
                    elif signal['signal'] in ['sell', 'top_sell']:
                        position = self.position_manager.open_position(
                            position_type='short',
                            entry_price=current_price,
                            entry_time=timestamp,
                            capital=current_capital,
                            signals=signals
                        )
                        # Añadir stop loss y take profit a la posición
                        position['stop_loss_price'] = current_price * (1 + self.position_manager.stop_loss_pct)
                        position['take_profit_price'] = current_price * (1 - self.position_manager.take_profit_pct)
                        print(f"\n📉 Abierta posición short a {current_price:.2f}")
                        print(f"🛑 Stop Loss: {position['stop_loss_price']:.2f}")
                        print(f"✅ Take Profit: {position['take_profit_price']:.2f}")
                        break
            
            # Registrar balance actual
            balance_history[timestamp.isoformat()] = current_capital
            
            # Calcular drawdown
            if current_capital < max_capital:
                drawdown = (max_capital - current_capital) / max_capital * 100
            else:
                drawdown = 0
            drawdown_data[timestamp] = {'drawdown': drawdown}
        
        # Calcular estadísticas finales
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = len([t for t in trades if t['pnl'] < 0])
        total_trades = len(trades)
        
        results = {
            'symbol': self.symbol,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'timeframes': self.timeframes,
            'initial_capital': self.initial_capital,
            'final_capital': current_capital,
            'total_return': ((current_capital - self.initial_capital) / self.initial_capital) * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'max_drawdown': max(d['drawdown'] for d in drawdown_data.values()) if drawdown_data else 0,
            'profit_factor': self._calculate_profit_factor(trades),
            'trades': trades,
            'price_data': price_data,
            'drawdown': drawdown_data,
            'balance_history': balance_history
        }
        
        return results
    
    def _calculate_profit_factor(self, trades):
        """
        Calcula el factor de beneficio de las operaciones
        """
        total_gain = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        total_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        return total_gain / total_loss if total_loss > 0 else float('inf')

    def _print_results(self):
        """
        Imprime los resultados del backtest
        """
        print("\n📊 Resultados del Backtest")
        print("═" * 40)
        print(f"💰 Capital Inicial: ${self.initial_capital:,.2f}")
        print(f"💵 Capital Final: ${self.results['final_capital']:,.2f}")
        print(f"📈 Retorno Total: {self.results['total_return']:.2f}%")
        print(f"🔄 Operaciones Totales: {self.results['total_trades']}")
        print(f"✅ Operaciones Ganadoras: {self.results['winning_trades']}")
        print(f"❌ Operaciones Perdedoras: {self.results['losing_trades']}")
        print(f"📊 Win Rate: {self.results['win_rate']:.2f}%")
        print(f"📉 Máximo Drawdown: {self.results['max_drawdown']:.2f}%")
        print(f"📈 Factor de Beneficio: {self.results['profit_factor']:.2f}")
        print("═" * 40) 