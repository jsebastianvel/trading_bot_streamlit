# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 22:56:53 2025

@author: OMEN Laptop
"""

# config.py

# Temporalidades y pesos asignados usando secuencia Fibonacci
# 1, 2, 3, 5, 8, 13
TIMEFRAMES = {
    '15m': 1,    # Peso mínimo
    '30m': 2,    # Siguiente número Fibonacci
    '1h': 3,     # Siguiente número Fibonacci
    '4h': 5,     # Siguiente número Fibonacci
    '1d': 8,     # Siguiente número Fibonacci
    '3d': 13     # Siguiente número Fibonacci
}

# Pesos para cada tipo de señal
SIGNAL_WEIGHTS = {
    'buy': 1.0,
    'sell': 1.0,
    'valley_buy': 1.5,  # Señales más fuertes en valles
    'top_sell': 1.5     # Señales más fuertes en picos
}

SYMBOL = 'BTC/USDT'
SIGNAL_THRESHOLD = 2.0  # umbral mínimo para dar señal
