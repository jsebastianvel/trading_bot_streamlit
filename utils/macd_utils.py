# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 23:58:34 2025

@author: OMEN Laptop
"""

import pandas_ta as ta

def interpretar_macd(df, tf):
    macd = df.ta.macd(close='close', fast=12, slow=26, signal=9)
    df['MACD_12_26_9'] = macd['MACD_12_26_9']
    df['MACDs_12_26_9'] = macd['MACDs_12_26_9']
    df['MACDh_12_26_9'] = macd['MACDh_12_26_9']
    
    latest = df.iloc[-1]
    
    hist = latest['MACDh_12_26_9']
    macd_line = latest['MACD_12_26_9']
    signal = latest['MACDs_12_26_9']
    
    if macd_line > signal:
        raw_signal = 'BUY'
    elif macd_line < signal:
        raw_signal = 'SELL'
    else:
        raw_signal = 'HOLD'

    fuerza = abs(hist)
    if fuerza < 50:
        fuerza_txt = 'Leve'
    elif fuerza < 150:
        fuerza_txt = 'Moderada'
    elif fuerza < 300:
        fuerza_txt = 'Fuerte'
    else:
        fuerza_txt = 'Muy fuerte'

    sentido = '📈' if hist >= 0 else '📉'
    
    print(f"⏱ Timeframe: {tf} → {sentido} Señal: {raw_signal} | Fuerza: {fuerza_txt} (MACDh = {hist:.1f})")
