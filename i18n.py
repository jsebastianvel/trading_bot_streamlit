# -*- coding: utf-8 -*-
"""Static translation table for the Streamlit UI (Spanish/English).

Kept as a flat dict of dicts rather than a full i18n library since the
app is a single Streamlit script with a fixed, enumerable set of strings.
"""

TRANSLATIONS = {
    "es": {
        # Nav
        "nav_label": "Sección",
        "nav_backtesting": "📊 Backtesting",
        "nav_live_trading": "🤖 Trading en Vivo",
        "nav_ai_agent": "🧠 Agente IA",
        "lang_selector_label": "🌐 Idioma / Language",

        # Live trading
        "live_title": "🤖 Trading Bot - Trading en Vivo",
        "live_disclaimer": (
            "🚧 **Este módulo es una demo de portafolio.** El trading en vivo está "
            "desactivado a propósito: no hay credenciales de API activas en este "
            "despliegue, y la ejecución de órdenes (`_execute_trade`) es un stub que "
            "solo envía una notificación por Telegram, sin enviar órdenes reales al "
            "exchange. Este panel muestra la arquitectura y el flujo de control, no "
            "ejecuta operaciones reales con dinero real."
        ),
        "live_sidebar_header": "Configuración de Trading",
        "live_exchange_label": "Exchange",
        "live_pair_label": "Par de Trading",
        "live_no_credentials": "❌ No hay credenciales de API configuradas en este despliegue (esperado: es un proyecto de portafolio).",
        "live_start_bot": "🟢 Iniciar Bot",
        "live_bot_started": "✅ Bot iniciado exitosamente",
        "live_start_error": "❌ Error al iniciar el bot: {error}",
        "live_stop_bot": "🔴 Detener Bot",
        "live_bot_stopped": "✅ Bot detenido exitosamente",
        "live_stop_error": "❌ Error al detener el bot: {error}",
        "live_enable_trading": "✅ Activar Trading",
        "live_trading_enabled": "✅ Trading activado",
        "live_disable_trading": "⛔ Desactivar Trading",
        "live_trading_disabled": "⛔ Trading desactivado",
        "live_bot_status": "Estado del Bot",
        "live_status_active": "🟢 Activo",
        "live_status_stopped": "🔴 Detenido",
        "live_auto_trading": "Trading Automático",
        "live_auto_enabled": "✅ Activado",
        "live_auto_disabled": "⛔ Desactivado",
        "live_info_block": (
            "ℹ️ **Información del Trading en Vivo**\n"
            "- El bot analiza el mercado cada minuto\n"
            "- Las señales se generan según la estrategia MACD multi-timeframe\n"
            "- El trading automático ejecutará operaciones solo cuando esté activado\n"
            "- Todas las operaciones se notifican por Telegram"
        ),
        "live_warning_block": (
            "⚠️ **Advertencias**\n"
            "- Asegúrate de tener suficiente saldo en tu cuenta\n"
            "- El bot opera con un máximo del 5% del capital por operación\n"
            "- Las operaciones automáticas pueden generar pérdidas\n"
            "- Monitorea regularmente el rendimiento del bot"
        ),

        # AI agent
        "agent_title": "Agente IA - Análisis con RAG + LLM",
        "agent_description": (
            "Este agente combina la señal técnica MACD multi-temporalidad con noticias "
            "recientes de cripto (recuperadas vía RAG) y usa un LLM (Gemini) para "
            "generar una explicación en lenguaje natural y una recomendación final."
        ),
        "agent_generate_button": "Generar análisis del agente",
        "agent_spinner": "Consultando precios, noticias y generando análisis...",
        "agent_error": "Error generando el análisis: {error}",
        "agent_recommendation": "Recomendación",
        "agent_buy_weight": "Peso Compra",
        "agent_sell_weight": "Peso Venta",
        "agent_brief_subheader": "Market Brief (generado por IA)",
        "agent_signals_expander": "Señales técnicas por temporalidad",
        "agent_news_expander": "Noticias usadas para el contexto ({count})",

        # Backtesting
        "bt_title": "🤖 Trading Bot - Análisis de Backtesting",
        "bt_sidebar_header": "Configuración de Backtesting",
        "bt_pair_label": "Par de Trading",
        "bt_start_date": "Fecha Inicial",
        "bt_end_date": "Fecha Final",
        "bt_date_order_error": "❌ La fecha inicial debe ser anterior a la fecha final",
        "bt_timeframe_label": "Temporalidad a analizar",
        "bt_timeframe_help": "Selecciona la temporalidad para el backtesting",
        "bt_capital_label": "Capital Inicial ($)",
        "bt_run_button": "Ejecutar Backtesting",
        "bt_timeframe_required": "❌ Debes seleccionar una temporalidad.",
        "bt_running_spinner": "Ejecutando backtesting...",
        "bt_completed": "✅ Backtesting completado exitosamente!",
        "bt_configure_hint": "👈 Configura los parámetros en el panel lateral y presiona 'Ejecutar Backtesting' para comenzar.",
        "bt_no_results": "No hay resultados de backtesting disponibles.",
        "bt_empty_file": "El archivo de resultados está vacío.",
        "bt_timestamp_parse_warning": "Error al parsear timestamp {timestamp}: {error}",
        "bt_details_block": (
            "**Detalles del Backtest:**\n"
            "- Par: {symbol}\n"
            "- Período: {start} a {end}\n"
            "- Timeframes: {timeframes}"
        ),
        "bt_metric_total_return": "Retorno Total",
        "bt_metric_win_rate": "Win Rate",
        "bt_metric_profit_factor": "Factor de Beneficio",
        "bt_metric_max_drawdown": "Máximo Drawdown",
        "bt_capital_evolution_subheader": "📈 Evolución del Capital",
        "bt_balance_timestamp_warning": "Error al procesar timestamp del balance: {error}",
        "bt_initial_capital_annotation": "Capital Inicial",
        "bt_drawdown_timestamp_warning": "Error al procesar timestamp del drawdown: {error}",
        "bt_drawdown_process_error": "Error al procesar drawdown: {error}",
        "bt_capital_chart_title": "Evolución del Capital y Drawdown",
        "bt_date_axis": "Fecha",
        "bt_capital_axis": "Capital ($)",
        "bt_drawdown_axis": "Drawdown (%)",
        "bt_capital_trace_name": "Capital",
        "bt_drawdown_trace_name": "Drawdown",
        "bt_no_valid_capital_data": "No hay datos válidos de evolución del capital",
        "bt_no_capital_data": "No hay datos de evolución del capital disponibles",
        "bt_technical_analysis_subheader": "📈 Análisis Técnico",
        "bt_price_trace_name": "Precio",
        "bt_technical_chart_title": "Análisis Técnico",
        "bt_price_axis": "Precio",
        "bt_no_valid_technical_data": "No hay datos válidos para el gráfico de análisis técnico",
        "bt_price_data_error": "Error al procesar price_data: {error}",
        "bt_trades_subheader": "📊 Registro de Operaciones",
        "bt_no_trades": "El backtesting no generó ninguna operación en el período seleccionado.",
        "bt_stats_subheader": "📊 Estadísticas Detalladas",
        "bt_trading_metrics_header": "**Métricas de Trading**",
        "bt_total_trades": "- Número total de trades: {value}",
        "bt_winning_trades": "- Trades ganadores: {value}",
        "bt_losing_trades": "- Trades perdedores: {value}",
        "bt_win_loss_ratio": "- Ratio ganador/perdedor: {value:.2f}%",
        "bt_capital_metrics_header": "**Métricas de Capital**",
        "bt_initial_capital_line": "- Capital inicial: ${value:,.2f}",
        "bt_final_capital_line": "- Capital final: ${value:,.2f}",
        "bt_total_return_line": "- Retorno total: {value:.2f}%",
        "bt_max_drawdown_line": "- Máximo drawdown: {value:.2f}%",
        "bt_load_error": "Error al cargar los resultados: {error}",
    },
    "en": {
        # Nav
        "nav_label": "Section",
        "nav_backtesting": "📊 Backtesting",
        "nav_live_trading": "🤖 Live Trading",
        "nav_ai_agent": "🧠 AI Agent",
        "lang_selector_label": "🌐 Idioma / Language",

        # Live trading
        "live_title": "🤖 Trading Bot - Live Trading",
        "live_disclaimer": (
            "🚧 **This module is a portfolio demo.** Live trading is intentionally "
            "disabled: no API credentials are active in this deployment, and order "
            "execution (`_execute_trade`) is a stub that only sends a Telegram "
            "notification — it never places real orders on the exchange. This panel "
            "showcases the architecture and control flow, not real trade execution "
            "with real money."
        ),
        "live_sidebar_header": "Trading Configuration",
        "live_exchange_label": "Exchange",
        "live_pair_label": "Trading Pair",
        "live_no_credentials": "❌ No API credentials configured in this deployment (expected: this is a portfolio project).",
        "live_start_bot": "🟢 Start Bot",
        "live_bot_started": "✅ Bot started successfully",
        "live_start_error": "❌ Error starting the bot: {error}",
        "live_stop_bot": "🔴 Stop Bot",
        "live_bot_stopped": "✅ Bot stopped successfully",
        "live_stop_error": "❌ Error stopping the bot: {error}",
        "live_enable_trading": "✅ Enable Trading",
        "live_trading_enabled": "✅ Trading enabled",
        "live_disable_trading": "⛔ Disable Trading",
        "live_trading_disabled": "⛔ Trading disabled",
        "live_bot_status": "Bot Status",
        "live_status_active": "🟢 Active",
        "live_status_stopped": "🔴 Stopped",
        "live_auto_trading": "Automatic Trading",
        "live_auto_enabled": "✅ Enabled",
        "live_auto_disabled": "⛔ Disabled",
        "live_info_block": (
            "ℹ️ **Live Trading Information**\n"
            "- The bot analyzes the market every minute\n"
            "- Signals are generated using the multi-timeframe MACD strategy\n"
            "- Automatic trading will only execute trades when enabled\n"
            "- All operations are notified via Telegram"
        ),
        "live_warning_block": (
            "⚠️ **Warnings**\n"
            "- Make sure you have sufficient balance in your account\n"
            "- The bot operates with a maximum of 5% of capital per trade\n"
            "- Automatic trades can generate losses\n"
            "- Regularly monitor the bot's performance"
        ),

        # AI agent
        "agent_title": "AI Agent - RAG + LLM Analysis",
        "agent_description": (
            "This agent combines the multi-timeframe MACD technical signal with "
            "recent crypto news (retrieved via RAG) and uses an LLM (Gemini) to "
            "generate a natural-language explanation and final recommendation."
        ),
        "agent_generate_button": "Generate agent analysis",
        "agent_spinner": "Fetching prices, news, and generating analysis...",
        "agent_error": "Error generating the analysis: {error}",
        "agent_recommendation": "Recommendation",
        "agent_buy_weight": "Buy Weight",
        "agent_sell_weight": "Sell Weight",
        "agent_brief_subheader": "Market Brief (AI-generated)",
        "agent_signals_expander": "Technical signals by timeframe",
        "agent_news_expander": "News used for context ({count})",

        # Backtesting
        "bt_title": "🤖 Trading Bot - Backtesting Analysis",
        "bt_sidebar_header": "Backtesting Configuration",
        "bt_pair_label": "Trading Pair",
        "bt_start_date": "Start Date",
        "bt_end_date": "End Date",
        "bt_date_order_error": "❌ Start date must be before end date",
        "bt_timeframe_label": "Timeframe to analyze",
        "bt_timeframe_help": "Select the timeframe for the backtest",
        "bt_capital_label": "Initial Capital ($)",
        "bt_run_button": "Run Backtest",
        "bt_timeframe_required": "❌ You must select a timeframe.",
        "bt_running_spinner": "Running backtest...",
        "bt_completed": "✅ Backtest completed successfully!",
        "bt_configure_hint": "👈 Configure the parameters in the sidebar and press 'Run Backtest' to begin.",
        "bt_no_results": "No backtest results available.",
        "bt_empty_file": "The results file is empty.",
        "bt_timestamp_parse_warning": "Error parsing timestamp {timestamp}: {error}",
        "bt_details_block": (
            "**Backtest Details:**\n"
            "- Pair: {symbol}\n"
            "- Period: {start} to {end}\n"
            "- Timeframes: {timeframes}"
        ),
        "bt_metric_total_return": "Total Return",
        "bt_metric_win_rate": "Win Rate",
        "bt_metric_profit_factor": "Profit Factor",
        "bt_metric_max_drawdown": "Max Drawdown",
        "bt_capital_evolution_subheader": "📈 Capital Evolution",
        "bt_balance_timestamp_warning": "Error processing balance timestamp: {error}",
        "bt_initial_capital_annotation": "Initial Capital",
        "bt_drawdown_timestamp_warning": "Error processing drawdown timestamp: {error}",
        "bt_drawdown_process_error": "Error processing drawdown: {error}",
        "bt_capital_chart_title": "Capital Evolution and Drawdown",
        "bt_date_axis": "Date",
        "bt_capital_axis": "Capital ($)",
        "bt_drawdown_axis": "Drawdown (%)",
        "bt_capital_trace_name": "Capital",
        "bt_drawdown_trace_name": "Drawdown",
        "bt_no_valid_capital_data": "No valid capital evolution data",
        "bt_no_capital_data": "No capital evolution data available",
        "bt_technical_analysis_subheader": "📈 Technical Analysis",
        "bt_price_trace_name": "Price",
        "bt_technical_chart_title": "Technical Analysis",
        "bt_price_axis": "Price",
        "bt_no_valid_technical_data": "No valid data for the technical analysis chart",
        "bt_price_data_error": "Error processing price_data: {error}",
        "bt_trades_subheader": "📊 Trade Log",
        "bt_no_trades": "The backtest did not generate any trades in the selected period.",
        "bt_stats_subheader": "📊 Detailed Statistics",
        "bt_trading_metrics_header": "**Trading Metrics**",
        "bt_total_trades": "- Total number of trades: {value}",
        "bt_winning_trades": "- Winning trades: {value}",
        "bt_losing_trades": "- Losing trades: {value}",
        "bt_win_loss_ratio": "- Win/loss ratio: {value:.2f}%",
        "bt_capital_metrics_header": "**Capital Metrics**",
        "bt_initial_capital_line": "- Initial capital: ${value:,.2f}",
        "bt_final_capital_line": "- Final capital: ${value:,.2f}",
        "bt_total_return_line": "- Total return: {value:.2f}%",
        "bt_max_drawdown_line": "- Max drawdown: {value:.2f}%",
        "bt_load_error": "Error loading results: {error}",
    },
}


def t(key, lang="es", **kwargs):
    """Look up `key` in the given language, falling back to Spanish, then the
    key itself if missing. Formats with `kwargs` when provided."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key)
    if text is None:
        text = TRANSLATIONS["es"].get(key, key)
    return text.format(**kwargs) if kwargs else text
