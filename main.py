# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 22:45:04 2025

@author: OMEN Laptop
"""

from config import TIMEFRAMES, SYMBOL, SIGNAL_THRESHOLD
from utils.api_data import get_price_data, get_orderbook_summary
from strategy.macd_strategy import check_macd_signal
from visual.macd_plot import plot_macd_chart
from macd_utils import interpretar_macd
from utils.telegram_notifications import TelegramNotifier
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar notificador de Telegram
notifier = TelegramNotifier()

# Pesos base por tipo de señal
SIGNAL_WEIGHTS = {
    'buy': 1.0,
    'sell': 1.0,
    'valley_buy': 1.5,
    'top_sell': 1.5,
    'hold': 0.0
}

def evaluate_multi_timeframe(symbol):
    peso_buy = 0
    peso_sell = 0
    resumen = []

    # Carpeta para guardar gráficas
    output_dir = r"C:/Users/OMEN Laptop/Documents/proyectosdeprogramacion/trading_bot_btc/charts"
    os.makedirs(output_dir, exist_ok=True)

    try:
        for tf, peso_tf in TIMEFRAMES.items():
            try:
                df = get_price_data(symbol, tf)
                interpretar_macd(df, tf)  # Interpretación del MACD
                signal, strength = check_macd_signal(df, timeframe=tf)  # Ahora recibimos también la fuerza

                # El peso final es el producto de:
                # - Peso base del tipo de señal
                # - Peso de la temporalidad
                # - Fuerza de la señal
                peso_signal = SIGNAL_WEIGHTS.get(signal, 0) * strength

                if signal in ['buy', 'valley_buy']:
                    peso_buy += peso_tf * peso_signal
                elif signal in ['sell', 'top_sell']:
                    peso_sell += peso_tf * peso_signal

                resumen.append(f"{tf}: {signal} (fuerza: {strength:.2f}, peso final: {peso_tf * peso_signal:.2f})")
                
                # Enviar notificación de señal individual
                if signal != 'hold':
                    notifier.send_trade_signal(
                        timeframe=tf,
                        signal=signal,
                        strength=strength,
                        price=df['close'].iloc[-1],
                        additional_info=f"Peso de la señal: {peso_tf * peso_signal:.2f}"
                    )
                
                # Guardar imagen del gráfico
                output_file = os.path.join(output_dir, f"macd_{tf}.png")
                plot_macd_chart(df, timeframe=tf, output_path=output_file)

            except Exception as e:
                error_msg = f"{tf}: ERROR - {e}"
                resumen.append(error_msg)
                notifier.send_error(str(e), f"Error en timeframe {tf}")

        # Mostrar resultados
        print("\n=== Señales por temporalidad ===")
        for r in resumen:
            print(r)

        print(f"\nTOTAL Peso BUY: {peso_buy:.2f} | SELL: {peso_sell:.2f}")

        # Decisión final con umbrales ajustados
        if peso_buy - peso_sell >= SIGNAL_THRESHOLD:
            decision = "📈 LONG"
        elif peso_sell - peso_buy >= SIGNAL_THRESHOLD:
            decision = "📉 SHORT"
        else:
            decision = "⏳ WAIT"

        print(f"\n📊 DECISIÓN FINAL: {decision}")
        
        # Obtener información del orderbook para el resumen
        book = get_orderbook_summary(symbol)
        
        # Enviar resumen final
        notifier.send_summary(
            peso_buy=peso_buy,
            peso_sell=peso_sell,
            decision=decision,
            orderbook=book
        )
        
        return decision

    except Exception as e:
        error_msg = f"Error general en la evaluación: {str(e)}"
        print(f"\n❌ {error_msg}")
        notifier.send_error(error_msg, "Error en evaluate_multi_timeframe")
        raise


def print_orderbook(symbol):
    try:
        book = get_orderbook_summary(symbol)

        print("\n=== Order Book (Profundidad Top 10) ===")
        print(f"💰 Bid Price:     ${book['bid_price']:.2f}")
        print(f"💰 Ask Price:     ${book['ask_price']:.2f}")
        print(f"📌 Precio Medio:  ${book['mid_price']:.2f}")

        print("\n📊 ÓRDENES DE COMPRA (BIDS)")
        print("═" * 100)
        print(f"{'Precio ($)':^15} {'Cantidad (BTC)':^15} {'Total (USD)':^15} {'% del Total':^15} {'BTC Acum.':^15} {'USD Acum.':^15}")
        print("─" * 100)
        for bid in book['bids_detail']:
            print(f"{bid['price']:^15.2f} {bid['amount']:^15.4f} {bid['total_usd']:^15.2f} {bid['pct_of_total']:^15.2f} {bid['cumulative_btc']:^15.4f} {bid['cumulative_usd']:^15.2f}")

        print("\n📊 ÓRDENES DE VENTA (ASKS)")
        print("═" * 100)
        print(f"{'Precio ($)':^15} {'Cantidad (BTC)':^15} {'Total (USD)':^15} {'% del Total':^15} {'BTC Acum.':^15} {'USD Acum.':^15}")
        print("─" * 100)
        for ask in book['asks_detail']:
            print(f"{ask['price']:^15.2f} {ask['amount']:^15.4f} {ask['total_usd']:^15.2f} {ask['pct_of_total']:^15.2f} {ask['cumulative_btc']:^15.4f} {ask['cumulative_usd']:^15.2f}")

        print("\n📈 ESTADÍSTICAS DE COMPRAS (BIDS)")
        print("═" * 50)
        print(f"📊 Tamaño Medio:     {book['bid_stats']['mean_size']:.4f} BTC")
        print(f"📊 Tamaño Mediano:   {book['bid_stats']['median_size']:.4f} BTC")
        print(f"📊 Orden Más Grande: {book['bid_stats']['largest_order']:.4f} BTC")
        print(f"📊 Rango de Precios: ${book['bid_stats']['price_range']:.2f}")
        print(f"📊 Concentración Top 3: {book['bid_stats']['concentration_top3']:.2f}%")

        print("\n📉 ESTADÍSTICAS DE VENTAS (ASKS)")
        print("═" * 50)
        print(f"📊 Tamaño Medio:     {book['ask_stats']['mean_size']:.4f} BTC")
        print(f"📊 Tamaño Mediano:   {book['ask_stats']['median_size']:.4f} BTC")
        print(f"📊 Orden Más Grande: {book['ask_stats']['largest_order']:.4f} BTC")
        print(f"📊 Rango de Precios: ${book['ask_stats']['price_range']:.2f}")
        print(f"📊 Concentración Top 3: {book['ask_stats']['concentration_top3']:.2f}%")

        print("\n💰 TOTALES")
        print("═" * 50)
        print(f"📥 Bids Total: {book['bids_total_btc']:.4f} BTC = ${book['bids_total_usd']:.2f}")
        print(f"📤 Asks Total: {book['asks_total_btc']:.4f} BTC = ${book['asks_total_usd']:.2f}")
        
        return book
    except Exception as e:
        error_msg = f"Error al obtener orderbook: {str(e)}"
        print(f"\n❌ {error_msg}")
        notifier.send_error(error_msg)
        return None


if __name__ == "__main__":
    evaluate_multi_timeframe(SYMBOL)
    print_orderbook(SYMBOL)


