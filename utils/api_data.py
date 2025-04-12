# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 22:46:40 2025

@author: OMEN Laptop
"""

# utils/api_data.py

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_price_data(symbol, timeframe='15m', start_date=None, end_date=None, limit=1000):
    """
    Obtiene datos históricos de precios
    
    Args:
        symbol: Par de trading (ej. 'BTC/USDT')
        timeframe: Temporalidad ('15m', '30m', '1h', '4h', '1d', '3d')
        start_date: Fecha de inicio (datetime o None)
        end_date: Fecha de fin (datetime o None)
        limit: Número máximo de velas a obtener
    """
    try:
        binance = ccxt.binance()
        
        # Asegurarse de que el símbolo esté en el formato correcto para Binance
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        # Convertir fechas a timestamp en milisegundos
        start_ts = int(start_date.timestamp() * 1000) if start_date else None
        end_ts = int(end_date.timestamp() * 1000) if end_date else None
        
        # Calcular el número de velas necesarias basado en el timeframe
        if start_ts and end_ts:
            # Mapeo de timeframes a minutos
            tf_map = {
                '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480,
                '12h': 720, '1d': 1440, '3d': 4320, '1w': 10080
            }
            
            # Obtener minutos del timeframe
            tf_minutes = tf_map.get(timeframe, 60)
            
            # Calcular número de velas necesarias
            time_diff = (end_ts - start_ts) / (1000 * 60)  # diferencia en minutos
            num_candles = int(time_diff / tf_minutes) + 2  # +2 para asegurar cobertura
            
            # Ajustar limit si es necesario
            limit = min(num_candles, 1000)  # Binance tiene un límite de 1000
        
        # Obtener datos históricos
        all_data = []
        current_ts = start_ts
        
        while True:
            try:
                # Hacer la petición
                ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, since=current_ts, limit=limit)
                
                if not ohlcv:
                    break
                    
                all_data.extend(ohlcv)
                
                # Verificar si hemos llegado al final
                last_ts = ohlcv[-1][0]
                if end_ts and last_ts >= end_ts:
                    break
                if len(ohlcv) < limit:
                    break
                    
                current_ts = last_ts + 1
                
            except Exception as e:
                print(f"Error al obtener datos para {symbol} en {timeframe}: {e}")
                break
        
        if not all_data:
            print(f"No se pudieron obtener datos para {symbol} en el período especificado")
            return pd.DataFrame()
        
        # Convertir a DataFrame
        df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
        
        # Filtrar por fechas y eliminar duplicados
        if start_date:
            df = df[df.index >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df.index <= pd.Timestamp(end_date)]
        
        # Eliminar duplicados y ordenar por índice
        df = df[~df.index.duplicated(keep='first')]
        df = df.sort_index()
        
        return df
        
    except Exception as e:
        print(f"Error en get_price_data: {e}")
        return pd.DataFrame()


def get_orderbook_summary(symbol, depth=10):
    binance = ccxt.binance()
    order_book = binance.fetch_order_book(symbol)

    # Precios bid y ask
    bid_price = order_book['bids'][0][0] if order_book['bids'] else None
    ask_price = order_book['asks'][0][0] if order_book['asks'] else None
    mid_price = (bid_price + ask_price) / 2 if bid_price and ask_price else None

    # Procesar las primeras N posiciones del orderbook
    bids = order_book['bids'][:depth]
    asks = order_book['asks'][:depth]

    # Crear DataFrames para mejor análisis
    bids_df = pd.DataFrame(bids, columns=['price', 'amount'])
    asks_df = pd.DataFrame(asks, columns=['price', 'amount'])

    # Calcular valores en USD
    bids_df['total_usd'] = bids_df['price'] * bids_df['amount']
    asks_df['total_usd'] = asks_df['price'] * asks_df['amount']

    # Calcular porcentajes del total
    bids_total = bids_df['amount'].sum()
    asks_total = asks_df['amount'].sum()
    
    bids_df['pct_of_total'] = (bids_df['amount'] / bids_total * 100)
    asks_df['pct_of_total'] = (asks_df['amount'] / asks_total * 100)

    # Calcular distribución acumulativa
    bids_df['cumulative_btc'] = bids_df['amount'].cumsum()
    asks_df['cumulative_btc'] = asks_df['amount'].cumsum()
    
    bids_df['cumulative_usd'] = bids_df['total_usd'].cumsum()
    asks_df['cumulative_usd'] = asks_df['total_usd'].cumsum()

    # Calcular estadísticas
    bid_stats = {
        'mean_size': bids_df['amount'].mean(),
        'median_size': bids_df['amount'].median(),
        'largest_order': bids_df['amount'].max(),
        'price_range': bids_df['price'].max() - bids_df['price'].min(),
        'concentration_top3': bids_df['amount'][:3].sum() / bids_total * 100
    }

    ask_stats = {
        'mean_size': asks_df['amount'].mean(),
        'median_size': asks_df['amount'].median(),
        'largest_order': asks_df['amount'].max(),
        'price_range': asks_df['price'].max() - asks_df['price'].min(),
        'concentration_top3': asks_df['amount'][:3].sum() / asks_total * 100
    }

    return {
        'bid_price': bid_price,
        'ask_price': ask_price,
        'mid_price': mid_price,
        'bids_total_btc': bids_total,
        'bids_total_usd': bids_df['total_usd'].sum(),
        'asks_total_btc': asks_total,
        'asks_total_usd': asks_df['total_usd'].sum(),
        'bids_detail': bids_df.to_dict('records'),
        'asks_detail': asks_df.to_dict('records'),
        'bid_stats': bid_stats,
        'ask_stats': ask_stats
    }

def print_orderbook(symbol):
    orderbook_summary = get_orderbook_summary(symbol)
    print("Orderbook Summary for", symbol)
    print("Bid Price:", orderbook_summary['bid_price'])
    print("Ask Price:", orderbook_summary['ask_price'])
    print("Mid Price:", orderbook_summary['mid_price'])
    print("Bids Total BTC:", orderbook_summary['bids_total_btc'])
    print("Bids Total USD:", orderbook_summary['bids_total_usd'])
    print("Asks Total BTC:", orderbook_summary['asks_total_btc'])
    print("Asks Total USD:", orderbook_summary['asks_total_usd'])
    print("Bid Stats:", orderbook_summary['bid_stats'])
    print("Ask Stats:", orderbook_summary['ask_stats'])
