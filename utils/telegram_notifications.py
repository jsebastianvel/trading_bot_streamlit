# -*- coding: utf-8 -*-
"""
Módulo para enviar notificaciones a través de Telegram
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        """Inicializa el notificador de Telegram"""
        load_dotenv()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
    
    def send_message(self, message):
        """Envía un mensaje a Telegram"""
        if not self.enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            requests.post(url, json=data)
        except Exception as e:
            print(f"Error al enviar mensaje a Telegram: {str(e)}")
    
    def send_trade_signal(self, timeframe, signal, strength, price):
        """Envía una señal de trading"""
        emoji = "🟢" if signal in ['buy', 'valley_buy'] else "🔴"
        message = (
            f"{emoji} <b>Señal de Trading</b>\n"
            f"Par: BTC/USDT\n"
            f"Timeframe: {timeframe}\n"
            f"Señal: {signal.upper()}\n"
            f"Fuerza: {strength:.2f}\n"
            f"Precio: ${price:,.2f}"
        )
        self.send_message(message)
    
    def send_error(self, error, context=""):
        """Envía un mensaje de error"""
        message = (
            f"⚠️ <b>Error en el Bot</b>\n"
            f"Contexto: {context}\n"
            f"Error: {str(error)}"
        )
        self.send_message(message)

    def send_trade_signal(self, timeframe, signal, strength, price, additional_info=None):
        """Envía una señal de trading formateada"""
        emoji_map = {
            'buy': '🟢',
            'sell': '🔴',
            'valley_buy': '💚',
            'top_sell': '❤️',
            'hold': '⚪'
        }
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = emoji_map.get(signal, '⚠️')
        
        message = f"""
<b>🤖 Señal de Trading</b>
━━━━━━━━━━━━━━━
⏰ <b>Fecha:</b> {current_time}
📊 <b>Timeframe:</b> {timeframe}
{emoji} <b>Señal:</b> {signal.upper()}
💪 <b>Fuerza:</b> {strength:.2f}
💵 <b>Precio:</b> ${price:.2f}
"""
        
        if additional_info:
            message += f"\nℹ️ <b>Info adicional:</b>\n{additional_info}"
            
        self.send_message(message)

    def send_summary(self, peso_buy, peso_sell, decision, orderbook=None):
        """Envía un resumen de la decisión final"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        emoji_decision = {
            "📈 LONG": "🚀",
            "📉 SHORT": "🔻",
            "⏳ WAIT": "⏳"
        }.get(decision, "❓")
        
        message = f"""
<b>📊 Resumen de Trading</b>
━━━━━━━━━━━━━━━
⏰ <b>Fecha:</b> {current_time}
📈 <b>Peso Compra:</b> {peso_buy:.2f}
📉 <b>Peso Venta:</b> {peso_sell:.2f}
{emoji_decision} <b>Decisión:</b> {decision}
"""
        
        if orderbook:
            message += f"""
📚 <b>Order Book:</b>
💰 Bid: ${orderbook['bid_price']:.2f}
💰 Ask: ${orderbook['ask_price']:.2f}
📊 Medio: ${orderbook['mid_price']:.2f}
"""
            
        self.send_message(message) 