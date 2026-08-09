# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 22:47:08 2025

@author: OMEN Laptop
"""

# strategy/macd_strategy.py

import pandas as pd
import pandas_ta as ta
import numpy as np

def calculate_threshold(timeframe):
    """Calcula umbrales dinámicos basados en la temporalidad"""
    # Mapeo de timeframes a factores multiplicadores
    tf_factors = {
        '15m': 0.5,  # Más restrictivo para timeframes cortos
        '30m': 0.6,
        '1h': 0.7,
        '4h': 0.8,
        '1d': 0.9,
        '3d': 1.0   # Menos restrictivo para timeframes largos
    }
    base_threshold = 0.8  # Aumentado de 0.5 a 0.8
    return base_threshold * tf_factors.get(timeframe, 0.7)

def check_macd_signal(df, timeframe=''):
    """
    Calcula señales MACD para un DataFrame dado
    
    Args:
        df: DataFrame con datos OHLCV
        timeframe: Temporalidad de los datos
    
    Returns:
        tuple: (señal, fuerza) donde señal puede ser 'buy', 'sell', 'valley_buy', 'top_sell' o 'hold'
    """
    # Verificar que hay suficientes datos
    if len(df) < 35:  # Necesitamos al menos 26 períodos para MACD + algunos más para señales
        print(f"\n⚠️ Insuficientes datos para calcular MACD ({len(df)} períodos)")
        return 'hold', 0.0
    
    try:
        # Calcular MACD usando pandas_ta
        macd = df.ta.macd(close='close', fast=12, slow=26, signal=9)
        df['MACD_12_26_9'] = macd['MACD_12_26_9']
        df['MACDs_12_26_9'] = macd['MACDs_12_26_9']
        df['MACDh_12_26_9'] = macd['MACDh_12_26_9']
        
        # Obtener últimos valores
        last_macd = df['MACD_12_26_9'].iloc[-1]
        last_signal = df['MACDs_12_26_9'].iloc[-1]
        last_hist = df['MACDh_12_26_9'].iloc[-1]
        prev_hist = df['MACDh_12_26_9'].iloc[-2] if len(df) > 1 else 0
        current_price = df['close'].iloc[-1]
        
        # Calcular umbral relativo al precio (usando porcentajes)
        price_threshold = current_price * 0.001  # 0.1% del precio actual
        
        # Calcular volatilidad usando ATR
        atr = df.ta.atr(high='high', low='low', close='close', length=14)
        df['TR'] = atr
        atr_value = df['TR'].iloc[-1]
        volatility = atr_value / price_threshold  # Normalizar la volatilidad respecto al umbral
        
        # Calcular umbral dinámico basado en la volatilidad y timeframe
        base_threshold = calculate_threshold(timeframe)
        threshold = price_threshold * base_threshold * (1 + volatility)
        
        # Calcular tendencia usando EMA
        ema_20 = df.ta.ema(close='close', length=20).iloc[-1]
        ema_50 = df.ta.ema(close='close', length=50).iloc[-1]
        trend = 'up' if ema_20 > ema_50 else 'down'
        
        # Imprimir valores para debugging
        print(f"\n🕒 Timeframe: {timeframe}")
        print(f"📊 Últimos valores MACD:")
        print(f"Precio: ${current_price:,.2f}")
        print(f"Umbral: ${threshold:,.2f}")
        print(f"MACD: {last_macd:,.2f}")
        print(f"Señal: {last_signal:,.2f}")
        print(f"Histograma: {last_hist:,.2f}")
        print(f"Volatilidad: {volatility:.4f}")
        
        # Calcular fuerza de la señal
        signal_strength = abs(last_hist) / threshold  # Normalizar respecto al umbral dinámico
        signal_strength = min(signal_strength * (1 + volatility), 1.0)  # Normalizar entre 0 y 1
        
        # Generar señales con confirmación de tendencia
        if last_hist > 0 and prev_hist <= 0:  # Cruce alcista
            if abs(last_hist) > threshold and trend == 'up':
                return 'valley_buy', signal_strength
            elif trend == 'up':
                return 'buy', signal_strength
        elif last_hist < 0 and prev_hist >= 0:  # Cruce bajista
            if abs(last_hist) > threshold and trend == 'down':
                return 'top_sell', signal_strength
            elif trend == 'down':
                return 'sell', signal_strength
        
        return 'hold', 0.0
        
    except Exception as e:
        print(f"\n❌ Error al calcular señales MACD: {str(e)}")
        return 'hold', 0.0

