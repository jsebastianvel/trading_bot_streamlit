# Trading Bot BTC

Bot de trading automatizado con interfaz web usando Streamlit. El bot utiliza el indicador MACD en múltiples temporalidades para tomar decisiones de trading.

## Características

- 📊 Análisis multi-timeframe (15m, 30m, 1h, 4h, 1d, 3d)
- 📈 Estrategia basada en MACD con pesos fibonacci
- 💰 Gestión de riesgo automática
- 🔔 Notificaciones por Telegram
- 🖥️ Interfaz web interactiva
- 📉 Backtesting incorporado

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/trading_bot_btc.git
cd trading_bot_btc
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
- Copia `.env.example` a `.env`
- Añade tus credenciales de Binance y Telegram

## Uso

1. Iniciar la interfaz web:
```bash
streamlit run app_streamlit.py
```

2. Acceder a través del navegador:
- La aplicación estará disponible en http://localhost:8501

## Configuración

- `config.py`: Configuración general del bot
- `.env`: Credenciales y configuración sensible
- `risk_management/`: Parámetros de gestión de riesgo

## Licencia

MIT License

## Autor

Tu Nombre 