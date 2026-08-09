# -*- coding: utf-8 -*-
"""
Aplicación Streamlit para visualizar resultados de backtesting
"""

import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import glob
from datetime import datetime, timedelta
from run_backtest import run_backtest
from config import TIMEFRAMES
from trading.live_trader import LiveTrader
import ccxt
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar ambiente
is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

# Configuración de secretos en producción
if is_production:
    # Usar secretos de Streamlit en producción
    BINANCE_API_KEY = st.secrets["BINANCE_API_KEY"]
    BINANCE_API_SECRET = st.secrets["BINANCE_API_SECRET"]
    TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID")
else:
    # Usar variables de entorno en desarrollo
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuración de la página
st.set_page_config(
    page_title="Trading Bot - Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Selector de seccion (radio en vez de st.tabs porque necesitamos saber
# desde Python cual esta activa, para mostrar el sidebar correcto)
NAV_OPTIONS = ["📊 Backtesting", "🤖 Trading en Vivo", "🧠 Agente IA"]
selected_view = st.radio("Seccion", NAV_OPTIONS, horizontal=True, label_visibility="collapsed")
st.markdown("---")

# Inicializar el estado de la sesión para el trader en vivo si no existe
if 'live_trader' not in st.session_state:
    st.session_state.live_trader = None
    st.session_state.is_trading = False

if selected_view == "🤖 Trading en Vivo":
    st.title("🤖 Trading Bot - Trading en Vivo")
    
    # Sección de configuración
    with st.sidebar:
        st.header("Configuración de Trading")
    
        # Selección de exchange y par
        exchange = st.selectbox(
            "Exchange",
            ["Binance"],
            index=0
        )
    
        symbol = st.selectbox(
            "Par de Trading",
            ["BTC/USDT", "ETH/USDT", "TAO/USDT"],
            index=0
        )
    
        # Configuración de API (oculta)
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_API_SECRET', '')
    
        if not api_key or not api_secret:
            st.error("❌ No se encontraron las credenciales de API en las variables de entorno")
    
    if api_key and api_secret:
        # Estado del bot y controles
        col1, col2, col3 = st.columns(3)
    
        with col1:
            if st.session_state.live_trader is None:
                if st.button("🟢 Iniciar Bot"):
                    try:
                        # Inicializar exchange
                        exchange_config = {
                            'apiKey': api_key,
                            'secret': api_secret,
                            'enableRateLimit': True
                        }
                        exchange_client = ccxt.binance(exchange_config)
                    
                        # Crear instancia del trader
                        st.session_state.live_trader = LiveTrader(
                            exchange_client=exchange_client,
                            symbol=symbol
                        )
                        st.session_state.live_trader.start()
                        st.success("✅ Bot iniciado exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al iniciar el bot: {str(e)}")
            else:
                if st.button("🔴 Detener Bot"):
                    try:
                        st.session_state.live_trader.stop()
                        st.session_state.live_trader = None
                        st.session_state.is_trading = False
                        st.success("✅ Bot detenido exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al detener el bot: {str(e)}")
    
        with col2:
            if st.session_state.live_trader is not None:
                if not st.session_state.is_trading:
                    if st.button("✅ Activar Trading"):
                        st.session_state.live_trader.enable_trading()
                        st.session_state.is_trading = True
                        st.success("✅ Trading activado")
                        st.rerun()
                else:
                    if st.button("⛔ Desactivar Trading"):
                        st.session_state.live_trader.disable_trading()
                        st.session_state.is_trading = False
                        st.success("⛔ Trading desactivado")
                        st.rerun()
    
        with col3:
            # Estado actual
            if st.session_state.live_trader is not None:
                st.metric(
                    "Estado del Bot",
                    "🟢 Activo" if st.session_state.live_trader.is_running else "🔴 Detenido"
                )
                st.metric(
                    "Trading Automático",
                    "✅ Activado" if st.session_state.is_trading else "⛔ Desactivado"
                )
            else:
                st.metric("Estado del Bot", "🔴 Detenido")
                st.metric("Trading Automático", "⛔ Desactivado")
    
        # Información y advertencias
        st.info("""
        ℹ️ **Información del Trading en Vivo**
        - El bot analiza el mercado cada minuto
        - Las señales se generan según la estrategia MACD multi-timeframe
        - El trading automático ejecutará operaciones solo cuando esté activado
        - Todas las operaciones se notifican por Telegram
        """)
    
        st.warning("""
        ⚠️ **Advertencias**
        - Asegúrate de tener suficiente saldo en tu cuenta
        - El bot opera con un máximo del 5% del capital por operación
        - Las operaciones automáticas pueden generar pérdidas
        - Monitorea regularmente el rendimiento del bot
        """)



if selected_view == "🧠 Agente IA":
    st.title("Agente IA - Analisis con RAG + LLM")
    st.markdown(
        """
        Este agente combina la señal técnica MACD multi-temporalidad con noticias
        recientes de cripto (recuperadas vía RAG) y usa un LLM (Gemini) para
        generar una explicación en lenguaje natural y una recomendación final.
        """
    )

    if st.button("Generar análisis del agente", type="primary"):
        with st.spinner("Consultando precios, noticias y generando análisis..."):
            try:
                from genai.agent import generate_market_brief
                st.session_state.agent_brief = generate_market_brief()
                st.session_state.agent_error = None
            except Exception as e:
                st.session_state.agent_error = str(e)

    if st.session_state.get("agent_error"):
        st.error(f"Error generando el análisis: {st.session_state.agent_error}")

    if st.session_state.get("agent_brief"):
        brief = st.session_state.agent_brief

        decision_icon = {"LONG": "🟢", "SHORT": "🔴", "WAIT": "🟡"}.get(brief["decision"], "")
        st.metric("Recomendación", f"{decision_icon} {brief['decision']}")

        col1, col2 = st.columns(2)
        col1.metric("Peso Compra", f"{brief['peso_buy']:.2f}")
        col2.metric("Peso Venta", f"{brief['peso_sell']:.2f}")

        st.subheader("Market Brief (generado por IA)")
        st.write(brief["explanation"])

        with st.expander("Señales técnicas por temporalidad"):
            for s in brief["signals"]:
                st.text(s)

        with st.expander(f"Noticias usadas para el contexto ({len(brief['news'])})"):
            for n in brief["news"]:
                st.markdown(f"- **[{n['source']}]** [{n['title']}]({n['link']})")

if selected_view == "📊 Backtesting":
    st.title("🤖 Trading Bot - Análisis de Backtesting")

    # Sidebar para configuración
    with st.sidebar:
        st.header("Configuración de Backtesting")

        # Parámetros de backtesting
        symbol = st.selectbox(
            "Par de Trading",
            ["BTC/USDT", "ETH/USDT", "TAO/USDT", "XRP/USDT", "SOL/USDT"],
            index=0
        )

        # Selección de fechas
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Fecha Inicial",
                value=datetime.now().date() - timedelta(days=365),  # Un año por defecto
                max_value=datetime.now().date()
            )

        with col2:
            end_date = st.date_input(
                "Fecha Final",
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )

        # Validar que la fecha inicial sea anterior a la final
        if start_date >= end_date:
            st.error("❌ La fecha inicial debe ser anterior a la fecha final")
            st.stop()

        # Selección de temporalidad (una sola opción)
        selected_timeframe = st.selectbox(
            "Temporalidad a analizar",
            list(TIMEFRAMES.keys()),
            index=None,
            help="Selecciona la temporalidad para el backtesting"
        )

        initial_capital = st.number_input(
            "Capital Inicial ($)",
            min_value=100,
            max_value=100000,
            value=1000,
            step=100
        )

        # Botón para ejecutar backtesting
        run_backtest_button = st.button("Ejecutar Backtesting")

    if run_backtest_button:
        if not selected_timeframe:
            st.error("❌ Debes seleccionar una temporalidad.")
        else:
            with st.spinner("Ejecutando backtesting..."):
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                results = run_backtest(
                    symbol=symbol,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    initial_capital=initial_capital,
                    timeframes=[selected_timeframe]  # Lista con un solo elemento
                )
                st.success("✅ Backtesting completado exitosamente!")
                st.session_state.last_run = datetime.now()
                st.session_state.show_results = True
                st.rerun()

    # Solo mostrar resultados si se ha ejecutado un backtesting
    if not hasattr(st.session_state, 'show_results'):
        st.session_state.show_results = False

    if not st.session_state.show_results:
        st.info("👈 Configura los parámetros en el panel lateral y presiona 'Ejecutar Backtesting' para comenzar.")
        st.stop()

    # Cargar resultados de backtesting
    results_dir = os.path.join(os.environ.get('TEMP', '/tmp'), "trading_bot_results")

    # Buscar archivos en el directorio de resultados
    result_files = []
    if os.path.exists(results_dir):
        result_files.extend(glob.glob(os.path.join(results_dir, "*.json")))

    if not result_files:
        st.warning("No hay resultados de backtesting disponibles.")
        st.stop()

    # Ordenar archivos por fecha de modificación (más reciente primero)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Usar el archivo más reciente automáticamente
    selected_file = result_files[0]
        
    try:
        with open(selected_file, 'r') as f:
            results = json.load(f)
            
        if not results:
            st.error("El archivo de resultados está vacío.")
            st.stop()

        # Convertir fechas y timestamps
        def safe_parse_timestamp(timestamp_str):
            try:
                if isinstance(timestamp_str, (int, float)):
                    return pd.to_datetime(timestamp_str, unit='s')
                elif isinstance(timestamp_str, str):
                    timestamp_str = timestamp_str.split('+')[0].strip()
                    return pd.to_datetime(timestamp_str)
                else:
                    return pd.to_datetime(timestamp_str)
            except Exception as e:
                st.warning(f"Error al parsear timestamp {timestamp_str}: {str(e)}")
                return None

        # Convertir fechas de inicio y fin
        if 'start_date' in results:
            results['start_date'] = safe_parse_timestamp(results['start_date'])
        if 'end_date' in results:
            results['end_date'] = safe_parse_timestamp(results['end_date'])

        # 1. Mostrar información del backtest
        st.info(f"""
        **Detalles del Backtest:**
        - Par: {results['symbol']}
        - Período: {results['start_date'].strftime('%Y-%m-%d %H:%M')} a {results['end_date'].strftime('%Y-%m-%d %H:%M')}
        - Timeframes: {', '.join(results['timeframes'])}
        """)

        # 2. Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Retorno Total", f"{results['total_return']:.2f}%")
        with col2:
            st.metric("Win Rate", f"{results['win_rate']:.2f}%")
        with col3:
            st.metric("Factor de Beneficio", f"{results['profit_factor']:.2f}")
        with col4:
            st.metric("Máximo Drawdown", f"{results['max_drawdown']:.2f}%")

        # 3. Gráfica de evolución del capital
        st.subheader("📈 Evolución del Capital")
        if 'balance_history' in results and results['balance_history']:
            # Convertir el historial de balance a DataFrame
            balance_data = []
            for timestamp_str, balance in results['balance_history'].items():
                try:
                    timestamp = safe_parse_timestamp(timestamp_str)
                    if timestamp is not None:
                        balance_data.append({
                            'timestamp': timestamp,
                            'balance': float(balance)
                        })
                except Exception as e:
                    st.warning(f"Error al procesar timestamp del balance: {str(e)}")
                    continue
            
            # Crear DataFrame y ordenar por timestamp
            balance_df = pd.DataFrame(balance_data)
            if not balance_df.empty:
                balance_df.set_index('timestamp', inplace=True)
                balance_df.sort_index(inplace=True)
                
                # Gráfica de evolución del capital
                fig = make_subplots(rows=2, cols=1, 
                                  shared_xaxes=True,
                                  vertical_spacing=0.05,
                                  row_heights=[0.7, 0.3])

                # Gráfica de balance
                fig.add_trace(
                    go.Scatter(
                        x=balance_df.index,
                        y=balance_df['balance'],
                        name='Capital',
                        line=dict(color='blue'),
                        fill='tozeroy'
                    ),
                    row=1, col=1
                )

                # Línea de capital inicial
                fig.add_hline(
                    y=results['initial_capital'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Capital Inicial",
                    row=1, col=1
                )

                # Procesar drawdown
                if 'drawdown' in results:
                    try:
                        drawdown_data = []
                        for timestamp_str, dd_value in results['drawdown'].items():
                            try:
                                timestamp = safe_parse_timestamp(timestamp_str)
                                if timestamp is not None:
                                    if isinstance(dd_value, dict):
                                        dd_value = dd_value.get('drawdown', 0)
                                    
                                    drawdown_data.append({
                                        'timestamp': timestamp,
                                        'drawdown': float(dd_value)
                                    })
                            except Exception as e:
                                st.warning(f"Error al procesar timestamp del drawdown: {str(e)}")
                                continue
                        
                        # Crear DataFrame de drawdown y ordenar
                        dd_df = pd.DataFrame(drawdown_data)
                        if not dd_df.empty:
                            dd_df.set_index('timestamp', inplace=True)
                            dd_df.sort_index(inplace=True)
                            
                            # Agregar gráfica de drawdown
                            fig.add_trace(
                                go.Scatter(
                                    x=dd_df.index,
                                    y=dd_df['drawdown'],
                                    name='Drawdown',
                                    fill='tozeroy',
                                    line=dict(color='red')
                                ),
                                row=2, col=1
                            )

                    except Exception as e:
                        st.error(f"Error al procesar drawdown: {str(e)}")

                # Actualizar layout
                fig.update_layout(
                    height=600,
                    title_text="Evolución del Capital y Drawdown",
                    showlegend=True,
                    xaxis2_title="Fecha",
                    yaxis_title="Capital ($)",
                    yaxis2_title="Drawdown (%)",
                    yaxis=dict(
                        tickformat='$,.2f',
                        range=[
                            min(balance_df['balance']) * 0.95,
                            max(balance_df['balance']) * 1.05
                        ]
                    ),
                    yaxis2=dict(
                        tickformat='.2%',
                        range=[
                            min(dd_df['drawdown'] if 'dd_df' in locals() and not dd_df.empty else [0]) * 1.5,
                            0
                        ]
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos válidos de evolución del capital")
        else:
            st.warning("No hay datos de evolución del capital disponibles")

        # 4. Gráfico de análisis técnico
        st.subheader("📈 Análisis Técnico")
        if 'price_data' in results:
            try:
                # Convertir price_data a DataFrame
                price_data_list = []
                for timestamp_str, data in results['price_data'].items():
                    timestamp = safe_parse_timestamp(timestamp_str)
                    if timestamp is not None:
                        data['timestamp'] = timestamp
                        price_data_list.append(data)
                
                price_df = pd.DataFrame(price_data_list)
                if not price_df.empty:
                    price_df.set_index('timestamp', inplace=True)
                    price_df.sort_index(inplace=True)

                    # Crear gráfico con subplots
                    fig = make_subplots(rows=2, cols=1, 
                                      shared_xaxes=True,
                                      vertical_spacing=0.05,
                                      row_heights=[0.7, 0.3])

                    # Gráfico de precio
                    fig.add_trace(
                        go.Candlestick(
                            x=price_df.index,
                            open=price_df['open'],
                            high=price_df['high'],
                            low=price_df['low'],
                            close=price_df['close'],
                            name="Precio"
                        ),
                        row=1, col=1
                    )

                    # Procesar trades para visualización
                    long_entries = []
                    short_entries = []
                    exits = []

                    for trade in results['trades']:
                        entry_time = pd.to_datetime(trade['entry_time'])
                        exit_time = pd.to_datetime(trade['exit_time'])
                        
                        if trade['type'] == 'long':
                            long_entries.append({
                                'time': entry_time,
                                'price': trade['entry_price'],
                                'stop_loss': trade.get('stop_loss_price'),
                                'take_profit': trade.get('take_profit_price')
                            })
                        else:
                            short_entries.append({
                                'time': entry_time,
                                'price': trade['entry_price'],
                                'stop_loss': trade.get('stop_loss_price'),
                                'take_profit': trade.get('take_profit_price')
                            })
                        
                        exits.append({
                            'time': exit_time,
                            'price': trade['exit_price']
                        })

                    # Agregar entradas long
                    if long_entries:
                        fig.add_trace(
                            go.Scatter(
                                x=[e['time'] for e in long_entries],
                                y=[e['price'] for e in long_entries],
                                mode='markers+text',
                                marker=dict(symbol='triangle-up', size=12, color='green'),
                                text=[f"${p['price']:,.2f}" for p in long_entries],
                                textposition='top center',
                                name='Long Entry',
                                showlegend=True
                            ),
                            row=1, col=1
                        )

                        # Agregar stop loss y take profit para longs
                        for entry in long_entries:
                            if entry.get('stop_loss'):
                                fig.add_shape(
                                    type="line",
                                    x0=entry['time'],
                                    x1=entry['time'] + pd.Timedelta(days=1),
                                    y0=entry['stop_loss'],
                                    y1=entry['stop_loss'],
                                    line=dict(color="red", width=1, dash="dash"),
                                    row=1, col=1
                                )
                            if entry.get('take_profit'):
                                fig.add_shape(
                                    type="line",
                                    x0=entry['time'],
                                    x1=entry['time'] + pd.Timedelta(days=1),
                                    y0=entry['take_profit'],
                                    y1=entry['take_profit'],
                                    line=dict(color="green", width=1, dash="dash"),
                                    row=1, col=1
                                )

                    # Agregar entradas short
                    if short_entries:
                        fig.add_trace(
                            go.Scatter(
                                x=[e['time'] for e in short_entries],
                                y=[e['price'] for e in short_entries],
                                mode='markers+text',
                                marker=dict(symbol='triangle-down', size=12, color='red'),
                                text=[f"${p['price']:,.2f}" for p in short_entries],
                                textposition='bottom center',
                                name='Short Entry',
                                showlegend=True
                            ),
                            row=1, col=1
                        )

                        # Agregar stop loss y take profit para shorts
                        for entry in short_entries:
                            if entry.get('stop_loss'):
                                fig.add_shape(
                                    type="line",
                                    x0=entry['time'],
                                    x1=entry['time'] + pd.Timedelta(days=1),
                                    y0=entry['stop_loss'],
                                    y1=entry['stop_loss'],
                                    line=dict(color="red", width=1, dash="dash"),
                                    row=1, col=1
                                )
                            if entry.get('take_profit'):
                                fig.add_shape(
                                    type="line",
                                    x0=entry['time'],
                                    x1=entry['time'] + pd.Timedelta(days=1),
                                    y0=entry['take_profit'],
                                    y1=entry['take_profit'],
                                    line=dict(color="green", width=1, dash="dash"),
                                    row=1, col=1
                                )

                    # Agregar salidas
                    if exits:
                        fig.add_trace(
                            go.Scatter(
                                x=[e['time'] for e in exits],
                                y=[e['price'] for e in exits],
                                mode='markers+text',
                                marker=dict(symbol='x', size=10, color='gray'),
                                text=[f"${e['price']:,.2f}" for e in exits],
                                textposition='bottom center',
                                name='Exit',
                                showlegend=True
                            ),
                            row=1, col=1
                        )

                    # MACD
                    if all(col in price_df.columns for col in ['MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9']):
                        fig.add_trace(
                            go.Scatter(
                                x=price_df.index,
                                y=price_df['MACD_12_26_9'],
                                name='MACD',
                                line=dict(color='blue')
                            ),
                            row=2, col=1
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=price_df.index,
                                y=price_df['MACDs_12_26_9'],
                                name='Signal',
                                line=dict(color='orange')
                            ),
                            row=2, col=1
                        )
                        fig.add_trace(
                            go.Bar(
                                x=price_df.index,
                                y=price_df['MACDh_12_26_9'],
                                name='Histogram',
                                marker_color=price_df['MACDh_12_26_9'].apply(
                                    lambda x: 'green' if x > 0 else 'red'
                                )
                            ),
                            row=2, col=1
                        )

                    # Actualizar layout
                    fig.update_layout(
                        height=800,
                        title_text="Análisis Técnico",
                        showlegend=True,
                        xaxis_rangeslider_visible=False,
                        yaxis=dict(title="Precio", tickformat='$,.2f'),
                        yaxis2=dict(title="MACD"),
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No hay datos válidos para el gráfico de análisis técnico")
            except Exception as e:
                st.error(f"Error al procesar price_data: {str(e)}")

        # 5. Tabla de trades
        st.subheader("📊 Registro de Operaciones")
        if results.get('trades'):
            trades_df = pd.DataFrame(results['trades'])
            trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
            trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
            trades_df['duration'] = trades_df['exit_time'] - trades_df['entry_time']
            
            # Formatear la tabla
            trades_df['pnl'] = trades_df['pnl'].round(2)
            trades_df['entry_price'] = trades_df['entry_price'].round(2)
            trades_df['exit_price'] = trades_df['exit_price'].round(2)
            
            # Agregar colores según P&L
            def color_pnl(val):
                color = 'green' if val > 0 else 'red'
                return f'color: {color}'
            
            styled_df = trades_df.style.applymap(color_pnl, subset=['pnl'])
            st.dataframe(styled_df)
        else:
            st.info("El backtesting no genero ninguna operacion en el periodo seleccionado.")

        # 6. Estadísticas adicionales
        st.subheader("📊 Estadísticas Detalladas")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Métricas de Trading**")
            st.write(f"- Número total de trades: {results['total_trades']}")
            st.write(f"- Trades ganadores: {results['winning_trades']}")
            st.write(f"- Trades perdedores: {results['losing_trades']}")
            st.write(f"- Ratio ganador/perdedor: {results['win_rate']:.2f}%")
            
        with col2:
            st.write("**Métricas de Capital**")
            st.write(f"- Capital inicial: ${results['initial_capital']:,.2f}")
            st.write(f"- Capital final: ${results['final_capital']:,.2f}")
            st.write(f"- Retorno total: {results['total_return']:.2f}%")
            st.write(f"- Máximo drawdown: {results['max_drawdown']:.2f}%")

    except Exception as e:
        st.error(f"Error al cargar los resultados: {e}")

