# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 23:32:44 2025

@author: OMEN Laptop
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas_ta as ta
import os
import numpy as np
from datetime import datetime

def plot_macd_chart(df, timeframe='', output_path=None):
    try:
        df = df.copy()
        macd = ta.macd(df['close'])
        df = df.join(macd)

        # Crear figura con subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
        
        # Gráfico de velas
        ax1.plot(df.index, df['close'], color='blue', label='Precio', linewidth=1)
        
        # Detectar señales
        df['valley_buy'] = (df['MACDh_12_26_9'] < -0.5) & (df['MACD_12_26_9'] > df['MACDs_12_26_9'])
        df['top_sell'] = (df['MACDh_12_26_9'] > 0.5) & (df['MACD_12_26_9'] < df['MACDs_12_26_9'])
        
        # Marcar señales en el gráfico de precios
        valley_buy_points = df[df['valley_buy']]
        top_sell_points = df[df['top_sell']]
        
        ax1.scatter(valley_buy_points.index, valley_buy_points['close'], 
                   color='green', marker='^', s=100, label='Valley Buy')
        ax1.scatter(top_sell_points.index, top_sell_points['close'], 
                   color='red', marker='v', s=100, label='Top Sell')
        
        # MACD
        ax2.plot(df.index, df['MACD_12_26_9'], color='blue', label='MACD', linewidth=1)
        ax2.plot(df.index, df['MACDs_12_26_9'], color='orange', label='Señal', linewidth=1)
        
        # Histograma MACD
        colors = ['green' if val >= 0 else 'red' for val in df['MACDh_12_26_9']]
        ax2.bar(df.index, df['MACDh_12_26_9'], color=colors, alpha=0.6, label='Histograma')
        
        # Configuración de ejes y etiquetas
        ax1.set_title(f'MACD - {timeframe}', fontsize=14)
        ax1.set_ylabel('Precio BTC', fontsize=12)
        ax2.set_ylabel('MACD', fontsize=12)
        ax2.set_xlabel('Fecha', fontsize=12)
        
        # Formato de fechas
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        
        # Rotar etiquetas de fecha
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Leyendas
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left')
        
        # Ajustar diseño
        plt.tight_layout()
        
        if output_path:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            try:
                # Guardar como PNG
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                print(f"✅ Gráfico guardado exitosamente en: {output_path}")
            except Exception as e:
                print(f"❌ Error al guardar la imagen: {str(e)}")
                # Intentar guardar como PDF si falla PNG
                pdf_path = output_path.replace('.png', '.pdf')
                plt.savefig(pdf_path, bbox_inches='tight')
                print(f"⚠️ Se guardó como PDF en su lugar: {pdf_path}")
        else:
            plt.show()
            
        # Cerrar la figura para liberar memoria
        plt.close(fig)
            
    except Exception as e:
        print(f"❌ Error al generar el gráfico MACD: {str(e)}")
        raise
