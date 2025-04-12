# -*- coding: utf-8 -*-
"""
Script para ejecutar backtesting de la estrategia MACD
"""

import os
import json
from datetime import datetime, timedelta
import tempfile
from backtesting.engine import BacktestEngine
import numpy as np
import pandas as pd

def run_backtest(symbol='BTC/USDT', start_date=None, end_date=None, initial_capital=1000.0, timeframes=None, risk_config=None):
    """
    Ejecuta el backtesting para un período específico
    
    Args:
        symbol: Par de trading (por defecto BTC/USDT)
        start_date: Fecha de inicio (datetime)
        end_date: Fecha de fin (datetime)
        initial_capital: Capital inicial para la simulación (por defecto 1000.0)
        timeframes: Lista de temporalidades a analizar (por defecto ['4h'])
        risk_config: Diccionario con configuración de gestión de riesgo (por defecto None)
    """
    # Valores por defecto
    if start_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    if timeframes is None:
        timeframes = ['4h']
    
    # Configuración de riesgo por defecto
    default_risk_config = {
        'stop_loss_pct': 0.02,      # 2% stop loss
        'take_profit_pct': 0.04,    # 4% take profit
        'trailing_stop_pct': 0.015,  # 1.5% trailing stop
        'max_position_size': 0.95    # 95% del capital
    }
    
    # Combinar configuración por defecto con la proporcionada
    if risk_config:
        default_risk_config.update(risk_config)
    risk_config = default_risk_config
    
    print(f"\n🔄 Iniciando backtesting para {symbol}")
    print(f"📅 Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
    print(f"💰 Capital inicial: ${initial_capital:,.2f}")
    print(f"⏰ Timeframes: {', '.join(timeframes)}")
    print("\n📊 Configuración de riesgo:")
    print(f"🛑 Stop Loss: {risk_config['stop_loss_pct']*100:.1f}%")
    print(f"✅ Take Profit: {risk_config['take_profit_pct']*100:.1f}%")
    print(f"📈 Trailing Stop: {risk_config['trailing_stop_pct']*100:.1f}%")
    print(f"💵 Tamaño máximo posición: {risk_config['max_position_size']*100:.1f}%")
    
    # Crear directorio para resultados si no existe
    results_dir = os.path.join(os.environ.get('TEMP', '/tmp'), "trading_bot_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Ejecutar backtesting
    engine = BacktestEngine(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        timeframes=timeframes,
        risk_config=risk_config
    )
    
    results = engine.run()
    
    # Asegurarse de que el símbolo esté en los resultados
    if 'symbol' not in results:
        results['symbol'] = symbol
    
    # Convertir todos los valores no serializables a strings
    def convert_to_serializable(obj):
        if isinstance(obj, (datetime, np.datetime64, pd.Timestamp)):
            return obj.isoformat()
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, pd.Index):
            return list(obj)
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if isinstance(obj, dict):
            return {str(k): convert_to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]
        if pd.isna(obj):
            return None
        return obj

    # Procesar resultados para asegurar que son serializables
    serializable_results = convert_to_serializable(results)
    
    # Asegurarse de que las fechas estén en formato ISO
    if 'start_date' in serializable_results:
        serializable_results['start_date'] = start_date.isoformat()
    if 'end_date' in serializable_results:
        serializable_results['end_date'] = end_date.isoformat()
    
    # Añadir configuración de riesgo a los resultados
    serializable_results['risk_config'] = risk_config
    
    # Añadir información adicional a los trades
    if 'trades' in serializable_results:
        for trade in serializable_results['trades']:
            # Calcular stop loss y take profit
            entry_price = trade['entry_price']
            if trade['type'] == 'long':
                trade['stop_loss_price'] = entry_price * (1 - risk_config['stop_loss_pct'])
                trade['take_profit_price'] = entry_price * (1 + risk_config['take_profit_pct'])
                trade['price_change_pct'] = ((trade['exit_price'] - trade['entry_price']) / trade['entry_price']) * 100
            else:  # short
                trade['stop_loss_price'] = entry_price * (1 + risk_config['stop_loss_pct'])
                trade['take_profit_price'] = entry_price * (1 - risk_config['take_profit_pct'])
                trade['price_change_pct'] = ((trade['entry_price'] - trade['exit_price']) / trade['entry_price']) * 100
            
            # Añadir timeframe
            trade['timeframe'] = timeframes[0]
            
            # Añadir información de MACD si está disponible en price_data
            if 'price_data' in results:
                entry_time = pd.to_datetime(trade['entry_time'])
                exit_time = pd.to_datetime(trade['exit_time'])
                
                if entry_time in results['price_data']:
                    entry_data = results['price_data'][entry_time]
                    trade['entry_macd'] = entry_data.get('MACD_12_26_9')
                    trade['entry_macd_signal'] = entry_data.get('MACDs_12_26_9')
                    trade['entry_macd_hist'] = entry_data.get('MACDh_12_26_9')
                
                if exit_time in results['price_data']:
                    exit_data = results['price_data'][exit_time]
                    trade['exit_macd'] = exit_data.get('MACD_12_26_9')
                    trade['exit_macd_signal'] = exit_data.get('MACDs_12_26_9')
                    trade['exit_macd_hist'] = exit_data.get('MACDh_12_26_9')
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    symbol_clean = symbol.replace('/', '_')
    timeframe_str = '_'.join(timeframes)  # Incluir temporalidad en el nombre del archivo
    results_file = os.path.join(results_dir, f"backtest_{symbol_clean}_{timeframe_str}_{timestamp}.json")
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=4)
    
    print(f"\n✅ Backtesting completado")
    print(f"📁 Resultados guardados en: {results_file}")
    
    return serializable_results

if __name__ == "__main__":
    run_backtest() 