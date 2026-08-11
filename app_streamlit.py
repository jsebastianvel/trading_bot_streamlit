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
from i18n import t

# Cargar variables de entorno
load_dotenv()

# En Streamlit Community Cloud los secretos configurados en el dashboard
# llegan via st.secrets, no como variables de entorno reales. Los copiamos
# a os.environ para que los modulos de genai/ (que leen os.environ
# directamente) los vean igual que en desarrollo local con .env.
for _key in ("GEMINI_API_KEY", "BINANCE_API_KEY", "BINANCE_API_SECRET", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
    if not os.environ.get(_key):
        try:
            _val = st.secrets.get(_key)
        except Exception:
            _val = None
        if _val:
            os.environ[_key] = _val

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

# Idioma de la interfaz (persistido en la sesión)
if "lang" not in st.session_state:
    st.session_state.lang = "en"

_lang_options = {"Español": "es", "English": "en"}
_lang_labels = list(_lang_options.keys())
_current_label = "Español" if st.session_state.lang == "es" else "English"
_selected_label = st.radio(
    t("lang_selector_label", st.session_state.lang),
    _lang_labels,
    index=_lang_labels.index(_current_label),
    horizontal=True,
    label_visibility="collapsed",
)
st.session_state.lang = _lang_options[_selected_label]
lang = st.session_state.lang

# Selector de seccion (radio en vez de st.tabs porque necesitamos saber
# desde Python cual esta activa, para mostrar el sidebar correcto)
NAV_KEYS = ["backtesting", "live_trading", "ai_agent"]
NAV_LABELS = [t(f"nav_{k}", lang) for k in NAV_KEYS]
_selected_nav_label = st.radio(
    t("nav_label", lang), NAV_LABELS, horizontal=True, label_visibility="collapsed"
)
selected_view = NAV_KEYS[NAV_LABELS.index(_selected_nav_label)]
st.markdown("---")

# Inicializar el estado de la sesión para el trader en vivo si no existe
if 'live_trader' not in st.session_state:
    st.session_state.live_trader = None
    st.session_state.is_trading = False

if selected_view == "live_trading":
    st.title(t("live_title", lang))
    st.info(t("live_disclaimer", lang))

    # Sección de configuración
    with st.sidebar:
        st.header(t("live_sidebar_header", lang))

        # Selección de exchange y par
        exchange = st.selectbox(
            t("live_exchange_label", lang),
            ["Binance"],
            index=0
        )

        symbol = st.selectbox(
            t("live_pair_label", lang),
            ["BTC/USDT", "ETH/USDT"],
            index=0
        )

        # Configuración de API (oculta)
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_API_SECRET', '')

        if not api_key or not api_secret:
            st.error(t("live_no_credentials", lang))

    if api_key and api_secret:
        # Estado del bot y controles
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.session_state.live_trader is None:
                if st.button(t("live_start_bot", lang)):
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
                        st.success(t("live_bot_started", lang))
                        st.rerun()
                    except Exception as e:
                        st.error(t("live_start_error", lang, error=str(e)))
            else:
                if st.button(t("live_stop_bot", lang)):
                    try:
                        st.session_state.live_trader.stop()
                        st.session_state.live_trader = None
                        st.session_state.is_trading = False
                        st.success(t("live_bot_stopped", lang))
                        st.rerun()
                    except Exception as e:
                        st.error(t("live_stop_error", lang, error=str(e)))

        with col2:
            if st.session_state.live_trader is not None:
                if not st.session_state.is_trading:
                    if st.button(t("live_enable_trading", lang)):
                        st.session_state.live_trader.enable_trading()
                        st.session_state.is_trading = True
                        st.success(t("live_trading_enabled", lang))
                        st.rerun()
                else:
                    if st.button(t("live_disable_trading", lang)):
                        st.session_state.live_trader.disable_trading()
                        st.session_state.is_trading = False
                        st.success(t("live_trading_disabled", lang))
                        st.rerun()

        with col3:
            # Estado actual
            if st.session_state.live_trader is not None:
                st.metric(
                    t("live_bot_status", lang),
                    t("live_status_active", lang) if st.session_state.live_trader.is_running else t("live_status_stopped", lang)
                )
                st.metric(
                    t("live_auto_trading", lang),
                    t("live_auto_enabled", lang) if st.session_state.is_trading else t("live_auto_disabled", lang)
                )
            else:
                st.metric(t("live_bot_status", lang), t("live_status_stopped", lang))
                st.metric(t("live_auto_trading", lang), t("live_auto_disabled", lang))

        # Información y advertencias
        st.info(t("live_info_block", lang))

        st.warning(t("live_warning_block", lang))



if selected_view == "ai_agent":
    st.title(t("agent_title", lang))
    st.markdown(t("agent_description", lang))

    if st.button(t("agent_generate_button", lang), type="primary"):
        with st.spinner(t("agent_spinner", lang)):
            try:
                from genai.agent import generate_market_brief
                st.session_state.agent_brief = generate_market_brief(lang=lang)
                st.session_state.agent_error = None
            except Exception as e:
                st.session_state.agent_error = str(e)

    if st.session_state.get("agent_error"):
        st.error(t("agent_error", lang, error=st.session_state.agent_error))

    if st.session_state.get("agent_brief"):
        brief = st.session_state.agent_brief

        decision_icon = {"LONG": "🟢", "SHORT": "🔴", "WAIT": "🟡"}.get(brief["decision"], "")
        st.metric(t("agent_recommendation", lang), f"{decision_icon} {brief['decision']}")

        col1, col2 = st.columns(2)
        col1.metric(t("agent_buy_weight", lang), f"{brief['peso_buy']:.2f}")
        col2.metric(t("agent_sell_weight", lang), f"{brief['peso_sell']:.2f}")

        st.subheader(t("agent_brief_subheader", lang))
        st.write(brief["explanation"])

        with st.expander(t("agent_signals_expander", lang)):
            for s in brief["signals"]:
                st.text(s)

        with st.expander(t("agent_news_expander", lang, count=len(brief['news']))):
            for n in brief["news"]:
                st.markdown(f"- **[{n['source']}]** [{n['title']}]({n['link']})")

if selected_view == "backtesting":
    st.title(t("bt_title", lang))

    # Sidebar para configuración
    with st.sidebar:
        st.header(t("bt_sidebar_header", lang))

        # Parámetros de backtesting
        symbol = st.selectbox(
            t("bt_pair_label", lang),
            ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT"],
            index=0
        )

        # Selección de fechas
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                t("bt_start_date", lang),
                value=datetime.now().date() - timedelta(days=365),  # Un año por defecto
                max_value=datetime.now().date()
            )

        with col2:
            end_date = st.date_input(
                t("bt_end_date", lang),
                value=datetime.now().date(),
                max_value=datetime.now().date()
            )

        # Validar que la fecha inicial sea anterior a la final
        if start_date >= end_date:
            st.error(t("bt_date_order_error", lang))
            st.stop()

        # Selección de temporalidad (una sola opción)
        selected_timeframe = st.selectbox(
            t("bt_timeframe_label", lang),
            list(TIMEFRAMES.keys()),
            index=None,
            help=t("bt_timeframe_help", lang)
        )

        initial_capital = st.number_input(
            t("bt_capital_label", lang),
            min_value=100,
            max_value=100000,
            value=1000,
            step=100
        )

        # Botón para ejecutar backtesting
        run_backtest_button = st.button(t("bt_run_button", lang))

    if run_backtest_button:
        if not selected_timeframe:
            st.error(t("bt_timeframe_required", lang))
        else:
            with st.spinner(t("bt_running_spinner", lang)):
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())

                results = run_backtest(
                    symbol=symbol,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    initial_capital=initial_capital,
                    timeframes=[selected_timeframe]  # Lista con un solo elemento
                )
                st.success(t("bt_completed", lang))
                st.session_state.last_run = datetime.now()
                st.session_state.show_results = True
                st.rerun()

    # Solo mostrar resultados si se ha ejecutado un backtesting
    if not hasattr(st.session_state, 'show_results'):
        st.session_state.show_results = False

    if not st.session_state.show_results:
        st.info(t("bt_configure_hint", lang))
        st.stop()

    # Cargar resultados de backtesting
    results_dir = os.path.join(os.environ.get('TEMP', '/tmp'), "trading_bot_results")

    # Buscar archivos en el directorio de resultados
    result_files = []
    if os.path.exists(results_dir):
        result_files.extend(glob.glob(os.path.join(results_dir, "*.json")))

    if not result_files:
        st.warning(t("bt_no_results", lang))
        st.stop()

    # Ordenar archivos por fecha de modificación (más reciente primero)
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Usar el archivo más reciente automáticamente
    selected_file = result_files[0]

    try:
        with open(selected_file, 'r') as f:
            results = json.load(f)

        if not results:
            st.error(t("bt_empty_file", lang))
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
                st.warning(t("bt_timestamp_parse_warning", lang, timestamp=timestamp_str, error=str(e)))
                return None

        # Convertir fechas de inicio y fin
        if 'start_date' in results:
            results['start_date'] = safe_parse_timestamp(results['start_date'])
        if 'end_date' in results:
            results['end_date'] = safe_parse_timestamp(results['end_date'])

        # 1. Mostrar información del backtest
        st.info(t(
            "bt_details_block", lang,
            symbol=results['symbol'],
            start=results['start_date'].strftime('%Y-%m-%d %H:%M'),
            end=results['end_date'].strftime('%Y-%m-%d %H:%M'),
            timeframes=', '.join(results['timeframes']),
        ))

        # 2. Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("bt_metric_total_return", lang), f"{results['total_return']:.2f}%")
        with col2:
            st.metric(t("bt_metric_win_rate", lang), f"{results['win_rate']:.2f}%")
        with col3:
            st.metric(t("bt_metric_profit_factor", lang), f"{results['profit_factor']:.2f}")
        with col4:
            st.metric(t("bt_metric_max_drawdown", lang), f"{results['max_drawdown']:.2f}%")

        # 3. Gráfica de evolución del capital
        st.subheader(t("bt_capital_evolution_subheader", lang))
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
                    st.warning(t("bt_balance_timestamp_warning", lang, error=str(e)))
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
                        name=t("bt_capital_trace_name", lang),
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
                    annotation_text=t("bt_initial_capital_annotation", lang),
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
                                st.warning(t("bt_drawdown_timestamp_warning", lang, error=str(e)))
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
                                    name=t("bt_drawdown_trace_name", lang),
                                    fill='tozeroy',
                                    line=dict(color='red')
                                ),
                                row=2, col=1
                            )

                    except Exception as e:
                        st.error(t("bt_drawdown_process_error", lang, error=str(e)))

                # Actualizar layout
                fig.update_layout(
                    height=600,
                    title_text=t("bt_capital_chart_title", lang),
                    showlegend=True,
                    xaxis2_title=t("bt_date_axis", lang),
                    yaxis_title=t("bt_capital_axis", lang),
                    yaxis2_title=t("bt_drawdown_axis", lang),
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
                st.warning(t("bt_no_valid_capital_data", lang))
        else:
            st.warning(t("bt_no_capital_data", lang))

        # 4. Gráfico de análisis técnico
        st.subheader(t("bt_technical_analysis_subheader", lang))
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
                            name=t("bt_price_trace_name", lang)
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
                        title_text=t("bt_technical_chart_title", lang),
                        showlegend=True,
                        xaxis_rangeslider_visible=False,
                        yaxis=dict(title=t("bt_price_axis", lang), tickformat='$,.2f'),
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
                    st.warning(t("bt_no_valid_technical_data", lang))
            except Exception as e:
                st.error(t("bt_price_data_error", lang, error=str(e)))

        # 5. Tabla de trades
        st.subheader(t("bt_trades_subheader", lang))
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

            styled_df = trades_df.style.map(color_pnl, subset=['pnl'])
            st.dataframe(styled_df)
        else:
            st.info(t("bt_no_trades", lang))

        # 6. Estadísticas adicionales
        st.subheader(t("bt_stats_subheader", lang))
        col1, col2 = st.columns(2)

        with col1:
            st.write(t("bt_trading_metrics_header", lang))
            st.write(t("bt_total_trades", lang, value=results['total_trades']))
            st.write(t("bt_winning_trades", lang, value=results['winning_trades']))
            st.write(t("bt_losing_trades", lang, value=results['losing_trades']))
            st.write(t("bt_win_loss_ratio", lang, value=results['win_rate']))

        with col2:
            st.write(t("bt_capital_metrics_header", lang))
            st.write(t("bt_initial_capital_line", lang, value=results['initial_capital']))
            st.write(t("bt_final_capital_line", lang, value=results['final_capital']))
            st.write(t("bt_total_return_line", lang, value=results['total_return']))
            st.write(t("bt_max_drawdown_line", lang, value=results['max_drawdown']))

    except Exception as e:
        st.error(t("bt_load_error", lang, error=str(e)))
